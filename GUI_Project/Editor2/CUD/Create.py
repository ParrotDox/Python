from CustomClasses import QGraphicsLineGroup, QGraphicsCubeGroup, QGraphicsMixedGroup
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
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("CreateDialog"); self.setFixedSize(480, 320)
        self.setObjectName("CreateDialog")

        self.figure: int = Figures.LINE
        self.points: list[QPointF] = []

    def initUI(self):
        #Widgets
        tab = QTabWidget(); tab.currentChanged.connect(lambda: self.setDimension(tab))

        creator2D = QWidget()
        x1_2D = QSpinBox(minimum=-10000, maximum=10000)
        x2_2D = QSpinBox(minimum=-10000, maximum=10000)
        y1_2D = QSpinBox(minimum=-10000, maximum=10000)
        y2_2D = QSpinBox(minimum=-10000, maximum=10000)
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.setPoints(x1_2D.value(), x2_2D.value(), y1_2D.value(), y2_2D.value()))

        creator3D = QWidget()
        
        confirm_3D = QPushButton("Confirm"); #confirm_3D.clicked()#!!!

        tab.addTab(creator2D, "Line")
        tab.addTab(creator3D, "Cube")
        #Layouts
        mainLayout = QVBoxLayout()

        creator2DLayout = QGridLayout(); creator2DLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        creator3DLayout = QGridLayout(); creator3DLayout.setAlignment(Qt.AlignmentFlag.AlignTop)


        mainLayout.addWidget(tab)

        creator2DLayout.addWidget(x1_2D, 0, 0); creator2DLayout.addWidget(x2_2D, 1, 0)
        creator2DLayout.addWidget(y1_2D, 0, 1); creator2DLayout.addWidget(y2_2D, 1, 1)
        creator2DLayout.addWidget(confirm_2D, 2, 0, 1, 2)

        creator3DLayout.addWidget(confirm_3D, 0, 0, 1, 2)

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