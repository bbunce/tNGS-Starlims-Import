from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from npInputFiles import InputFiles
from npImportWs import ImportWorksheet
from npVariant import Variant
import sys
import os

class Window(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("tNGS Starlims Import")
        self.setGeometry(50,50, 500, 300)
        # self.setWindowIcon(QtGui.QIcon("../images/exeterlogo-small.png"))
        self.UI()

    def UI(self):
        self.header()
        self.body()
        self.footer()

        vbox = QVBoxLayout()
        vbox.addWidget(self.groupTitle)
        vbox.addWidget(self.groupNGS)
        vbox.addWidget(self.groupStarlims)
        vbox.addWidget(self.groupFooter)
        self.setLayout(vbox)

        self.show()

    def header(self):
        self.groupTitle = QGroupBox()
        gridHeader = QGridLayout()
        title = QLabel("tNGS Starlims Import")
        newfont = QtGui.QFont("Arial", 28, QtGui.QFont.Bold)
        title.setFont(newfont)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridHeader.addWidget(title,0,0)
        self.groupTitle.setLayout(gridHeader)

    def body(self):
        ngs_fPath = "Select file..."
        star_fPath = "Select file..."

        self.groupNGS = QGroupBox("Select tNGS 'Summary' file")
        self.groupStarlims = QGroupBox("Select Starlims workbatch load file")
        gridNGS = QGridLayout()
        gridStarlims = QGridLayout()

        # Starlims Import file path
        self.txt_ngsPath = QLineEdit(self)
        self.txt_ngsPath.setText(ngs_fPath)
        self.btn_ngsPath = QPushButton("tNGS variant file")
        self.btn_ngsPath.clicked.connect(lambda: self.get_filePath(self.txt_ngsPath))

        # Starlims load file file path
        self.txt_starPath = QLineEdit(self)
        self.txt_starPath.setText(star_fPath)
        self.btn_starPath = QPushButton("Starlims load file")
        self.btn_starPath.clicked.connect(lambda: self.get_filePath(self.txt_starPath))

        gridNGS.addWidget(self.txt_ngsPath, 0,0)
        gridNGS.addWidget(self.btn_ngsPath, 0,1)
        gridStarlims.addWidget(self.txt_starPath, 1,0)
        gridStarlims.addWidget(self.btn_starPath, 1,1)

        self.groupNGS.setLayout(gridNGS)
        self.groupStarlims.setLayout(gridStarlims)

    def footer(self):
        self.groupFooter = QGroupBox("")
        gridFooter = QGridLayout()

        # Reset form
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(lambda: self.reset_form())

        # Run
        self.btn_run = QPushButton("Run")
        self.btn_run.clicked.connect(lambda: self.run())

        # Quit
        self.btn_exit = QPushButton("Close")
        self.btn_exit.clicked.connect(self.exit)

        # Colour Dial
        self.dial = QDial()
        self.dial.setMinimum(1)
        self.dial.setMaximum(75)
        self.dial.setValue(1)
        self.dial.valueChanged.connect(self.colour_dial)

        gridFooter.addWidget(self.btn_reset, 0 , 1)
        gridFooter.addWidget(self.btn_run, 0, 2)
        gridFooter.addWidget(self.btn_exit, 0, 3)
        gridFooter.addWidget(self.dial, 0, 4)

        self.groupFooter.setLayout(gridFooter)


    def get_filePath(self, textbox):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open file", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            textbox.setText(fileName)

    def reset_form(self):
        self.txt_ngsPath.setText("Select file...")
        self.txt_starPath.setText("Select file...")
        self.setStyleSheet(f"background-color: none;")
        self.msgbox("Information", "Form reset")

    def run(self):
        #self.msgbox("Information", "Processing...")
        try:
            inputFiles = InputFiles(self.txt_ngsPath.text(), self.txt_starPath.text())

            # create new directory to store all working files
            try:
                workDir = f"{os.path.dirname(self.txt_ngsPath.text())}\\{inputFiles.tngsID} tNGS import files\\"
                os.mkdir(workDir)
            except FileExistsError:
                pass

            importWs = ImportWorksheet(self.txt_ngsPath.text(), inputFiles.tngsID, inputFiles.starID, workDir)

            # loop through variants in varPath and assign to sample_var dictionary
            sample_var = inputFiles.starSamples
            for i in range(2, importWs.ws_main_noRows + 1):
                sampleID = importWs.ws_main.cell(row=i, column=1).value
                if sampleID in sample_var:
                    sample_var[sampleID].append(Variant(importWs.ws_main, i))

            # write variants to variantDetails tab
            importWs.write_variantDetails(sample_var)

            # write variant to mutationsurveyor tab
            importWs.write_mutationSurveyor(sample_var)

        except Exception as e:
            self.msgbox("Run Error:", str(e))
            # self.reset_form()
            return None
        self.msgbox("User reminder", "Please check X-linked gene zygosity calls and any mitochondiral variant "
                    + "nomenclature")
        self.msgbox("Information", "\tComplete\t\t")

    def exit(self):
        sys.exit()

    def colour_dial(self):
        colours = ['mediumseagreen', 'cadetblue', 'lightcoral', 'khaki']
        self.setStyleSheet(f"background-color: {colours[int(self.dial.value()/25)]};")

    def msgbox(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)

        x = msg.exec_()  # this will show our messagebox
