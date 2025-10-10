#Import modules
from random import choice
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)


#Main app objects and settings
app = QApplication([])
mainWindow = QWidget()
mainWindow.setWindowTitle("Random word maker")
mainWindow.resize(300, 200)

article = QLabel("Word randomizer")
textL = QLabel("?")
textM = QLabel("?")
textR = QLabel("?")
buttonL = QPushButton("Randomize")
buttonM = QPushButton("Randomize")
buttonR = QPushButton("Randomize")

words = ["Kawaboonga", "Bahoonker", "Boinker", "Truncate", "Capybara", "LeFrog", "Konnichiwa"]


#All design here
masterLayout = QVBoxLayout()
row1 = QHBoxLayout()
row2 = QHBoxLayout()
row3 = QHBoxLayout()

row1.addWidget(article, alignment=Qt.AlignmentFlag.AlignCenter)

row2.addWidget(textL, alignment=Qt.AlignmentFlag.AlignCenter)
row2.addWidget(textM, alignment=Qt.AlignmentFlag.AlignCenter)
row2.addWidget(textR, alignment=Qt.AlignmentFlag.AlignCenter)

row3.addWidget(buttonL)
row3.addWidget(buttonM)
row3.addWidget(buttonR)

masterLayout.addLayout(row1)
masterLayout.addLayout(row2)
masterLayout.addLayout(row3)
mainWindow.setLayout(masterLayout)



#Create Functions
def randomWord(btn: QPushButton):
    word = choice(words)
    if btn == buttonL:
        textL.setText(word)
    elif btn == buttonM:
        textM.setText(word)
    elif btn == buttonR:
        textR.setText(word)


#Events
buttonL.clicked.connect(lambda: randomWord(buttonL))
buttonM.clicked.connect(lambda: randomWord(buttonM))
buttonR.clicked.connect(lambda: randomWord(buttonR))


#Show/Run App
mainWindow.show()
app.exec_()