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

class ProjectionDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF]):
        super().__init__()
        self.initUI()
        self.setWindowTitle("ProjectionDialog"); self.setFixedSize(480, 320)
        self.setObjectName("ProjectionDialog")

        self.scene = scene
        self.figure = figure
        self.points: list[QPointF] = points
        self.item: QGraphicsCustomItemGroup = item
        self.groupItem: QGraphicsCustomItemGroup = groupItem
    
    def initUI(self):
        #widgets
        projectedXZ = QCheckBox("Project to XZ")
        projectedYZ = QCheckBox("Project to YZ")
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.project(self.scene, self.figure, self.item, self.groupItem, self.points, projectedXZ.isChecked(), projectedYZ.isChecked()))
        #layout
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(projectedXZ)
        mainLayout.addWidget(projectedYZ)
        mainLayout.addWidget(confirm_2D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def project(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], projectedXZ, projectedYZ):
        if (not projectedXZ and not projectedYZ) or (projectedXZ and projectedYZ):
            return
        
        if figure == Figures.LINE or figure == Figures.POINT:
            
            #points of line
            startPoint_GLOBAL = points[0]
            endPoint_GLOBAL = points[1]
            centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()
            
            #transformations for points (reverse motion)
            transform = QTransform()
            if projectedXZ and not projectedYZ: #Make Y-Axis zeroed
                transform.scale(1, 0)
            elif not projectedXZ and projectedYZ: #Make X-Axis zeroed
                transform.scale(0, 1)
            
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
                        if projectedXZ and not projectedYZ: #Make Y-Axis zeroed
                            transform.scale(1, 0)
                        elif not projectedXZ and projectedYZ: #Make X-Axis zeroed
                            transform.scale(0, 1)

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
    
                