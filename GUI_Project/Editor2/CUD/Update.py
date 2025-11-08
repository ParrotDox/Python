from CustomClasses import QGraphicsLineGroup, QGraphicsCubeGroup, QGraphicsMixedGroup, AdditionalMethods
from EditorEnum import Figures
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
    
    def __init__(self, figure, scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("UpdateDialog")
        self.setObjectName("UpdateDialog")

        self.scaleFactor = scaleFactor
        self.figure: int = Figures.LINE
        self.points: list[QPointF] = []
        self.cube: QGraphicsCubeGroup = None
    
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
            tX = QSpinBox(minimum=-10000, maximum=10000)
            tY = QSpinBox(minimum=-10000, maximum=10000)
            tZ = QSpinBox(minimum=-10000, maximum=10000)
            sX = QSpinBox(minimum=0.1, maximum=10, value=1)
            sY = QSpinBox(minimum=0.1, maximum=10, value=1)
            sZ = QSpinBox(minimum=0.1, maximum=10, value=1)
            rX = QSpinBox(minimum=-360, maximum=360)
            rY = QSpinBox(minimum=-360, maximum=360)
            rZ = QSpinBox(minimum=-360, maximum=360)
            camZ  = QSpinBox(minimum=1, maximum=10000)
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.setCube(tX.value(), tY.value(), tZ.value(), sX.value(), sY.value(), sZ.value(), rX.value(), rY.value(), rZ.value(), camZ.value(), self.scaleFactor))
            #layout
            mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            mainLayout.addWidget(tX)
            mainLayout.addWidget(tY)
            mainLayout.addWidget(tZ)
            mainLayout.addWidget(sX)
            mainLayout.addWidget(sY)
            mainLayout.addWidget(sZ)
            mainLayout.addWidget(rX)
            mainLayout.addWidget(rY)
            mainLayout.addWidget(rZ)
            mainLayout.addWidget(camZ)
            mainLayout.addWidget(confirm_3D)

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
    def setCube(self, tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleFactor):
        cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleFactor)
        self.points = cube.cubePoints
        self.cube = cube
        self.accept()