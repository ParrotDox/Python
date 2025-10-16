#Import modules
import re
from math import floor
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy
    )


#Main app, widgets and settings
app = QApplication([])
mainWindow = QWidget(); mainWindow.setFont(QFont("Bahnscrift", 14))
mainWindow.setWindowTitle("Calculator")

label = QLabel("Input"); label.setFixedHeight(25)
lineEdit = QLineEdit(); lineEdit.setFixedHeight(30); lineEdit.setReadOnly(True)

operationMarks = "/*C-+%"
operationButtons = []
for mrk in operationMarks:
    btn = QPushButton(mrk)
    btn.setMinimumWidth(35)
    btn.setMinimumHeight(35)
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    operationButtons.append(btn)

numberButtons = []
for num in range(10):
    btn = QPushButton(str(num))
    btn.setMinimumWidth(35)
    btn.setMinimumHeight(35)
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    numberButtons.append(btn)

processButton = QPushButton("Process")
processButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


#All design here
styleSheet="QWidget {background-color: #292f31; color: #d7dee1}" \
"QLineEdit { border: 0px solid #222}" \
"QPushButton { border: 0px solid #222; border-radius: 5px; background-color: #5c676b}" \
"QPushButton:hover { background-color: #6355df}" \
"QPushButton:pressed { background-color: #9a94f6}"

mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
panelLayout = QGridLayout()

mainLayout.addWidget(label)
mainLayout.addWidget(lineEdit)
mainLayout.addLayout(panelLayout)

for i in range(len(operationButtons)):
    btn = operationButtons[i]
    row = floor(i/3)
    col = i%3
    panelLayout.addWidget(btn, row, col)
    panelLayout.setColumnStretch(col, 1)
    panelLayout.setRowStretch(row, 1)
    
for i in range(len(numberButtons)):
    btn = numberButtons[i]
    row = floor(i/3) + 3
    col = i%3
    panelLayout.addWidget(btn, row, col)
    panelLayout.setColumnStretch(col, 1)
    panelLayout.setRowStretch(row, 1)

panelLayout.addWidget(processButton, 6, 1, 1, 2)

mainWindow.setLayout(mainLayout)
mainWindow.setStyleSheet(styleSheet)

#Create Functions
def input(mark):
    if (mark == "C"):
        lineEdit.clear()
        return
    currentLine = lineEdit.text()
    lineLength = len(currentLine)
    #Can't write operations at the start
    if (lineLength == 0) and (mark in operationMarks):
        return
    #Can't write two operations in a row
    if (mark in operationMarks) and (currentLine[-1] in operationMarks):
        return
    #Can't write 0 as the first digit of the number
    if (mark == "0") and (lineLength == 0 or currentLine[-1] in operationMarks):
        return
    
    #If there is a result <= 0
    try:
        if int(currentLine) <= 0:
            lineEdit.setText(mark)
            return
    except:
        print("Input check <= 0 exception (Usually it's normal. Nothing to check)")

    lineEdit.setText(currentLine + mark)

def process():
    currentLine = lineEdit.text()
    lineLength = len(currentLine)
    pattern = f"([{re.escape(operationMarks)}])"
    splitted = re.split(pattern, currentLine)
    
    if splitted[-1] in operationMarks:
        return
    
    result = int(splitted[0])
    try:
        operation = ""
        isReady = False
        for splits in splitted[1:]:
            if isReady == False:
                operation = splits
                isReady = True
            else:   #/*C-+%
                number = int(splits)
                if operation == operationMarks[0]:
                    result /= number
                elif operation == operationMarks[1]:
                    result *= number
                elif operation == operationMarks[3]:
                    result -= number
                elif operation == operationMarks[4]:
                    result += number
                elif operation == operationMarks[5]:
                    result %= number
                isReady = False
    except Exception as err:
        print(err)
    
    result = round(result)
    lineEdit.setText(str(result))
    
def _connectMarkEvents(iteration):
    if iteration >= len(operationMarks):
        return
    btn: QPushButton = operationButtons[iteration]
    btn.clicked.connect(lambda: input(operationMarks[iteration]))
    return _connectMarkEvents(iteration + 1)

def _connectNumberEvents(iteration):
    if iteration == 10:
        return
    btn: QPushButton = numberButtons[iteration]
    btn.clicked.connect(lambda: input(str(iteration)))
    return _connectNumberEvents(iteration + 1)


#Events
_connectMarkEvents(0)
_connectNumberEvents(0)
processButton.clicked.connect(process)
    

#Show/Run App
mainWindow.show()
app.exec()