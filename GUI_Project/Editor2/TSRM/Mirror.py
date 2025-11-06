from EditorEnum import Figures
from CustomClasses import QGraphicsLineGroup, QGraphicsCubeGroup, QGraphicsMixedGroup
from Additional import AdditionalMethods
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
from CustomClasses import (
    QGraphicsLineGroup, 
    QGraphicsCubeGroup, 
    QGraphicsPointGroup,
    QGraphicsMixedGroup)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class MirrorDialog(QDialog, AdditionalMethods):

    def __init__(self, figure: Figures, groupItem: QGraphicsItemGroup, points: list[QPointF]):
        super().__init__()
        self.initUI()
        self.setWindowTitle("MirrorDialog"); self.setFixedSize(480, 320)
        self.setObjectName("MirrorDialog")

        self.figure = figure
        self.groupItem = groupItem
        self.points: list[QPointF] = points #At start: raw, at result: mirrored
        self.items: QGraphicsItemGroup = []
    
    def initUI(self):
        #widgets
        mirrorer_X = QCheckBox("Mirror X")
        mirrorer_Y = QCheckBox("Mirror Y")
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.MirrorItem(self.figure, self.points, mirrorer_X.isChecked(), mirrorer_Y.isChecked()))
        #layout
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(mirrorer_X)
        mainLayout.addWidget(mirrorer_Y)
        mainLayout.addWidget(confirm_2D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def MirrorItem(self, figure: Figures, points: list[QPointF], mirrorX, mirrorY):
        if not mirrorX and not mirrorY:
            return
        if figure == Figures.LINE:
            #points of line
            startPoint_GLOBAL = points[0]
            endPoint_GLOBAL = points[1]
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
    
                