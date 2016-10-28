# -*- coding: utf-8 -*-

from wordlist import w
import random

class game:

    def __init__(self):
        self.secret = random.choice(w)
        self.guessedLetters=''
        self.allowedletters='abcdefghijklmnopqrstuvwxyz'
        self.maxnumberguesses = len(self.secret)

    def guess(self, letter):

        self.guessedLetters += letter
        return self.guessedLetters


    def matchresult(self):

        match = ""

        for s in range(0,len(self.secret)):
            match +='*'

        for letter in self.guessedLetters:
            for idx,secretletter in enumerate(self.secret):
                if letter == secretletter:
                    match[idx] = letter

        return "".join(match)


    def validateGuess(self,letter):

        isguessvalid = ""

        if letter == "":
            isguessvalid = "guessed letter was empty"
        elif letter in self.guessedLetters:
                isguessvalid = "%s has been guessed before" %letter
        elif letter not in self.allowedletters:
                isguessvalid = "%s is not allowed" %letter
        else:
            isguessvalid = "guessed letter is valid"

        return isguessvalid


    def turnsleft(self):

        tl = self.maxnumberguesses - len(self.guessedLetters)

        return tl

    def gamestate(self):

        if self.turnsleft() > 0:
            gs = 'running'
        elif self.turnsleft() == 0 and self.matchresult() == self.secret:
            gs ='won'
        else:
            gs = 'lost'

        return gs

# Comment
