#!/usr/bin/python

# NOTE:
# This is the code. If you are seeing this when you open the program normally, please follow the steps here:
# https://sites.google.com/site/evanspythonhub/having-problems

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO AREA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Program by: Evan
# PROGRAM made in 2012
# This program will play MasterMind and facilitate games of MasterMind.

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CONFIG AREA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Colors And Color Shortcuts:
colors = {"-":"blank", "b":"blue", "d":"black", "w":"white", "r":"red", "y":"yellow", "g":"green"}

# Automatically Display Guess Box?
doshow = True

# Default Length Of Secret:
numpegs = 4

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DATA AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from rabbit.all import *

def getscore(move, secret):
    score = []
    scored = []
    for x in move:
        if x in secret:
            numscored = 0
            for y in scored:
                if y == x:
                    numscored += 1
            numexist = 0
            for y in secret:
                if y == x:
                    numexist += 1
            if numscored < numexist:
                scored.append(x)
                score.append(0)
    for x in xrange(0, len(move)):
        if move[x] == secret[x]:
            score.remove(0)
            score.append(1)
    return sorted(score)

class mastermind(object):
    def __init__(self, colors):
        self.colors = colors
        self.gen = random()
    def choose(self, amount=4):
        """Chooses A New Secret."""
        self.secret = ""
        for x in xrange(0, amount):
            self.secret += self.gen.choose(self.colors)
    def score(self, move):
        """Scores A Move."""
        return getscore(move, self.secret)
    def guess(self, length, moves, guesses=None):
        """Guesses At A Secret."""
        done = 0
        while not done:
            self.choose(length)
            if guesses != None:
                while self.secret in guesses:
                    self.choose(length)
                guesses.append(self.secret)
            done = 1
            for x in moves:
                if self.score(x) != moves[x]:
                    done = 0
        return self.secret

class mindcalc(object):
    def __init__(self, colorlist):
        self.m = mastermind(colorlist)
    def calculate(self, length, times):
        num = 0
        for x in xrange(0, times):
            self.m.choose(length)
            secret = self.m.secret
            moves = {}
            if length < 4:
                guesses = []
            done = 0
            while not done:
                num += 1
                if length < 4:
                    guess = self.m.guess(length, moves, guesses)
                elif length < 5:
                    guess = self.m.guess(length, moves, [])
                else:
                    guess = self.m.guess(length, moves)
                moves[guess] = getscore(guess, secret)
                if moves[guess] == [1]*length:
                    done = 1
        return float(num)/float(times)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class main(base):
    def initialize(self, args):
        self.colors = args[0]
        self.doshow = args[1]
        self.numpegs = args[2]
        self.app.display("Score System:  0=A Correct Color In An Incorrect Place  1=A Correct Color In A Correct Place")
        displayer = "Colors:   "
        for x in self.colors:
            displayer += self.colors[x]+" ("+x+"),   "
        self.colorstring = displayer[:-4]
        self.app.display(self.colorstring)
        self.root.bind("<Control-s>", lambda event: self.box.main.insert("end", self.showinfo()))
        self.multi = isno(popup("Question", "Singleplayer(Y) or Multiplayer(n)?"))
        if self.multi:
            self.serv = isno(popup("Question", "Client(Y) or Server(n)?"))
            if not self.serv:
                self.host = popup("Entry", "Host?")
            self.port = popup("Integer", "Port?")
            if self.serv:
                self.app.display("Waiting For A Connection...")
            else:
                self.app.display("Connecting...")
            self.register(self.connect, 200)
        else:
            colorslist = []
            for x in colors:
                colorslist.append(x)
            self.mind = mastermind(colorslist)
            self.choosenew()
    def showinfo(self):
        displayer = self.colorstring+"\n\nGuesses And Scores:\n"
        for x in self.displayers:
            try:
                a,b=x
            except TypeError:
                displayer += x+"\n"
            else:
                displayer += a+" | "+b+"\n"
        displayer += "\nEntry Area:"
        out = popup("Entry", displayer)
        if out == None:
            self.root.destroy()
        return out
    def connect(self):
        if self.serv:
            self.mind = longserver(self.port)
            self.mind.start()
            self.turn = 1
        else:
            self.mind = client()
            if self.host == "":
                self.mind.connect(self.port)
            else:
                self.mind.connect(self.port, self.host)
            self.turn = 0
        self.app.display("Connected.")
        if self.turn:
            self.begin()
        else:
            self.app.display("Waiting For Other Player...")
            self.register(self.begin, 400)
    def begin(self):
        self.displayers = []
        if self.turn:
            done = 0
            while not done:
                done = 1
                self.app.display("Choose A Secret:")
                secret = superformat(delspace(self.get()))
                if "," in secret:
                    secret = secret.split(",")
                self.secret = ""
                for x in secret:
                    if x in self.colors:
                        self.secret += x
                    else:
                        try:
                            self.secret += flip(self.colors)[x]
                        except KeyError:
                            done = 0
                            self.app.display("Invalid Secret.")
                            break
            secretlist = []
            for x in self.secret:
                secretlist.append(self.colors[x])
            self.app.display("Your Secret:", strlist(secretlist, ", "))
            self.length = len(self.secret)
            self.mind.send(str(self.length))
            self.app.display("Waiting For Other Player...")
            self.register(self.hider, 400)
        else:
            self.length = int(self.mind.receive())
            self.app.display("The Other Player Chose A Secret of Length:", self.length)
            self.guesser()
    def guesser(self):
        done = 0
        while not done:
            done = 1
            self.app.display("Make A Guess:")
            if self.doshow:
                guess = superformat(delspace(self.showinfo()))
            else:
                guess = superformat(delspace(self.get()))
            if "," in guess:
                guess = guess.split(",")
            self.guess = ""
            for x in guess:
                if x in self.colors:
                    self.guess += x
                else:
                    try:
                        self.guess += flip(self.colors)[x]
                    except KeyError:
                        done = 0
                        self.app.display("Invalid Guess.")
                        break
            if done == 1 and len(self.guess) != self.length:
                self.app.display("Invalid Guess.")
                done = 0
        guesslist = []
        for x in self.guess:
            guesslist.append(self.colors[x])
        printable = strlist(guesslist, ", ")
        self.app.display("You Guessed:", printable)
        self.displayers.append(printable)
        self.app.display("Getting Score...")
        self.register(self.getscore, 200)
    def choosenew(self):
        self.displayers = []
        self.turn = isno(popup("Question", "Guess(Y) Or Hide(n)?"))
        if self.turn:
            self.beginattempt()
        else:
            self.length = 0
            while self.length <= 0:
                self.app.display("Length of Secret?")
                inputstring = delspace(self.get())
                if inputstring == "":
                    self.length = self.numpegs
                else:
                    self.length = int(getnum(inputstring))
                if self.length <= 0:
                    self.app.display("Invalid Length.")
            self.mind.choose(self.length)
            self.app.display("Using Length "+str(self.length)+".")
            self.guesser()
    def getscore(self):
        if self.multi:
            self.mind.send(self.guess)
            score = self.mind.receive()[1:]
        else:
            score = strlist(self.mind.score(self.guess), ", ")
        self.app.display("Score:", score)
        self.displayers.append((self.displayers.pop(),score))
        test = "1, "*self.length
        if score == test[:-2]:
            self.app.display("You Guessed Correctly! ("+str(len(self.displayers))+" Guesses)")
            if self.multi:
                self.turn = 1
                self.begin()
            else:
                self.choosenew()
        else:
            self.guesser()
    def hider(self):
        guess = self.mind.receive()
        score = strlist(getscore(guess, self.secret), ", ")
        self.mind.send("#"+score)
        guesslist = []
        for x in guess:
            guesslist.append(self.colors[x])
        displayer = strlist(guesslist, ", ")
        self.app.display("The Other Player Guessed:", displayer)
        self.app.display("Their Guess Got A Score Of:", score)
        self.displayers.append((displayer,score))
        test = "1, "*self.length
        if score == test[:-2]:
            self.app.display("The Other Player Guessed Correctly! ("+str(len(self.displayers))+" Guesses)")
            self.turn = 0
            self.app.display("Waiting For Other Player...")
            self.register(self.begin, 400)
        else:
            self.app.display("Waiting For Other Player...")
            self.register(self.hider, 400)
    def beginattempt(self):
        self.app.display("Choose A Secret.")
        self.length = 0
        while self.length <= 0:
            self.app.display("How Long Is Your Secret?")
            self.length = int(getnum(self.get()))
            if self.length <= 0:
                self.app.display("Invalid Length.")
        self.moves = {}
        if self.length < 4:
            self.guesses = []
        self.register(self.attempt, 200)
    def attempt(self):
        if self.length < 4:
            move = self.mind.guess(self.length, self.moves, self.guesses)
        elif self.length < 5:
            move = self.mind.guess(self.length, self.moves, [])
        else:
            move = self.mind.guess(self.length, self.moves)
        movelist = []
        for x in move:
            movelist.append(self.colors[x])
        displayer = strlist(movelist, ", ")
        self.app.display("The Computer Guesses:", displayer)
        self.displayers.append(displayer)
        done = 0
        while not done:
            done = 1
            self.app.display("What Is The Score?")
            score = superformat(delspace(self.get()))
            if "," in score:
                score = score.split(",")
            self.moves[move] = []
            for x in score:
                x = int(getnum(x))
                if x == 0 or x == 1:
                    self.moves[move].append(x)
                else:
                    done = 0
                    self.app.display("Invalid Score.")
                    break
            if done == 1 and len(self.moves[move]) > self.length:
                self.app.display("Invalid Score.")
                done = 0
        self.moves[move] = sorted(self.moves[move])
        displayer = strlist(self.moves[move], ", ")
        self.app.display("You Scored It With:", displayer)
        self.displayers.append((self.displayers.pop(),displayer))
        if self.moves[move] == [1]*self.length:
            self.app.display("The Computer Was Correct! ("+str(len(self.displayers))+" Guesses)")
            self.choosenew()
        else:
            self.register(self.attempt, 200)

if __name__ == "__main__":
    main("MasterMind", "Loading...", 35, colors, doshow, numpegs).start()
