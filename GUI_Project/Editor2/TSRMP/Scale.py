from EditorEnum import Figures
from CustomClasses import QGraphicsCustomItemGroup, QGraphicsMixedGroup, QGraphicsLineGroup, QGraphicsCustomScene, AdditionalMethods, QGraphicsCubeGroup
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
    QGraphicsEllipseItem,
    QCheckBox,
    QLabel
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class ScaleDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("ScaleDialog")
        self.setObjectName("ScaleDialog")
        self.setMinimumWidth(200)

        self.scene = scene
        self.figure = figure
        self.points: list[QPointF] = points
        self.item: QGraphicsCustomItemGroup = item
        self.groupItem: QGraphicsCustomItemGroup = groupItem
        self.scaleFactor = scaleFactor
        self.cube = None
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop); mainLayout.setSpacing(10)
        if figure == Figures.POINT or figure == Figures.LINE or figure == Figures.MIXED:
            #widgets
            scaler_X = QDoubleSpinBox(minimum=-10000, maximum=10000); scaler_X.setMinimumWidth(50); scaler_X.setMinimumHeight(35)
            scaler_Y = QDoubleSpinBox(minimum=-10000, maximum=10000); scaler_Y.setMinimumWidth(50); scaler_Y.setMinimumHeight(35)
            label_sX = QLabel("Scale x")
            label_sY = QLabel("Scale y")
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.scale(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, scaler_X.value(), scaler_Y.value(), 1))
            confirm_2D.setFixedHeight(35)
            #layout
            mainLayout.addWidget(label_sX)
            mainLayout.addWidget(scaler_X)
            mainLayout.addWidget(label_sY)
            mainLayout.addWidget(scaler_Y)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            scaler_X = QDoubleSpinBox(minimum=-10000, maximum=10000); scaler_X.setMinimumWidth(50); scaler_X.setMinimumHeight(35)
            scaler_Y = QDoubleSpinBox(minimum=-10000, maximum=10000); scaler_Y.setMinimumWidth(50); scaler_Y.setMinimumHeight(35)
            scaler_Z = QDoubleSpinBox(minimum=-10000, maximum=10000); scaler_Z.setMinimumWidth(50); scaler_Z.setMinimumHeight(35)
            label_sX = QLabel("Scale x")
            label_sY = QLabel("Scale y")
            label_sZ = QLabel("Scale z")
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.scale(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, scaler_X.value(), scaler_Y.value(), scaler_Z.value()))
            confirm_3D.setFixedHeight(35)
            #layout
            mainLayout.addWidget(label_sX)
            mainLayout.addWidget(scaler_X)
            mainLayout.addWidget(label_sY)
            mainLayout.addWidget(scaler_Y)
            mainLayout.addWidget(label_sZ)
            mainLayout.addWidget(scaler_Z)
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
        spinBox_stylesheet = (
            'QDoubleSpinBox {'
                'font-size: 16px;'
                'color: #632599;'
                'background-color: #DBB1FF;'
                'border: 0x solid #DBB1FF;'
                'border-radius: 2px;' \
                'padding-left: 5px;'
            '}'
            )
        styleSheet =  dialog_stylesheet + label_stylesheet + button_stylesheet + spinBox_stylesheet
        self.setStyleSheet(styleSheet)
        pass
    
    #Slots
    def scale(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, group: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor, scaleX, scaleY, scaleZ):
        
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
            
                if isinstance(gr, QGraphicsCubeGroup):

                    if gr.parentItem() != None:

                        parent = gr.parentItem()

                        old_cube: QGraphicsCubeGroup = gr
                        camZ = old_cube.camZ
                        scaleF = scaleFactor

                        new_cube = AdditionalMethods.createCustomCube(0, 0, 0, 1 * scaleX, 1 * scaleY, 1 * scaleZ, 0, 0, 0, camZ, scaleF, old_cube)
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
        
        elif figure == Figures.CUBE:

            old_cube: QGraphicsCubeGroup = item
            camZ = old_cube.camZ
            scaleF = scaleFactor

            new_cube = AdditionalMethods.createCustomCube(0, 0, 0, 1 * scaleX, 1 * scaleY, 1 * scaleZ, 0, 0, 0, camZ, scaleF, old_cube)
            self.cube = new_cube
        self.accept()
    
                