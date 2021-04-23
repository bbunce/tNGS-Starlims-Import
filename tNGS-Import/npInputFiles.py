import re
import csv

class InputFiles():

    def __init__(self, varPath, starPath):
        self.varPath = varPath
        self.starPath = starPath
        self.starID = re.findall("[0-9]{7}", self.starPath)[0]
        try:
            self.tngsID = re.findall("[0-9]{7}", self.varPath)[0]
        except:
            print('No 7 digit id detected')
        self.starSamples = self.get_well_sample_instrIDs()
        self.noSamples = len(self.starSamples)

    def get_well_sample_instrIDs(self):
        samples = {}
        csv_file = open(self.starPath)
        csv_reader = list(csv.reader(csv_file, delimiter="\t"))
        for row in range(5, len(csv_reader)):
            samples[csv_reader[row][1][:9]] = [csv_reader[row][0], csv_reader[row][1]]
        csv_file.close()
        return samples



