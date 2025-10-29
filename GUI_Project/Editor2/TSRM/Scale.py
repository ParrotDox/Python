from EditorEnum import Figures
from TSRM.Additional import AdditionalDialogMethods
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QDoubleSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
    QGraphicsScene,
    QGraphicsLineItem,
    QGraphicsItemGroup,
    QGraphicsEllipseItem
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class ScaleDialog(QDialog, AdditionalDialogMethods):

    def __init__(self, figure: Figures, groupItem: QGraphicsItemGroup):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("ScaleDialog"); self.setFixedSize(480, 320)
        self.setObjectName("ScaleDialog")

        self.groupItem = groupItem
        self.points: list[QPointF] = self.getPoints(groupItem)
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.LINE:
            #widgets
            scaler_X = QDoubleSpinBox(minimum=0.1, maximum=10.0)
            scaler_Y = QDoubleSpinBox(minimum=0.1, maximum=10.0)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.scaleLine(scaler_X.value(), scaler_Y.value()))
            #layout
            mainLayout.addWidget(scaler_X)
            mainLayout.addWidget(scaler_Y)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            scalerX = QDoubleSpinBox(minimum=-360, maximum=360)
            confirm_3D = QPushButton("Confirm"); #confirm_3D.clicked()#!!!
            #layout
            mainLayout.addWidget(scalerX)
            mainLayout.addWidget(confirm_3D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def scaleLine(self, scaleX, scaleY):
        #get lineItem from group
        lineItem = self.getLineItemFromGroup(self.groupItem)
        #points of line
        startPoint_GLOBAL = lineItem.line().p1()
        centerPoint_GLOBAL = lineItem.line().center()
        endPoint_GLOBAL = lineItem.line().p2()
        #transformations for points (reverse motion)
        transform = QTransform()
        transform.translate(centerPoint_GLOBAL.x(), centerPoint_GLOBAL.y())
        transform.scale(scaleX, scaleY)
        transform.translate(centerPoint_GLOBAL.x() * -1, centerPoint_GLOBAL.y() * -1)
        #apply transformations
        startPoint = transform.map(startPoint_GLOBAL)
        endPoint = transform.map(endPoint_GLOBAL)
        self.points = [startPoint, endPoint]
        self.accept()
    
                