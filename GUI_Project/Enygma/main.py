import Enygma
import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from Enygma import *

class EnygmaWidget(QMainWindow):
    layout: QLayout
    mainLayout: QVBoxLayout
    textAreaLayout: QHBoxLayout
    buttonLayout: QHBoxLayout

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enygma")

        #Creation of main widget
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)

        #Widget creation
        self.InputTextArea = QLineEdit(maxLength=10)
        self.OutputTextArea = QLineEdit(maxLength=10)
        self.processButton = QPushButton("Process")

        #Widget size config
        self.InputTextArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.OutputTextArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.processButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        #Widget textSize config
        font = QFont()
        font.setPointSize(20)
        self.InputTextArea.setFont(font)
        self.OutputTextArea.setFont(font)
        self.processButton.setFont(font)

        #Widget signals and slots config
        self.processButton.clicked.connect(self.processWord)
        #Layout creation
        self.mainLayout = QVBoxLayout()
        self.textAreaLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        #Layout filling
        self.textAreaLayout.addWidget(self.InputTextArea)
        self.textAreaLayout.addWidget(self.OutputTextArea)
        self.buttonLayout.addWidget(self.processButton)

        #Layout inclusion
        self.mainLayout.addLayout(self.textAreaLayout)
        self.mainLayout.addLayout(self.buttonLayout)

        #Set the main layout
        mainWidget.setLayout(self.mainLayout)

    #Mechanism of encoding
    @Slot(result=str)
    def processWord(self):
        sample = self.InputTextArea.text()
        encodedSample = self.encodeWord(sample)
        self.OutputTextArea.setText(encodedSample)
    
    @Slot(result=str)
    def encodeWord(self, sample):
        rotor1 = Rotor("JGDQOXUSCAMIFRVTPNEWKBLZYH", "F")
        rotor2 = Rotor("NTZPSFBOKMWRCJDIVLAEYUXHGQ", "A")
        mirror = Mirror("YRUHQSLDPXNGOKMIEBFZCWVJAT")
        enygma1 = Enygma(mirror, [rotor1, rotor2])
        encodedWord = ""
        for ch in sample:
            encodedWord += enygma1.EncryptSymbol(ch)
            enygma1.RotateWheels()
        return encodedWord


def main():
    app = QApplication(sys.argv)
    widget = EnygmaWidget()
    widget.show()
    sys.exit(app.exec())
main()