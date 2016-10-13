# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score, Move
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, MoveForm
from utils import get_by_urlsafe, check_if_guessed_before, matchresult


NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

GET_MOVE_REQUEST = endpoints.ResourceContainer(MoveForm,
    urlsafe_game_key=messages.StringField(1),)


MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

_allowedLetters='abcdefghijklmnopqrstuvwxyz'

@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        
        game = Game.new_game(user.key)
        

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Guess a Number!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        _game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if _game:
            return _game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        _game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if _game.game_over:
            return _game.to_form('Game already over!')

        if request.guess == '':
            return _game.to_form('guess was empty!')
        elif request.guess not in _allowedLetters:
            return _game.to_form("%s is not allowed" %request.guess)
        elif check_if_guessed_before(request.guess,_game.key) == 'NOK':
            return _game.to_form("%s has been guessed before" %request.guess)
        else:
            _matchresult = matchresult(_game.target, _game.key, request.guess)
#Hier gehts weiter
            _noMoves = Move.query(Move.game == _game.key)

            _nextNoList = ""
            _nextNo = '0'

            if _noMoves is None:
                print('NONE BAZINGA')
                _nextNo = '0'
            else:

                for n in _noMoves:
                    print('BAZINGA')
                    _nextNoList += str(n.no)

                _nextNo = int(max(list(_nextNoList))) + 1
                print('Yo NO!!!!!')
                print(_nextNo)


            

        _move = Move(
            game = _game.key,
            no = _nextNo,
            guess = request.guess,
            matchresult = _matchresult
        )
        print('put da move yo!')
        _move.put()

        _moves = Move.query(Move.game == _game.key)

        _game.attempts_remaining -= 1


        if _matchresult == _game.target:
            _game.end_game(True)
            return _game.to_form('You win!')

        if request.guess in _game.target:
            msg = 'you found a new letter.'
        else:
            msg = 'guessed letter is not part of the secret word.'

        if _game.attempts_remaining < 1:
            _game.end_game(False)
            return _game.to_form(msg + ' Game over!')
        else:
            _game.put()
            return _game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))
# Own Code Start
    @endpoints.method(request_message=GET_MOVE_REQUEST,
                      response_message=MoveForm,
                      path='move/{urlsafe_game_key}',
                      name='get_move',
                      http_method='GET')
    def get_move(self, request):
        """Return the current game state."""
        move = get_by_urlsafe(request.urlsafe_game_key, Move)
        if move:
            return move.to_form('What a smart move!')
        else:
            raise endpoints.NotFoundException('Move not found!')
# Own Code End

api = endpoints.api_server([HangmanApi])
