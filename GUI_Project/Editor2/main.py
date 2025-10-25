from Editor import *
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow
)
#App init and start
app = QApplication([])
mainWindow = EditorWidget()
mainWindow.show()
app.exec()