from FIGURES import Figures
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
    QGraphicsLineItem,
    QGraphicsItemGroup
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF

class RotateDialog(QDialog):

    def __init__(self, figure: Figures, lineItem: QGraphicsItemGroup):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("RotateDialog"); self.setFixedSize(480, 320)
        self.setObjectName("RotateDialog")

        self.line = lineItem
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.LINE:
            #widgets
            rotator = QSpinBox(minimum=-360, maximum=360)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.rotateLine(rotator.value()))
            #layout
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(rotator)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            rotatorX = QSpinBox(minimum=-360, maximum=360)
            rotatorY = QSpinBox(minimum=-360, maximum=360)
            rotatorZ = QSpinBox(minimum=-360, maximum=360)
            confirm_3D = QPushButton("Confirm"); #confirm_3D.clicked()#!!!
            #layout
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(rotatorX)
            mainLayout.addWidget(rotatorY)
            mainLayout.addWidget(rotatorZ)
            mainLayout.addWidget(confirm_3D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def rotateLine(self, rotation):
        #get line from group
        items = self.line.childItems()
        lineItem = None
        print(f"rotate {self.line}")
        for it in items:
            if isinstance(it, QGraphicsLineItem):
                lineItem = it
                break
        #Find center of rotation
        lineCenter = lineItem.line().center()
        centerPoint = lineItem.mapToParent(lineCenter)
        print(centerPoint)
        #rotate group relative to the center
        self.line.setTransformOriginPoint(centerPoint)
        self.line.setRotation(lineItem.rotation() + rotation)
        self.accept()