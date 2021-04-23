# '''
# import os
# import openpyxl
# from npInputFiles import InputFiles
# from npImportWs import ImportWorksheet
# from npVariant import Variant
#
# # input file paths
# varPath = r"C:\Users\bhsbu\dev\Work\tNGS-Starlims-Import\data\2020-07-14_2004549_variants.14-07-2020_STARLiMS_import.xlsx"
# starPath = r"C:\Users\bhsbu\dev\Work\tNGS-Starlims-Import\data\PL2000003-02-01.txt"
#
# inputFiles = InputFiles(varPath, starPath)
#
# # create new directory to store all working files
# try:
#     workDir = f"{os.path.dirname(varPath)}\\{inputFiles.tngsID} tNGS import files\\"
#     os.mkdir(workDir)
# except FileExistsError:
#     pass
#
# importWs = ImportWorksheet(varPath, inputFiles.tngsID, workDir)
#
# # loop through variants in varPath and assign to sample_var dictionary
# sample_var = inputFiles.starSamples
# for i in range(2, importWs.ws_main_noRows+1):
#     sampleID = importWs.ws_main.cell(row=i, column=1).value
#     if sampleID in sample_var:
#         sample_var[sampleID].append(Variant(importWs.ws_main, i))
#
# # write variants to variantDetails tab
# importWs.write_variantDetails(sample_var)
# # importWs.write_mutationSurveyor(sample_var)
#
# importWs.closeWs()
# '''

from npGui import Window
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




