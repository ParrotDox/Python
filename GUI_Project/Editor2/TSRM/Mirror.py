from FIGURES import Figures
from TSRM.Additional import AdditionalDialogMethods
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QCheckBox,
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

class MirrorDialog(QDialog, AdditionalDialogMethods):

    def __init__(self, figure: Figures, groupItem: QGraphicsItemGroup):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("MirrorDialog"); self.setFixedSize(480, 320)
        self.setObjectName("MirrorDialog")

        self.groupItem = groupItem
        self.points: list[QPointF] = self.getPoints(groupItem)
        self.items: QGraphicsItemGroup = []
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        #widgets
        mirrorer_X = QCheckBox("Mirror X")
        mirrorer_Y = QCheckBox("Mirror Y")
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.MirrorItem(mirrorer_X.isChecked(), mirrorer_Y.isChecked(), figure))
        #layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(mirrorer_X)
        mainLayout.addWidget(mirrorer_Y)
        mainLayout.addWidget(confirm_2D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def MirrorItem(self, mirrorX, mirrorY, figure: Figures):
        if figure == Figures.LINE:
            #get lineItem from group
            lineItem = self.getLineItemFromGroup(self.groupItem)
            #points of line
            startPoint_GLOBAL = lineItem.line().p1()
            centerPoint_GLOBAL = lineItem.line().center()
            endPoint_GLOBAL = lineItem.line().p2()
            #transformations for points (reverse motion)
            transform = QTransform()
            if mirrorX and not mirrorY: #transformation X
                transform.scale(-1, 1)
                #apply transformation
            elif not mirrorX and mirrorY: #transformation Y
                transform.scale(1, -1)
            elif mirrorX and mirrorY: #transformation XY
                transform.scale(-1, -1)
            #apply transformations
            startPoint = transform.map(startPoint_GLOBAL)
            endPoint = transform.map(endPoint_GLOBAL)
            self.points = [startPoint, endPoint]
            
        elif figure == Figures.CUBE:
            pass
        self.accept()
    
                