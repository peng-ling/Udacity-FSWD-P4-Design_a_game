"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints
from models import User, Game, Score, Move


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


def matchresult(secret, urlsafe, actualguess):

    _match = ""

    _guessedLetters = ""

    _moves = Move.query(Move.game == urlsafe)

    for s in range(0,len(secret)):
        _match +='*'
        _matchlist = list(_match)

    if _moves is not None:
        for g in _moves:
            _guessedLetters += str(g.guess)
        _guessedLetters += actualguess
    else:
        _guessedLetters += actualguess
    for letter in _guessedLetters:
        for idx,secretletter in enumerate(secret):
            if letter == secretletter:
                _matchlist[idx] = letter
                    
    return "".join(_matchlist)
