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
from google.appengine.ext import ndb

from models import User, Game, Score, Move, Ranking

from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, MoveForm, GamesForm, CancelGameConfirmationForm,\
    RankingsForm, RankingForm, GameHistoryForm
from utils import get_by_urlsafe, check_if_guessed_before, matchresult,\
    guessedletters, compute_ranking

GET_GAME_H = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

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

GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))

GET_HIGH_SCORE = endpoints.ResourceContainer(
    limit=messages.IntegerField(1),)

CANCEL_GAME = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)


MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

_allowedLetters = 'abcdefghijklmnopqrstuvwxyz'


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
        return game.to_form('Good luck playing Hangman!', None, None)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        _game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if _game:
            return _game.to_form('Time to make a move!', None, None)
        else:
            raise endpoints.NotFoundException('Game not found!')
# MAKE_MOVE_REQUEST

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        _game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # Check if game is not over, if so return information.
        if _game.game_over:
            return _game.to_form('Game already over!', None, None)
        # Validates input.
        # First check for empty field.
        if request.guess == '':
            return _game.to_form('guess was empty!', None, None)
        # Second check for not allowed letters.
        elif request.guess not in _allowedLetters:
            return _game.to_form("%s is not allowed" % request.guess, None, None)
        # Third check if letter has been guessed before.
        elif check_if_guessed_before(request.guess, _game.key) == 'NOK':
            return _game.to_form("%s has been guessed before" % request.guess,
                                 None, guessedletters(request))
        # In case input is ok..
        else:
            # compute the result string after guess, e.g. ***h****
            _matchresult = matchresult(_game.target, request)
            # Querry for moves already made in this game to compute remaining
            # moves and move number.
            _noMoves = Move.query(Move.game == _game.key)
            # Initiate List of move Numbers and number of current move.
            _nextNoList = ""
            _nextNo = '0'
            # Check if this is the first move of a new game.
            if _noMoves.get() is None:
                _nextNo = 0
            # If this is not the first move of a new game, compute move number.
            else:

                for n in _noMoves:
                    _nextNoList += str(n.move_no)

                _nextNo = int(max(list(_nextNoList))) + 1
        # Create new Bigtable move entity
        _move = Move(
            game=_game.key,
            move_no=_nextNo,
            guess=request.guess,
            matchresult=_matchresult
        )
        # write move to Bigtable
        _move.put()

        _moves = Move.query(Move.game == _game.key)

        _game.attempts_remaining -= 1

        if _matchresult == _game.target:
            _game.end_game(True)
            compute_ranking(_game.user)
            return _game.to_form('You win!', _matchresult,
                                 guessedletters(request))

        if request.guess in _game.target:
            msg = 'You found a new letter.'
        else:
            msg = 'Guessed letter is not part of the secret word.'

        if _game.attempts_remaining < 1:
            _game.end_game(False)
            compute_ranking(_game.user)
            return _game.to_form(msg + ' Game over!', _matchresult,
                                 guessedletters(request))
        else:
            _game.put()
            return _game.to_form(msg, _matchresult, guessedletters(request))

    @endpoints.method(request_message=GET_HIGH_SCORE,
                      response_message=ScoreForms,
                      path='scores',
                      name='get_high_scores',
                      http_method='GET')
# HIGH SCORE
    def get_scores(self, request):
        """Return a high score"""
        # Returns a list of games odered by number of guesses (lower is better)
        return ScoreForms(items=[score.to_form() for score \
        in Score.query().order(Score.guesses).fetch(request.limit)])

# GET USER GAMES
    @endpoints.method(request_message=GET_USER_GAMES_REQUEST,
                      response_message=GamesForm,
                      path='usergames',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):

        _curuser = User.query(User.name == request.user_name)
        _curuseres = _curuser.get()

        if _curuseres is None:
            a = GamesForm(message='User does not exist!')
            return a

        _games = Game.query(Game.user == _curuseres.key)

        return GamesForm(items=[g.to_form(None, None, None) for g in _games])

# CANCEL Game
# cancel_game

    @endpoints.method(request_message=CANCEL_GAME,
                      response_message=CancelGameConfirmationForm,
                      path='game/delete/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):

        # Get game from Bigtable
        _game = get_by_urlsafe(request.urlsafe_game_key, Game)

        # Check if game was found by url_safe_gamekey
        if _game:
            # If so execute query.
            _gameover = _game.query().get()

            # Check if game is over.
            if _gameover and _gameover.game_over == True:
                # get moves of that game.
                _moves = Move.query(Move.game == _gameover.key).fetch()
                # Make a list of related move entities to delete.
                list_of_keys = ndb.put_multi(_moves)
                list_of_entities = ndb.get_multi(list_of_keys)
                # Delete the moves.
                ndb.delete_multi(list_of_keys)
                # Delete the game.
                _gameover.key.delete()
                # Return confirmation that game has been deleted
                return _gameover.to_delete_confirmation_form('Game deleted!')

            # In case game is not over go here.
            elif _gameover and _gameover.game_over == False:
                # Tell the user that a not ended game can not be deleted.
                return _gameover.to_delete_confirmation_form(
                    'Cant delete Game which is not over!')

        # If game was not found raise an error.
        else:
            raise endpoints.NotFoundException('Game not found!')

# GET_USER_SCORES
# get_user_scores

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
            average = float(total_attempts_remaining) / count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))
# GET USER RANKINGS

    @endpoints.method(response_message=RankingsForm,
                      path='ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return the current game state."""
        _rankings = Ranking.query().order(-Ranking.player_ranking).fetch()
        if _rankings:
            return RankingsForm(items=[rank.to_form() for rank in _rankings])
        else:
            raise endpoints.NotFoundException('Ranking not found')

# get_game_history

    @endpoints.method(request_message=GET_GAME_H,
                      response_message=GameHistoryForm,
                      path='gamehistory/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):

        _game = get_by_urlsafe(request.urlsafe_game_key, Game)

        _moves = Move.query(Move.game == _game.key,
                            ).order(Move.move_no).fetch()

        return GameHistoryForm(items=[m.to_form_hist() for m in _moves])


api = endpoints.api_server([HangmanApi])
