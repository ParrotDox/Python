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
    QGraphicsLineItem,
    QGraphicsItemGroup,
    QGraphicsScene,
    QLabel
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class TranslateDialog(QDialog, AdditionalMethods):

    def __init__(self, scene: QGraphicsCustomScene, figure: Figures, item: QGraphicsCustomItemGroup, groupItem: QGraphicsCustomItemGroup, points: list[QPointF], scaleFactor):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("TranslateDialog")
        self.setObjectName("TranslateDialog")
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
            translator_X = QDoubleSpinBox(minimum=-10000, maximum=10000); translator_X.setMinimumWidth(50); translator_X.setMinimumHeight(35)
            translator_Y = QDoubleSpinBox(minimum=-10000, maximum=10000); translator_Y.setMinimumWidth(50); translator_Y.setMinimumHeight(35)
            label_tX = QLabel("Translate x")
            label_tY = QLabel("Translate y")
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.translate(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, translator_X.value(), translator_Y.value(), 0))
            confirm_2D.setFixedHeight(35)
            
            #layout
            mainLayout.addWidget(label_tX)
            mainLayout.addWidget(translator_X)
            mainLayout.addWidget(label_tY)
            mainLayout.addWidget(translator_Y)
            
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            
            #widgets
            translator_X = QDoubleSpinBox(minimum=-10000, maximum=10000); translator_X.setMinimumWidth(50); translator_X.setMinimumHeight(35)
            translator_Y = QDoubleSpinBox(minimum=-10000, maximum=10000); translator_Y.setMinimumWidth(50); translator_Y.setMinimumHeight(35)
            translator_Z = QDoubleSpinBox(minimum=-10000, maximum=10000); translator_Z.setMinimumWidth(50); translator_Z.setMinimumHeight(35)
            label_tX = QLabel("Translate x")
            label_tY = QLabel("Translate y")
            label_tZ = QLabel("Translate z")
            confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.translate(self.scene, self.figure, self.item, self.groupItem, self.points, self.scaleFactor, translator_X.value(), translator_Y.value(), translator_Z.value()))
            confirm_3D.setFixedHeight(35)
            #layout
            mainLayout.addWidget(label_tX)
            mainLayout.addWidget(translator_X)
            mainLayout.addWidget(label_tY)
            mainLayout.addWidget(translator_Y)
            mainLayout.addWidget(label_tZ)
            mainLayout.addWidget(translator_Z)
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

                    if gr.parentItem() != None:

                        parent = gr.parentItem()

                        old_cube: QGraphicsCubeGroup = gr
                        camZ = old_cube.camZ
                        scaleF = scaleFactor

                        new_cube = AdditionalMethods.createCustomCube(translationX, translationY, translationZ, 1, 1, 1, 0, 0, 0, camZ, scaleF, old_cube)
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
            camZ = old_cube.camZ
            scaleF = scaleFactor

            new_cube = AdditionalMethods.createCustomCube(translationX, translationY, translationZ, 1, 1, 1, 0, 0, 0, camZ, scaleF, old_cube)
            self.cube = new_cube
        
        self.accept()