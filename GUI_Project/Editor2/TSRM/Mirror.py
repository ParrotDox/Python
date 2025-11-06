from EditorEnum import Figures
from CustomClasses import QGraphicsCustomItemGroup, QGraphicsMixedGroup, QGraphicsLineGroup, QGraphicsCustomScene
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

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF]):
        super().__init__()
        self.initUI()
        self.setWindowTitle("MirrorDialog"); self.setFixedSize(480, 320)
        self.setObjectName("MirrorDialog")

        self.scene = scene
        self.figure = figure
        self.points: list[QPointF] = points
        self.item: QGraphicsCustomItemGroup = item
        self.groupItem: QGraphicsCustomItemGroup = groupItem
    
    def initUI(self):
        #widgets
        mirrorer_X = QCheckBox("Mirror X")
        mirrorer_Y = QCheckBox("Mirror Y")
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.mirror(self.scene, self.figure, self.item, self.groupItem, self.points, mirrorer_X.isChecked(), mirrorer_Y.isChecked()))
        #layout
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(mirrorer_X)
        mainLayout.addWidget(mirrorer_Y)
        mainLayout.addWidget(confirm_2D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def mirror(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], mirrorX, mirrorY):
        if not mirrorX and not mirrorY:
            return
        
        if figure == Figures.LINE or figure == Figures.POINT:
            
            #points of line
            startPoint_GLOBAL = points[0]
            endPoint_GLOBAL = points[1]
            centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()
            
            #transformations for points (reverse motion)
            transform = QTransform()
            if mirrorX and not mirrorY: #transformation X
                transform.scale(-1, 1)
            elif not mirrorX and mirrorY: #transformation Y
                transform.scale(1, -1)
            elif mirrorX and mirrorY: #transformation XY
                transform.scale(-1, -1)
            
            #apply transformations
            startPoint = transform.map(startPoint_GLOBAL)
            endPoint = transform.map(endPoint_GLOBAL)
            self.points = [startPoint, endPoint]
        
        elif figure == Figures.MIXED:
            
            mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(group, (QGraphicsMixedGroup))
            mixedGroups.append(group)

            for gr in mixedGroups:
                for item in gr.childItems():
                    if isinstance(item, QGraphicsLineGroup):

                        #points of line
                        startPoint_GLOBAL = item.points[0]
                        endPoint_GLOBAL = item.points[1]
                        centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()

                         #transformations for points (reverse motion)
                        transform = QTransform()
                        if mirrorX and not mirrorY: #transformation X
                            transform.scale(-1, 1)
                        elif not mirrorX and mirrorY: #transformation Y
                            transform.scale(1, -1)
                        elif mirrorX and mirrorY: #transformation XY
                            transform.scale(-1, -1)

                        #apply transformations
                        startPoint = transform.map(startPoint_GLOBAL)
                        endPoint = transform.map(endPoint_GLOBAL)

                        points = [startPoint, endPoint]

                        #get parent
                        parent: QGraphicsMixedGroup = item.parentItem()

                        #create new line
                        newItem = AdditionalMethods.createCustomLine(points, scene.scaleFactor)

                        #replace old line by new
                        parent.removeFromGroup(item)
                        scene.removeItem(item)
                        parent.addToGroup(newItem)
                
                    elif isinstance(item, QGraphicsMixedGroup):
                        pass
                    
        elif figure == Figures.CUBE:
            pass
        self.accept()
    
                