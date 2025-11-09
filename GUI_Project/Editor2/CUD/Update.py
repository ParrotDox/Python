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
    QLabel
)
from PySide6.QtCore import Qt, Signal, QPointF
class UpdateDialog(QDialog):
    
    def __init__(self, figure, scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("UpdateDialog")
        self.setObjectName("UpdateDialog")
        self.setMinimumWidth(200)

        self.scaleFactor = scaleFactor
        self.figure: int = Figures.LINE
        self.points: list[QPointF] = []
        self.cube: QGraphicsCubeGroup = None
    
    def initUI(self, figure): #figure 1 - line, 2 - cube
        mainLayout = None
        if figure == Figures.LINE:
            #widgets
            x1 = QSpinBox(minimum=-10000, maximum=10000); x1.setMinimumWidth(50); x1.setMinimumHeight(35)
            x2 = QSpinBox(minimum=-10000, maximum=10000); x2.setMinimumWidth(50); x2.setMinimumHeight(35)
            y1 = QSpinBox(minimum=-10000, maximum=10000); y1.setMinimumWidth(50); y1.setMinimumHeight(35)
            y2 = QSpinBox(minimum=-10000, maximum=10000); y2.setMinimumWidth(50); y2.setMinimumHeight(35)
            label_x1 = QLabel("x1")
            label_x2 = QLabel("x2")
            label_y1 = QLabel("y1")
            label_y2 = QLabel("y2")
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.setPoints(x1.value(), x2.value(), y1.value(), y2.value()))
            confirm_2D.setFixedHeight(35)
            #layout
            mainLayout = QGridLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
            mainLayout.addWidget(label_x1, 0, 0); mainLayout.addWidget(label_x2, 0, 1)
            mainLayout.addWidget(x1, 1, 0); mainLayout.addWidget(x2, 1, 1)
            mainLayout.addWidget(label_y1, 2, 0); mainLayout.addWidget(label_y2, 2, 1)
            mainLayout.addWidget(y1, 3, 0); mainLayout.addWidget(y2, 3, 1)
            mainLayout.addWidget(confirm_2D, 4, 0, 1, 2)
        elif figure == Figures.CUBE:
            #widgets
            tX = QSpinBox(minimum=-10000, maximum=10000); tX.setMinimumWidth(50); tX.setMinimumHeight(35); 
            tY = QSpinBox(minimum=-10000, maximum=10000); tY.setMinimumWidth(50); tY.setMinimumHeight(35)
            tZ = QSpinBox(minimum=-10000, maximum=10000); tZ.setMinimumWidth(50); tZ.setMinimumHeight(35)
            sX = QSpinBox(minimum=0.1, maximum=10, value=1); sX.setMinimumWidth(50); sX.setMinimumHeight(35)
            sY = QSpinBox(minimum=0.1, maximum=10, value=1); sY.setMinimumWidth(50); sY.setMinimumHeight(35)
            sZ = QSpinBox(minimum=0.1, maximum=10, value=1); sZ.setMinimumWidth(50); sZ.setMinimumHeight(35)
            rX = QSpinBox(minimum=-360, maximum=360); rX.setMinimumWidth(50); rX.setMinimumHeight(35)
            rY = QSpinBox(minimum=-360, maximum=360); rY.setMinimumWidth(50); rY.setMinimumHeight(35)
            rZ = QSpinBox(minimum=-360, maximum=360); rZ.setMinimumWidth(50); rZ.setMinimumHeight(35)
            camZ  = QSpinBox(minimum=1, maximum=10000); camZ.setMinimumWidth(50); camZ.setMinimumHeight(35)
            label_tX = QLabel("Translate x")
            label_tY = QLabel("Translate y")
            label_tZ = QLabel("Translate z")
            label_sX = QLabel("Scale x")
            label_sY = QLabel("Scale y")
            label_sZ = QLabel("Scale z")
            label_rX = QLabel("Rotate x")
            label_rY = QLabel("Rotate y")
            label_rZ = QLabel("Rotate z")
            label_camZ = QLabel("Camera z")
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.setCube(tX.value(), tY.value(), tZ.value(), sX.value(), sY.value(), sZ.value(), rX.value(), rY.value(), rZ.value(), camZ.value(), self.scaleFactor))
            confirm_3D.setFixedHeight(35)
            #layout
            mainLayout = QGridLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
            mainLayout.addWidget(label_tX, 0, 0)
            mainLayout.addWidget(tX, 1, 0)
            mainLayout.addWidget(label_tY, 2, 0)
            mainLayout.addWidget(tY, 3, 0)
            mainLayout.addWidget(label_tZ, 4, 0)
            mainLayout.addWidget(tZ, 5, 0)
            mainLayout.addWidget(label_sX, 0, 1)
            mainLayout.addWidget(sX, 1, 1)
            mainLayout.addWidget(label_sY, 2, 1)
            mainLayout.addWidget(sY, 3, 1)
            mainLayout.addWidget(label_sZ, 4, 1)
            mainLayout.addWidget(sZ, 5, 1)
            mainLayout.addWidget(label_rX, 0, 2)
            mainLayout.addWidget(rX, 1, 2)
            mainLayout.addWidget(label_rY, 2, 2)
            mainLayout.addWidget(rY, 3, 2)
            mainLayout.addWidget(label_rZ, 4, 2)
            mainLayout.addWidget(rZ, 5, 2)
            mainLayout.addWidget(label_camZ, 6, 1)
            mainLayout.addWidget(camZ, 7, 1)
            mainLayout.addWidget(confirm_3D, 8, 1)

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