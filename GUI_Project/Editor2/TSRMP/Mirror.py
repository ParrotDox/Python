from EditorEnum import Figures
from CustomClasses import QGraphicsCustomItemGroup, QGraphicsMixedGroup, QGraphicsLineGroup, QGraphicsCustomScene
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
    QGraphicsMixedGroup,
    AdditionalMethods)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class MirrorDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("MirrorDialog")
        self.setObjectName("MirrorDialog")
        self.setMinimumWidth(200)

        self.scene = scene
        self.figure = figure
        self.points: list[QPointF] = points
        self.item: QGraphicsCustomItemGroup = item
        self.groupItem: QGraphicsCustomItemGroup = groupItem
        self.scaleFactor = scaleFactor
        self.cube = None
    
    def initUI(self, figure):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.POINT or figure == Figures.LINE or figure == Figures.MIXED:
            #widgets
            mirrorer_X = QCheckBox("Mirror X"); mirrorer_X.setMinimumWidth(25)
            mirrorer_Y = QCheckBox("Mirror Y"); mirrorer_X.setMinimumWidth(25)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.mirror(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, mirrorer_X.isChecked(), mirrorer_Y.isChecked(), False))
            confirm_2D.setFixedHeight(35)
            #layout
            mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
            mainLayout.addWidget(mirrorer_X)
            mainLayout.addWidget(mirrorer_Y)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            mirrorer_X = QCheckBox("Mirror X")
            mirrorer_Y = QCheckBox("Mirror Y")
            mirrorer_Z = QCheckBox("Mirror Z")
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.mirror(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, mirrorer_X.isChecked(), mirrorer_Y.isChecked(), mirrorer_Z.isChecked()))
            confirm_3D.setFixedHeight(35)
            #layout
            mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
            mainLayout.addWidget(mirrorer_X)
            mainLayout.addWidget(mirrorer_Y)
            mainLayout.addWidget(mirrorer_Z)
            mainLayout.addWidget(confirm_3D)
        self.setLayout(mainLayout)
        #StyleSheets
        dialog_stylesheet = (
            'QDialog {'
            'background-color: #FFFFFF;'
            '}'
        )
        label_stylesheet = (
            'QLabel {'
            'color: #132238;'
            'font-family: "Work Sans";'
            'font-size: 18px;' 
            '}'
        )
        button_stylesheet = (
            'QPushButton {'
            'background-color: #EEEEEE;'
            'color: #132238;'
            'border-radius: 12px;'
            'font-family: "Work Sans";'
            'font-size: 12px;' 
            'font-weight: bold;'
            '}'
            
            'QPushButton:hover {'
            'background-color: #A53DFF;'
            'color: #FFFFFF;'
            'font-size: 16px;}'
            'QPushButton:pressed {'
            'background-color: #632599;'
            'color: #FFFFFF;'
            'font-size: 16px;}'

            'QPushButton:checked {'
            'background-color: #DBB1FF;'
            'color: #FFFFFF;'
            'font-size: 16px;}'
        )
        checkBox_stylesheet = (
            'QCheckBox {'
                'color: #132238;'
                'font-family: "Work Sans";'
                'font-size: 16px;'
                'spacing: 8px;'
            '}'

            'QCheckBox::indicator {'
                'border: 2px solid #632599;'
                'border-radius: 3px;'
                'background-color: #DBB1FF;'
            '}'

            'QCheckBox::indicator:checked {'
                'background-color: #632599;'
                'border: 2px solid #632599;'
            '}'
        )
        styleSheet =  dialog_stylesheet + label_stylesheet + button_stylesheet + checkBox_stylesheet
        self.setStyleSheet(styleSheet)
        pass
    
    #Slots
    def mirror(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor, mirrorX, mirrorY, mirrorZ):
        if (mirrorX or mirrorY or mirrorZ) == False:
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
                
                if isinstance(gr, QGraphicsCubeGroup):

                    if gr.parentItem() != None:

                        parent = gr.parentItem()

                        old_cube: QGraphicsCubeGroup = gr
                        tX = old_cube.tX
                        tY = old_cube.tY
                        tZ = old_cube.tZ
                        sX = old_cube.sX
                        sY = old_cube.sY
                        sZ = old_cube.sZ
                        if mirrorX:
                            sX = sX * -1
                        if mirrorY:
                            sY = sY * -1
                        if mirrorZ:
                            sZ = sZ * -1
                        rX = old_cube.rX
                        rY = old_cube.rY
                        rZ = old_cube.rZ
                        camZ = old_cube.camZ
                        scaleF = scaleFactor

                        new_cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleF)
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

            old_cube: QGraphicsCubeGroup = item
            tX = old_cube.tX
            tY = old_cube.tY
            tZ = old_cube.tZ
            sX = old_cube.sX
            sY = old_cube.sY
            sZ = old_cube.sZ
            if mirrorX:
                sX = sX * -1
            if mirrorY:
                sY = sY * -1
            if mirrorZ:
                sZ = sZ * -1
            rX = old_cube.rX
            rY = old_cube.rY
            rZ = old_cube.rZ
            camZ = old_cube.camZ
            scaleF = scaleFactor

            new_cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleF)
            self.cube = new_cube
        self.accept()
    
                