
class game:

    def __init__(self):
        self.secret = "pizza"
        self.guessedLetters = ""

    def guess(self, letter):
        self.guessedLetters += letter
        return self.guessedLetters

    def matchresult(self):
        match = ""
        for letter in self.guessedLetters:
            for secretletter in self.secret:
                if letter == secretletter:
                    match += letter
                else:
                    match += '*'
        return match

    def validateGuess(self,letter):
        isguessvalid = ""
        if letter == "":
            isguessvalid = "guessed letter was empty"
        elif letter in self.guessedLetters:
                isguessvalid = "%S has been guessed before" %letter
        else
            isguessvalid = "Bingo"
        return isguessvalid





schakka = game()

schakka.guess("a")
print (schakka.guessedLetters)
print (schakka.matchresult())
schakka.guess("b")

print (schakka.validateGuess(''))
print (schakka.validateGuess('b'))

print (schakka.guessedLetters)
print (schakka.matchresult())
