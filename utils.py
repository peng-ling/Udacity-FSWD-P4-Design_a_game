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

# Checks if letter has been guessed befor.
def check_if_guessed_before(guess, urlsafe):
    # Get all moves of a game to get guessed letters.
    _moves = Move.query(Move.game == urlsafe).get()

    # Check if this is the first move and Return ok (letter has not been
    # guessed before)
    if not _moves:
        return "OK"
    # Itterate over all guessed letters and...
    for g in _moves.guess:
        # if has been guessed before return "NOK"
        # (letter has been guesed before).
        if g == guess:
            return "NOK"
        # Letter has not been guessed before.
        else:
            return "OK"

# Returns string which shows letters which are in the secret, e.g. **k****
def matchresult(secret, request):

    _match = ""
    _guessedLetters = ""

    # as lenght of secret is variable prepare a *** string of correct lenght.
    for s in range(0, len(secret)):
        _match += '*'
        _matchlist = list(_match)

    # Get all letters which have been guessed so far.
    _guessedLetters = guessedletters(request)
    # Itterate over guessedletters and if one of the matches with secret..
    for letter in _guessedLetters:
        # replace * by guessed letter.
        for idx, secretletter in enumerate(secret):
            if letter == secretletter:
                _matchlist[idx] = letter
    # Return matchresult as a string.
    return "".join(_matchlist)

# Returns all guessed letters for a game.
def guessedletters(request):
    _guessedLetters = ""

    # get current game.
    _game = get_by_urlsafe(request.urlsafe_game_key, Game)

    # query moves of current game
    _moves = Move.query(Move.game == _game.key).fetch()

    # Check if a move has been made already.
    if _moves is not None:
        # For every move get the guessed letter and concatenate them.
        for g in _moves:
            _guessedLetters += str(g.guess)
        # As matchresult gets computed before the first move
        # is put() add the guessed letter from request here.
        _guessedLetters += request.guess
        # make guessed letters distinct, as otherwise guessed letters will
        # duplicate.
        _guessedLettersdist = ''.join(set(_guessedLetters))
    # In case no move has been made for current game go here.
    else:
        _guessedLettersdist += request.guess
    # Return all so far guessed letters.
    return _guessedLettersdist

# Computes the actuall ranking of a given user und stores it in / updates
# Ranking
def compute_ranking(user_key):

    _gamecount = 0
    _score = 0
    _rank = 0

    # Fetch all games of one user
    _usergames = Game.query(Game.game_over == True,
                            Game.user == user_key).fetch()

    # Itterate over all games of one user and...
    for ug in _usergames:
        #..count the games he played.
        _gamecount += 1
        #..compute and sum up the score of each game.
        _score += (ug.attempts_allowed -
                   (ug.attempts_allowed - ug.attempts_remaining))

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
        _ranking = Ranking(player_name=_user.name,
                           player_ranking=_rank, user=user_key)
        _ranking.put()
