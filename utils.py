"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints
from models import User, Game, Score, Move, Ranking


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()

    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')

    return entity


def check_if_guessed_before(guess, urlsafe):

    _moves = Move.query(Move.game == urlsafe).get()

    if not _moves:
        return "OK"

    for g in _moves.guess:

        if g == guess:
            return "NOK"
        else:
            return "OK"


def matchresult(secret, request):

    _match = ""

    _guessedLetters = ""

    for s in range(0,len(secret)):
        _match +='*'
        _matchlist = list(_match)

    _guessedLetters = guessedletters(request)
    for letter in _guessedLetters:
        for idx,secretletter in enumerate(secret):
            if letter == secretletter:
                _matchlist[idx] = letter
                    
    return "".join(_matchlist)

def guessedletters(request):
    _guessedLetters = ""

    _game = get_by_urlsafe(request.urlsafe_game_key, Game)

    _moves = Move.query(Move.game == _game.key)

    if _moves is not None:
        for g in _moves:
            _guessedLetters += str(g.guess)
        _guessedLetters += request.guess
    else:
        _guessedLetters += request.guess

    return _guessedLetters

# Computes the actuall ranking of a given user und stores it in / updates Ranking
def compute_ranking(user_key):

    _gamecount = 0
    _score = 0
    _rank = 0

    # Fetch all games of one user
    _usergames = Game.query(Game.game_over == True, Game.user == user_key).fetch()

    # Itterate over all games of one user and...
    for ug in _usergames:
        #..count the games he played.
        _gamecount += 1
        #..compute and sum up the score of each game.
        _score += (ug.attempts_allowed - (ug.attempts_allowed - ug.attempts_remaining))
    
    # Rank is the score divided by the number of games.
    _rank = _score / _gamecount

    # Check if user has an entry in Ranking already and..
    _already_ranked = Ranking.query(Ranking.user == user_key).get()

        #..if so update the new rank only.
    if _already_ranked:
        r = _already_ranked.key.get()
        r.player_ranking = _rank
        r.put()
        # .. otherwise generate a whole new Ranging entry.
    else:
        _user = User.query(User.key == user_key).get()
        print('Kacke mit EI!')
        print(_user)
        print(type(_user))
        _ranking = Ranking(player_name = _user.name, player_ranking = _rank , user = user_key)
        _ranking.put()

