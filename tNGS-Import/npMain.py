# tNGS starlims import file format .xlxs
# starlims sequencing load file format .txt

import os, shutil
from npInputFiles import InputFiles
from npRegex import Regex

# input file paths
varPath = r"C:\Users\bhsbu\dev\Work\tNGS-Starlims-Import\data\2020-07-14_2004549_variants.14-07-2020_STARLiMS_import.xlsx"
starPath = r"C:\Users\bhsbu\dev\Work\tNGS-Starlims-Import\data\PL2000003-02-01"

tNGS = InputFiles(varPath, starPath)

# create new directory to store all working files
try:
    workDir = f"{os.path.dirname(varPath)}\\{tNGS.tngsID} tNGS import files\\"
    os.mkdir(workDir)
except FileExistsError:
    pass
    # shutil.rmtree(workDir) # delete directory and contents

Regex = Regex(varPath, tNGS.tngsID, workDir)


# tNGS.check()
# Regex.createCopy()


