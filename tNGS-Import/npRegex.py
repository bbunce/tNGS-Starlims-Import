import openpyxl
from datetime import datetime
import os

class Regex:

    def __init__(self, varPath, varID, workDir):
        self.varPath = varPath
        self.varID = varID
        self.workDir = workDir
        self.timeNow = datetime.now().strftime("%Y-%m-%d %H%M")
        self.newWbName = f"{self.workDir}{self.varID} regex {self.timeNow}.xlsx"
        self.wb = self.createCopy()
        self.ws = self.createWorksheets()

    def createCopy(self):
        openpyxl.load_workbook(self.varPath).save(self.newWbName)
        return openpyxl.load_workbook(self.newWbName)

    def createWorksheets(self):
        ws_ms = self.wb.create_sheet("MutationSurveyor")
        ws_var = self.wb.create_sheet("VariantDetails")
        self.wb.save(self.newWbName)
        return {'ms': ws_ms, 'var': ws_var}

