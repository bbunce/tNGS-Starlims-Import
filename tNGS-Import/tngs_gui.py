from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from tngs_regex import VariantRegex
from tngs_import import Import
import sys

class Window(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("tNGS Starlims Import")
        self.setGeometry(50,50, 500, 300)
        self.setWindowIcon(QtGui.QIcon("../images/exeterlogo-small.png"))
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
        self.groupNGS = QGroupBox("Select tNGS 'Starlims Import' file")
        self.groupStarlims = QGroupBox("Select Starlims workbatch load file")
        gridNGS = QGridLayout()
        gridStarlims = QGridLayout()

        # Starlims Import file path
        self.txt_ngsPath = QLineEdit(self)
        self.btn_ngsPath = QPushButton("tNGS variant file")
        self.btn_ngsPath.clicked.connect(lambda: self.get_filePath(self.txt_ngsPath))

        # Starlims load file file path
        self.txt_starPath = QLineEdit(self)
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
        self.txt_ngsPath.setText("")
        self.txt_starPath.setText("")
        self.setStyleSheet(f"background-color: none;")

    def run(self):
        regex = VariantRegex(self.txt_ngsPath.text(),'../../output/')
        imp = Import(regex.fullExportPath,self.txt_starPath.text())

    def exit(self):
        sys.exit()

    def colour_dial(self):
        colours = ['mediumseagreen', 'cadetblue', 'lightcoral', 'khaki']
        self.setStyleSheet(f"background-color: {colours[int(self.dial.value()/25)]};")

    def msgbox_info(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)

        x = msg.exec_()  # this will show our messagebox

# def main():
#     app = QApplication(sys.argv)
#     window = Window()
#     sys.exit(app.exec_())
