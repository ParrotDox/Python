from FIGURES import Figures
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, Signal, QPointF
class UpdateDialog(QDialog):
    
    def __init__(self, figure):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("UpdateDialog"); self.setFixedSize(480, 320)
        self.setObjectName("UpdateDialog")

        self.points: list[QPointF] = []
    
    def initUI(self, figure): #figure 1 - line, 2 - cube
        mainLayout = None
        if figure == Figures.LINE:
            #widgets
            x1_2D = QSpinBox(minimum=-10000, maximum=10000)
            x2_2D = QSpinBox(minimum=-10000, maximum=10000)
            y1_2D = QSpinBox(minimum=-10000, maximum=10000)
            y2_2D = QSpinBox(minimum=-10000, maximum=10000)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.setPoints(x1_2D.value(), x2_2D.value(), y1_2D.value(), y2_2D.value()))
            #layout
            mainLayout = QGridLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            mainLayout.addWidget(x1_2D, 0, 0); mainLayout.addWidget(x2_2D, 1, 0)
            mainLayout.addWidget(y1_2D, 0, 1); mainLayout.addWidget(y2_2D, 1, 1)
            mainLayout.addWidget(confirm_2D, 2, 0, 1, 2)
        elif figure == Figures.CUBE:
            #widgets
            confirm_3D = QPushButton("Confirm"); #confirm_3D.clicked()#!!!
            #layout
            mainLayout = QGridLayout()

        self.setLayout(mainLayout)
        #StyleSheets
        pass

    #Slots
    def setDimension(self, tab: QTabWidget):
        self.dimension = tab.currentIndex()
        return
    def setPoints(self, x1, x2, y1, y2):
        if x1 == x2 and y1 == y2:
            print("Points can't have equal coordinates.")
            return
        self.points = [QPointF(float(x1), float(y1)), QPointF(float(x2), float(y2))]
        self.accept()