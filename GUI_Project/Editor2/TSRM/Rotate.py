from FIGURES import Figures
from TSRM.Additional import AdditionalDialogMethods
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
    QGraphicsScene,
    QGraphicsLineItem,
    QGraphicsItemGroup
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class RotateDialog(QDialog, AdditionalDialogMethods):

    def __init__(self, figure: Figures, groupItem: QGraphicsItemGroup):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("RotateDialog"); self.setFixedSize(480, 320)
        self.setObjectName("RotateDialog")

        self.groupItem = groupItem
        self.points: list[QPointF] = self.getPoints(groupItem)
    
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
        #get lineItem from group
        lineItem = self.getLineItemFromGroup(self.groupItem)
        #points of line
        startPoint_GLOBAL = lineItem.line().p1()
        centerPoint_GLOBAL = lineItem.line().center()
        endPoint_GLOBAL = lineItem.line().p2()
        #transformations for points (reverse motion)
        transform = QTransform()
        transform.translate(centerPoint_GLOBAL.x(), centerPoint_GLOBAL.y())
        transform.rotate(rotation)
        transform.translate(centerPoint_GLOBAL.x() * -1, centerPoint_GLOBAL.y() * -1)
        #apply transformations
        startPoint = transform.map(startPoint_GLOBAL)
        endPoint = transform.map(endPoint_GLOBAL)
        self.points = [startPoint, endPoint]
        self.accept()