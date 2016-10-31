"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

from wordlist import w

# Entity which stores the users.
class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()

# Entity which stores the games.
class Game(ndb.Model):
    """Game object"""
    #secret word which one needs to reveal.
    target = ndb.StringProperty(required=True)
    #Number of attempts which one may make to guess the secret word.
    attempts_allowed = ndb.IntegerProperty(required=True)
    # Number of attempts to guess the secret word.
    attempts_remaining = ndb.IntegerProperty(required=True)
    # State of game (running / over).
    game_over = ndb.BooleanProperty(required=True, default=False)
    # Key to user who initiated the game.
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        # Retrieve the secret word randomly from list.
        _secretWord = random.choice(w)
        # Compute the number of attemps one have to guess the word.
        _attempts = len(_secretWord) +5

        game = Game(user=user,
                    target=_secretWord,
                    attempts_allowed=_attempts,
                    attempts_remaining=_attempts ,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message, matchresult, guessedletters):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        form.matchresult = matchresult
        form.guessedletters = guessedletters
        return form

    def to_delete_confirmation_form(self, message):
        """Returns confirmation in case a game has been succsessfully been
        deleted"""
        form = CancelGameConfirmationForm()
        form.urlsafe_key = self.key.urlsafe()
        form.message = message
        return form

    # Sets if game is won or lost after it is finished and writes score.
    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        # Write Score.
        score.put()

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4)
    user_name = messages.StringField(5, required=True)
    matchresult = messages.StringField(6)
    guessedletters = messages.StringField(7)

class GamesForm(messages.Message):
    """Returns a list of all games"""
    items = messages.MessageField(GameForm,1, repeated=True)
    message = messages.StringField(2)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    
# CANCEL Game
# cancel_game
class CancelGameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)

class CancelGameConfirmationForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    message = messages.StringField(2)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class Move(ndb.Model):
    game = ndb.KeyProperty(required=True, kind='Game')
    move_no = ndb.IntegerProperty(required=True)
    guess = ndb.StringProperty(required=True)
    matchresult = ndb.StringProperty(required=True)

    def to_form(self, message):
        form = MoveForm()

        form.urlsafe_key = self.key.urlsafe(),
        form.move_no=self.move_no,
        form.guess=self.guess,
        form.matchresult=self.matchresult,
        form.movesleft = self.movesleft

        return form

    def to_form_hist(self):
        form = MoveFormHist()
        form.move_no = self.move_no
        form.guess = self.guess
        form.matchresult = self.matchresult
        return form

class MoveFormHist(messages.Message):

    move_no = messages.IntegerField(2)
    guess = messages.StringField(3)
    matchresult = messages.StringField(4)
    movesleft = messages.IntegerField(5)

class MoveForm(messages.Message):
    #urlsafe_key = messages.StringField(1, required=True)
    move_no = messages.IntegerField(2)
    guess = messages.StringField(3)
    matchresult = messages.StringField(4)
    movesleft = messages.IntegerField(5)

class GameHistoryForm(messages.Message):
    items = messages.MessageField(MoveFormHist,1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

# Stores high scores
class Ranking(ndb.Model):
    """User Ranking"""
    player_name = ndb.StringProperty(required=True)
    player_ranking = ndb.IntegerProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')

    def to_form(self):
        return RankingForm(player_name = self.player_name, player_ranking = self.player_ranking)

class RankingForm(messages.Message):
    player_name = messages.StringField(1)
    player_ranking = messages.IntegerField(2)

class RankingsForm(messages.Message):
    items = messages.MessageField(RankingForm,1, repeated=True)
