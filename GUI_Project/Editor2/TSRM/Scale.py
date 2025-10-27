from FIGURES import Figures
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QDoubleSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
    QGraphicsLineItem,
    QGraphicsItemGroup
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class ScaleDialog(QDialog):

    def __init__(self, figure: Figures, lineItem: QGraphicsItemGroup):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("ScaleDialog"); self.setFixedSize(480, 320)
        self.setObjectName("ScaleDialog")

        self.line = lineItem
        self.points: list[QPointF] = []
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.LINE:
            #widgets
            scaler_X = QDoubleSpinBox(minimum=0.1, maximum=10.0)
            scaler_Y = QDoubleSpinBox(minimum=0.1, maximum=10.0)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.scaleLine(scaler_X.value(), scaler_Y.value()))
            #layout
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(scaler_X)
            mainLayout.addWidget(scaler_Y)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            scalerX = QDoubleSpinBox(minimum=-360, maximum=360)
            confirm_3D = QPushButton("Confirm"); #confirm_3D.clicked()#!!!
            #layout
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(scalerX)
            mainLayout.addWidget(confirm_3D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def scaleLine(self, scaleX, scaleY):
        #get line from group
        items = self.line.childItems()
        lineItem = None
        for it in items:
            if isinstance(it, QGraphicsLineItem):
                lineItem = it
                break
        #get points and scale them
        startPoint = lineItem.line().p1(); startPoint.setX(startPoint.x()*scaleX); startPoint(startPoint.y()*scaleY)
        endPoint = lineItem.line().p2(); endPoint.setX(endPoint.x()*scaleX); endPoint(endPoint.y()*scaleY)
        self.Points = [startPoint, endPoint]
        self.accept()