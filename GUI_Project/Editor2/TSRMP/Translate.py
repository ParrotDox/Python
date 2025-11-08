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
    QGraphicsLineItem,
    QGraphicsItemGroup,
    QGraphicsScene
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class TranslateDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("TranslateDialog")
        self.setObjectName("TranslateDialog")

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
            translator_X = QSpinBox(minimum=-10000, maximum=10000)
            translator_Y = QSpinBox(minimum=-10000, maximum=10000)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.translate(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, translator_X.value(), translator_Y.value(), 0))
            
            #layout
            mainLayout.addWidget(translator_X)
            mainLayout.addWidget(translator_Y)
            
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            
            #widgets
            translator_X = QSpinBox(minimum=-10000, maximum=10000)
            translator_Y = QSpinBox(minimum=-10000, maximum=10000)
            translator_Z = QSpinBox(minimum=-10000, maximum=10000)
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.translate(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, translator_X.value(), translator_Y.value(), translator_Z.value()))
            
            #layout
            mainLayout.addWidget(translator_X)
            mainLayout.addWidget(translator_Y)
            mainLayout.addWidget(translator_Z)
            mainLayout.addWidget(confirm_3D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def translate(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor, translationX, translationY, translationZ):
        
        if figure == Figures.POINT:

            #points of line
            startPoint_GLOBAL = points[0]
            endPoint_GLOBAL = points[1]
            
            #transformations for points (reverse motion)
            transform = QTransform()
            transform.translate(translationX, translationY)
            
            #apply transformations
            startPoint = points[0]
            endPoint = points[1]
            
            if startPoint_GLOBAL == item.points[0]:
                startPoint = transform.map(startPoint_GLOBAL)
            elif endPoint_GLOBAL == item.points[0]:
                endPoint = transform.map(endPoint_GLOBAL)
            
            self.points = [startPoint, endPoint]

        elif figure == Figures.LINE:

            #points of line
            startPoint_GLOBAL = points[0]
            endPoint_GLOBAL = points[1]
            centerPoint_GLOBAL = QLineF(startPoint_GLOBAL, endPoint_GLOBAL).center()
            
            #transformations for points (reverse motion)
            transform = QTransform()
            transform.translate(translationX, translationY)
            
            #apply transformations
            startPoint = transform.map(startPoint_GLOBAL)
            endPoint = transform.map(endPoint_GLOBAL)
            
            self.points = [startPoint, endPoint]

        elif figure == Figures.MIXED:
            
            mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(group, (QGraphicsMixedGroup, QGraphicsCubeGroup))
            mixedGroups.append(group)

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

                        new_cube = AdditionalMethods.createCustomCube(tX + translationX, tY + translationY, tZ + translationZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleF)
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
                        transform.translate(translationX, translationY)

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

            new_cube = AdditionalMethods.createCustomCube(tX + translationX, tY + translationY, tZ + translationZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleF)
            self.cube = new_cube
        
        self.accept()