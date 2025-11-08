from EditorEnum import Figures
from CustomClasses import QGraphicsCustomItemGroup, QGraphicsMixedGroup, QGraphicsLineGroup, QGraphicsCustomScene, AdditionalMethods, QGraphicsCubeGroup
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

class RotateDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("RotateDialog")
        self.setObjectName("RotateDialog")

        self.scene = scene
        self.figure = figure
        self.points: list[QPointF] = points
        self.item: QGraphicsCustomItemGroup = item
        self.groupItem: QGraphicsCustomItemGroup = groupItem
        self.scaleFactor = scaleFactor
        self.cube = None
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.POINT or figure == Figures.LINE or figure == Figures.MIXED:
            #widgets
            rotator = QSpinBox(minimum=-360, maximum=360)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.rotate(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, rotator.value(), 0, 0))
            #layout
            mainLayout.addWidget(rotator)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            rotatorX = QSpinBox(minimum=-360, maximum=360)
            rotatorY = QSpinBox(minimum=-360, maximum=360)
            rotatorZ = QSpinBox(minimum=-360, maximum=360)
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.rotate(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, rotatorX.value(), rotatorY.value(), rotatorZ.value()))
            #layout
            mainLayout.addWidget(rotatorX)
            mainLayout.addWidget(rotatorY)
            mainLayout.addWidget(rotatorZ)
            mainLayout.addWidget(confirm_3D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def rotate(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor, rotateX, rotateY, rotateZ):
        
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
                            transform.rotate(rotateX)
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
                    transform.rotate(rotateX)
                    transform.translate(anchorPoint.x() * -1, anchorPoint.y() * -1)
                
                elif endPoint_GLOBAL == item.points[0]:
                    
                    transform.translate(anchorPoint.x(), anchorPoint.y())
                    transform.rotate(rotateX)
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
            transform.rotate(rotateX)
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
                
                if isinstance(gr, QGraphicsCubeGroup):

                    if gr.parentItem != None:

                        parent = gr.parentItem()

                        old_cube: QGraphicsCubeGroup = gr
                        tX = old_cube.tX
                        tY = old_cube.tY
                        tZ = old_cube.tZ
                        sX = old_cube.sX
                        sY = old_cube.sY
                        sZ = old_cube.sZ
                        rX = old_cube.rX
                        rY = old_cube.rY
                        rZ = old_cube.rZ
                        camZ = old_cube.camZ
                        scaleF = scaleFactor

                        new_cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX + rotateX, rY + rotateY, rZ + rotateZ, camZ, scaleF)
                        self.cube = new_cube

                        #replace old cube by new cube
                        parent.removeFromGroup(old_cube)
                        scene.removeItem(old_cube)
                        parent.addToGroup(new_cube)

                for item in gr.childItems():
                    
                    if isinstance(item, QGraphicsLineGroup):

                        #points of line
                        startPoint_GLOBAL = item.points[0]
                        endPoint_GLOBAL = item.points[1]
                        centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()

                         #transformations for points (reverse motion)
                        transform = QTransform()
                        transform.translate(anchorPoint.x(), anchorPoint.y())
                        transform.rotate(rotateX)
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
        
        elif figure == Figures.CUBE:

            old_cube: QGraphicsCubeGroup = item
            tX = old_cube.tX
            tY = old_cube.tY
            tZ = old_cube.tZ
            sX = old_cube.sX
            sY = old_cube.sY
            sZ = old_cube.sZ
            rX = old_cube.rX
            rY = old_cube.rY
            rZ = old_cube.rZ
            camZ = old_cube.camZ
            scaleF = scaleFactor

            new_cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX + rotateX, rY + rotateY, rZ + rotateZ, camZ, scaleF)
            self.cube = new_cube

        self.accept()