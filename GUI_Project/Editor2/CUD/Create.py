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

class CreateDialog(QDialog):
    
    def __init__(self, scaleFactor):
        super().__init__()
        self.initUI()
        self.setWindowTitle("CreateDialog")
        self.setObjectName("CreateDialog")

        self.scaleFactor = scaleFactor
        self.figure: int = Figures.LINE
        self.points: list[QPointF] = []
        self.cube: QGraphicsCubeGroup = None

    def initUI(self):
        #Widgets
        tab = QTabWidget(); tab.currentChanged.connect(lambda: self.setDimension(tab))

        creator2D = QWidget()
        x1 = QSpinBox(minimum=-10000, maximum=10000)
        x2 = QSpinBox(minimum=-10000, maximum=10000)
        y1 = QSpinBox(minimum=-10000, maximum=10000)
        y2 = QSpinBox(minimum=-10000, maximum=10000)
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.setPoints(x1.value(), x2.value(), y1.value(), y2.value()))

        creator3D = QWidget()
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

        tab.addTab(creator2D, "Line")
        tab.addTab(creator3D, "Cube")
        #Layouts
        mainLayout = QVBoxLayout()

        creator2DLayout = QGridLayout(); creator2DLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        creator3DLayout = QVBoxLayout(); creator3DLayout.setAlignment(Qt.AlignmentFlag.AlignTop)


        mainLayout.addWidget(tab)

        creator2DLayout.addWidget(x1, 0, 0); creator2DLayout.addWidget(x2, 1, 0)
        creator2DLayout.addWidget(y1, 0, 1); creator2DLayout.addWidget(y2, 1, 1)
        creator2DLayout.addWidget(confirm_2D, 2, 0, 1, 2)

        creator3DLayout.addWidget(tX)
        creator3DLayout.addWidget(tY)
        creator3DLayout.addWidget(tZ)
        creator3DLayout.addWidget(sX)
        creator3DLayout.addWidget(sY)
        creator3DLayout.addWidget(sZ)
        creator3DLayout.addWidget(rX)
        creator3DLayout.addWidget(rY)
        creator3DLayout.addWidget(rZ)
        creator3DLayout.addWidget(camZ)
        creator3DLayout.addWidget(confirm_3D)

        creator2D.setLayout(creator2DLayout)
        creator3D.setLayout(creator3DLayout)
        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def setDimension(self, tab: QTabWidget):
        option = tab.currentIndex()
        if option == 0:
            self.figure = Figures.LINE
        elif option == 1:
            self.figure = Figures.CUBE
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
