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
    QGraphicsEllipseItem,
    QRadioButton
)
from CustomClasses import (
    QGraphicsLineGroup, 
    QGraphicsCubeGroup, 
    QGraphicsPointGroup,
    QGraphicsMixedGroup,
    AdditionalMethods)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class ProjectionDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("ProjectionDialog")
        self.setObjectName("ProjectionDialog")
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
        if figure == Figures.POINT or figure == Figures.LINE:
            #widgets
            projectedXZ = QRadioButton("Project to XZ")
            projectedYZ = QRadioButton("Project to YZ")
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.project(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, projectedXZ.isChecked(), projectedYZ.isChecked(), False))
            confirm_2D.setFixedHeight(35)
            #layout
            mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
            mainLayout.addWidget(projectedXZ)
            mainLayout.addWidget(projectedYZ)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE or figure == Figures.MIXED:
            #widgets
            projectedXZ = QRadioButton("Project to XZ")
            projectedYZ = QRadioButton("Project to YZ")
            projectedXY = QRadioButton("Project to XY")
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.project(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, projectedXZ.isChecked(), projectedYZ.isChecked(), projectedXY.isChecked()))
            confirm_3D.setFixedHeight(35)
            #layout
            mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
            mainLayout.addWidget(projectedXZ)
            mainLayout.addWidget(projectedYZ)
            mainLayout.addWidget(projectedXY)
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
        radioButton_stylesheet = (
            'QRadioButton {'
                'color: #132238;'
                'font-family: "Work Sans";'
                'font-size: 16px;'
                'spacing: 8px;'
            '}'

            'QRadioButton::indicator {'
                'border: 2px solid #632599;'
                'border-radius: 3px;'
                'background-color: #DBB1FF;'
            '}'

            'QRadioButton::indicator:checked {'
                'background-color: #632599;'
                'border: 2px solid #632599;'
            '}'
        )
        styleSheet =  dialog_stylesheet + label_stylesheet + button_stylesheet + radioButton_stylesheet
        self.setStyleSheet(styleSheet)
        pass
    
    #Slots
    def project(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor, projectedXZ, projectedYZ, projectedXY):
        
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
                        if projectedXZ:
                            sY = sX * 0
                        if projectedYZ:
                            sX = sX * 0
                        if projectedXY:
                            sZ = sZ * 0
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
            old_cube: QGraphicsCubeGroup = item
            tX = old_cube.tX
            tY = old_cube.tY
            tZ = old_cube.tZ
            sX = old_cube.sX
            sY = old_cube.sY
            sZ = old_cube.sZ
            if projectedXZ:
                sY = sX * 0
            if projectedYZ:
                sX = sX * 0
            if projectedXY:
                sZ = sZ * 0
            rX = old_cube.rX
            rY = old_cube.rY
            rZ = old_cube.rZ
            camZ = old_cube.camZ
            scaleF = scaleFactor

            new_cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleF)
            self.cube = new_cube
        self.accept()
    
                