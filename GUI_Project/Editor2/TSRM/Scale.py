from EditorEnum import Figures
from CustomClasses import QGraphicsCustomItemGroup, QGraphicsMixedGroup, QGraphicsLineGroup, QGraphicsCustomScene
from Additional import AdditionalMethods
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

class ScaleDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF]):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("TranslateDialog"); self.setFixedSize(480, 320)
        self.setObjectName("TranslateDialog")

        self.scene = scene
        self.figure = figure
        self.points: list[QPointF] = points
        self.item: QGraphicsCustomItemGroup = item
        self.groupItem: QGraphicsCustomItemGroup = groupItem
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.POINT or figure == Figures.LINE or figure == Figures.MIXED:
            #widgets
            scaler_X = QDoubleSpinBox(minimum=0.1, maximum=10.0)
            scaler_Y = QDoubleSpinBox(minimum=0.1, maximum=10.0)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.scale(self.scene, self.figure, self.item, self.groupItem, self.points, scaler_X.value(), scaler_Y.value()))
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
    def scale(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], scaleX, scaleY):
        
        if figure == Figures.POINT:
            
            #If group is a MixedGroup
            if isinstance(group, QGraphicsMixedGroup):
                
                mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(group, (QGraphicsMixedGroup))
                mixedGroups.append(group)
                anchorPoint = item.mapToScene(item.boundingRect().center() / scene.scaleFactor)

                for gr in mixedGroups:
                    for item in gr.childItems():
                        if isinstance(item, QGraphicsLineGroup):

                            #points of line
                            startPoint_GLOBAL = item.points[0]
                            endPoint_GLOBAL = item.points[1]
                            centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()

                             #transformations for points (reverse motion)
                            transform = QTransform()
                            transform.translate(anchorPoint.x(), anchorPoint.y())
                            transform.scale(scaleX, scaleY)
                            transform.translate(anchorPoint.x() * -1, anchorPoint.y() * -1)

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
            
                #If group is a LineGroup
            elif isinstance(group, QGraphicsLineGroup):

                anchorPoint = item.mapToScene(item.boundingRect().center() / scene.scaleFactor)

                #points of line
                startPoint_GLOBAL = group.points[0]
                endPoint_GLOBAL = group.points[1]
                #transformations for points (reverse motion)
                transform = QTransform()
                if startPoint_GLOBAL == item.points[0]:
                    
                    transform.translate(anchorPoint.x(), anchorPoint.y())
                    transform.scale(scaleX, scaleY)
                    transform.translate(anchorPoint.x() * -1, anchorPoint.y() * -1)
                
                elif endPoint_GLOBAL == item.points[0]:
                    
                    transform.translate(anchorPoint.x(), anchorPoint.y())
                    transform.scale(scaleX, scaleY)
                    transform.translate(anchorPoint.x() * -1, anchorPoint.y() * -1)

                #apply transformations
                startPoint = points[0]
                endPoint = points[1]
                startPoint = transform.map(startPoint_GLOBAL)
                endPoint = transform.map(endPoint_GLOBAL)
                self.points = [startPoint, endPoint]
                print(self.points)

        elif figure == Figures.LINE:
            
            #points of line
            startPoint_GLOBAL = points[0]
            endPoint_GLOBAL = points[1]
            centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()
            
            #transformations for points (reverse motion)
            transform = QTransform()
            transform.translate(centerPoint_GLOBAL.x(), centerPoint_GLOBAL.y())
            transform.scale(scaleX, scaleY)
            transform.translate(centerPoint_GLOBAL.x() * -1, centerPoint_GLOBAL.y() * -1)
            
            #apply transformations
            startPoint = transform.map(startPoint_GLOBAL)
            endPoint = transform.map(endPoint_GLOBAL)
            self.points = [startPoint, endPoint]
        
        elif figure == Figures.MIXED:
            
            mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(group, (QGraphicsMixedGroup))
            mixedGroups.append(group)
            anchorPoint = group.mapToScene(group.boundingRect().center() / scene.scaleFactor)

            for gr in mixedGroups:
                for item in gr.childItems():
                    if isinstance(item, QGraphicsLineGroup):

                        #points of line
                        startPoint_GLOBAL = item.points[0]
                        endPoint_GLOBAL = item.points[1]
                        centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()

                         #transformations for points (reverse motion)
                        transform = QTransform()
                        transform.translate(anchorPoint.x(), anchorPoint.y())
                        transform.scale(scaleX, scaleY)
                        transform.translate(anchorPoint.x() * -1, anchorPoint.y() * -1)

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
        self.accept()
    
                