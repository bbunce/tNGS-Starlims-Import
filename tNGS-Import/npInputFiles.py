import re

class InputFiles():

    def __init__(self, varPath, starPath):
        self.varPath = varPath
        self.starPath = starPath
        self.starID = re.findall("[0-9]{7}", self.starPath)[0]
        try:
            self.tngsID = re.findall("[0-9]{7}", self.varPath)[0]
        except:
            print('No 7 digit id detected')

    def check(self):
        print(self.varPath + "\n" + self.starPath)
        print(self.tngsID)
        print(self.starID)


