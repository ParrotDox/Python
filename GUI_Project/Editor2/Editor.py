import os
from CUD.Create import CreateDialog
from CUD.Update import UpdateDialog
from TSRMP.Translate import TranslateDialog
from TSRMP.Scale import ScaleDialog
from TSRMP.Rotate import RotateDialog
from TSRMP.Mirror import MirrorDialog
from TSRMP.Projection import ProjectionDialog
from EditorEnum import Figures, SelectModes
from CustomClasses import (
    QGraphicsCustomScene,
    QOneWayToggleButton,
    QGraphicsCustomItemGroup,
    QGraphicsLineGroup, 
    QGraphicsCubeGroup, 
    QGraphicsPointGroup,
    QGraphicsMixedGroup, 
    QGraphicsCustomView,
    AdditionalMethods)
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsEllipseItem,
    QGraphicsItemGroup
)
from PySide6.QtCore import Qt, QLineF, QPointF, QPoint, QRect
from PySide6.QtGui import QPen, QBrush, QColor, QIcon, QPixmap

class EditorWidget(QWidget):

    def __init__(self):
        super().__init__()

        #SelectMode
        self.selectMode: SelectModes = SelectModes.LINE

        #Colors
        self.defaultPen: QPen       = None
        self.defaultBrush: QBrush   = None
        self.focusedPen: QPen       = None
        self.focusedBrush: QBrush   = None
        self.preparedPen:QPen       = None
        self.preparedBrush: QBrush  = None
        self.crossPen: QPen         = None
        self.crossBrush: QBrush     = None
        self.gridPen: QPen          = None
        self.gridBrush: QBrush      = None
        self.initColors()

        #Current selection
        self.currentGroup: QGraphicsCustomItemGroup = None
        self.currentItem: QGraphicsItem = None #Can be point or group

        #Prepared items to group
        self.preparedGroups: list[QGraphicsCustomItemGroup] = []

        #Groups to prevent deletion
        self.groups = []

        #Current scale
        self.scaleFactor = 50

        #Toggle buttons
        self.selectModeButtons = []
        self.initUI()
        self.setWindowTitle("Editor"); self.setFixedSize(1280, 720)
        self.setObjectName("Editor")
 
    def initUI(self):
        #widgets
        buttonCreate = QPushButton("C"); buttonCreate.setFixedSize(45,45); buttonCreate.clicked.connect(lambda: self.openCreateDialog(scene, library))
        buttonUpdate = QPushButton("U"); buttonUpdate.setFixedSize(45,45); buttonUpdate.clicked.connect(lambda: self.openUpdateDialog(scene, library))
        buttonDelete = QPushButton("D"); buttonDelete.setFixedSize(45,45); buttonDelete.clicked.connect(lambda: self.deleteCurrentItem(scene, library))

        buttonTranslate = QPushButton("T"); buttonTranslate.setFixedSize(45,45); buttonTranslate.clicked.connect(lambda: self.openTranslateDialog(scene, library))
        buttonScale = QPushButton("S"); buttonScale.setFixedSize(45,45); buttonScale.clicked.connect(lambda: self.openScaleDialog(scene, library))
        buttonRotate = QPushButton("R"); buttonRotate.setFixedSize(45,45); buttonRotate.clicked.connect(lambda: self.openRotateDialog(scene, library))
        buttonMirror = QPushButton("M"); buttonMirror.setFixedSize(45,45); buttonMirror.clicked.connect(lambda: self.openMirrorDialog(scene, library))
        buttonProjection = QPushButton("P"); buttonProjection.setFixedSize(45,45); buttonProjection.clicked.connect(lambda: self.openProjectionDialog(scene, library))

        buttonPoint = QOneWayToggleButton(self.createIcon("Icons/point.png", 45, 45), ""); buttonPoint.setFixedSize(45,45); buttonPoint.clicked.connect(lambda:self.setSelectMode(self.selectModeButtons, SelectModes.POINT)); buttonPoint.setCheckable(True); buttonPoint.setChecked(False)
        buttonLine = QOneWayToggleButton(self.createIcon("Icons/line.png", 45, 45), ""); buttonLine.setFixedSize(45,45); buttonLine.clicked.connect(lambda:self.setSelectMode(self.selectModeButtons, SelectModes.LINE)); buttonLine.setCheckable(True); buttonLine.setChecked(True)
        buttonMixed = QOneWayToggleButton(self.createIcon("Icons/group.png", 45, 45), ""); buttonMixed.setFixedSize(45,45); buttonMixed.clicked.connect(lambda:self.setSelectMode(self.selectModeButtons, SelectModes.MIXED)); buttonMixed.setCheckable(True); buttonMixed.setChecked(False)
        self.selectModeButtons.extend([buttonPoint, buttonLine, buttonMixed])

        buttonGroup = QPushButton(self.createIcon("Icons/pack.png", 45, 45), ""); buttonGroup.setFixedSize(45,45); buttonGroup.clicked.connect(lambda: self.groupPreparedItems(scene, library))
        buttonUngroup = QPushButton(self.createIcon("Icons/unpack.png", 45, 45), ""); buttonUngroup.setFixedSize(45,45); buttonUngroup.clicked.connect(lambda: self.ungroup(scene, library, self.currentGroup))

        scene = QGraphicsCustomScene(QRect(-1000*self.scaleFactor,-1000*self.scaleFactor,2000*self.scaleFactor,2000*self.scaleFactor), self.scaleFactor, self.gridPen, self.crossPen)
        view = QGraphicsCustomView(scene); view.scale(1, -1)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.itemFocused.connect(lambda scene, filteredGroups, point: self.setCurrentItemByCSM(scene, library, filteredGroups, point))
        view.itemFocusedToGroup.connect(lambda scene, filteredGroups, point: self.prepareToGroup(scene, library, filteredGroups, point))
        view.itemMoved.connect(lambda leftMousePos, delta: self.moveItemsAtScene(scene, library, view, leftMousePos, delta))
        view.scaleFactorChanged.connect(lambda deltaY: self.redrawEverything(scene, library, self.scaleFactor, deltaY, self.gridPen, self.crossPen))
        
        objectsLabel = QLabel("Objects")
        library = QListWidget(); library.itemClicked.connect(lambda item: self.setCurrentItemByLibrary(scene, library, item))

        #layouts
        mainLayout = QHBoxLayout()

        workspaceLayout = QVBoxLayout()
        libraryLayout = QHBoxLayout()

        actionsLayout = QHBoxLayout(); actionsLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        cudLayout = QHBoxLayout()
        tsrmpLayout = QHBoxLayout()
        selectModeLayout = QHBoxLayout()
        groupLayout = QHBoxLayout()

        objectsLayout = QVBoxLayout()

        mainLayout.addLayout(workspaceLayout); mainLayout.addLayout(libraryLayout)
        mainLayout.setStretchFactor(workspaceLayout, 3); mainLayout.setStretchFactor(libraryLayout, 1)

        actionsLayout.setContentsMargins(10, 10, 10, 10)
        actionsLayout.addLayout(cudLayout); actionsLayout.addSpacing(15)
        actionsLayout.addLayout(tsrmpLayout); actionsLayout.addSpacing(15)
        actionsLayout.addLayout(selectModeLayout); actionsLayout.addSpacing(15)
        actionsLayout.addLayout(groupLayout)

        libraryLayout.addLayout(objectsLayout)

        cudLayout.addWidget(buttonCreate); cudLayout.addWidget(buttonUpdate); cudLayout.addWidget(buttonDelete);
        tsrmpLayout.addWidget(buttonTranslate); tsrmpLayout.addWidget(buttonScale); tsrmpLayout.addWidget(buttonRotate); tsrmpLayout.addWidget(buttonMirror); tsrmpLayout.addWidget(buttonProjection)
        selectModeLayout.addWidget(buttonPoint); selectModeLayout.addWidget(buttonLine); selectModeLayout.addWidget(buttonMixed)
        groupLayout.addWidget(buttonGroup); groupLayout.addWidget(buttonUngroup)

        workspaceLayout.setContentsMargins(10, 0, 30, 0)
        workspaceLayout.addLayout(actionsLayout); workspaceLayout.addWidget(view)

        objectsLayout.addWidget(objectsLabel); objectsLayout.addWidget(library)

        self.setLayout(mainLayout)


        #StyleSheets
        editor_stylesheet = (
            'QWidget#Editor {'
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
        view_stylesheet = (
            'QGraphicsView {'
            'border: 5px solid #EEEEEE;'
            'border-radius: 5px;'
            '}'
        )
        library_stylesheet = (
            'QListWidget {'
            'background-color: #EEEEEE;'
            'border: 5px solid #EEEEEE;'
            'font-family: "Work Sans";'
            'border-radius: 8px'
            '}'
            'QListWidget::item {'
            'background-color: #FFFFFF;'
            'padding: 10px 15px;'
            'margin: 0px 0px 5px 0px;'
            'font-size: 16px;'
            'border-radius: 5px;'
            '}'
            'QListWidget::item:hover {'
            'background-color: #A53DFF;'
            'padding: 10px 15px;'
            '}'
            'QListWidget::item:selected {'
            'background-color: #DBB1FF;'
            'color: #132238;'
            'padding: 10px 15px;'
            '}'
        )
        styleSheet = (editor_stylesheet + label_stylesheet 
                      + button_stylesheet + view_stylesheet
                      + library_stylesheet)
        
        self.setStyleSheet(styleSheet)
        pass
    #Colors
    def initColors(self):
        self.defaultPen = QPen(); self.defaultBrush = QBrush()
        self.focusedPen = QPen(); self.focusedBrush = QBrush()
        self.preparedPen = QPen(); self.preparedBrush = QBrush()
        self.gridPen = QPen(); self.gridBrush = QBrush()
        self.crossPen = QPen(); self.crossBrush = QBrush()

        self.defaultPen.setColor(QColor(19, 34, 56))
        self.defaultPen.setWidth(2)
        self.defaultPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.defaultBrush.setColor(QColor(19, 34, 56))

        self.focusedPen.setColor(QColor(165, 61, 255))
        self.focusedPen.setWidth(3)
        self.focusedPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.focusedBrush.setColor(QColor(165, 61, 255))

        self.preparedPen.setColor(QColor(0, 195, 208))
        self.preparedPen.setWidth(3)
        self.preparedPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.preparedBrush.setColor(QColor(0, 195, 208))

        self.gridPen.setColor(QColor(19, 34, 56))
        self.gridPen.setWidth(1)
        self.gridPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.gridBrush.setColor(QColor(19, 34, 56))

        self.crossPen.setColor(QColor(19, 34, 56))
        self.crossPen.setWidth(4)
        self.crossPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.crossBrush.setColor(QColor(19, 34, 56))
    def paintItem(self, item: QGraphicsItem, pen: QPen, brush: QBrush):
        items: list[QGraphicsItem] = self.getAllBaseChildItems(item)
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                ellipse: QGraphicsEllipseItem = it
                ellipse.setBrush(brush)
                ellipse.setPen(pen)
            elif isinstance(it, QGraphicsLineItem):
                line: QGraphicsLineItem = it
                line.setPen(pen)
    #Icons
    def createIcon(self, picPath: str, w: int, h: int):
        absPath = os.path.dirname(os.path.abspath(__file__))
        iconPath = os.path.join(absPath, *picPath.split("/"))
        pixmap = QPixmap(iconPath); pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon = QIcon(pixmap)
        return icon
    #Dialogs
    def openCreateDialog(self, scene: QGraphicsScene, library: QListWidget):
        dialog = CreateDialog(self.scaleFactor)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            if dialog.figure == Figures.LINE:
                
                '''Add everywhere'''
                points: list[QPointF] = dialog.points
                newLine = AdditionalMethods.createCustomLine(points, self.scaleFactor) #line is a group!
                self.addItemEverywhere(scene, library, newLine, points)

            elif dialog.figure == Figures.CUBE:
                '''Add everywhere'''
                cube: QGraphicsCubeGroup = dialog.cube
                points = dialog.points
                self.addItemEverywhere(scene, library, cube, points)
        else:
            return
    def openUpdateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentItem == None:
            return
        
        figureType = AdditionalMethods.whatFigure(self.currentItem)
        parent: QGraphicsCustomItemGroup = self.currentItem.parentItem()
        dialog: UpdateDialog = None

        '''Send appropriate arguments depended on selectionMode'''
        '''Seek Mixed group'''
        if figureType == Figures.POINT:

            #Point can't exist without a parent line
            if parent != None:
                
                parent = parent.parentItem() #Got QMixedGroup
            
            dialog = UpdateDialog(Figures.LINE, parent, self.scaleFactor)

        elif figureType == Figures.LINE:

            dialog = UpdateDialog(Figures.LINE, self.currentItem, self.scaleFactor)

        elif figureType == Figures.MIXED:

            return
        
        elif figureType == Figures.CUBE:

            dialog = UpdateDialog(Figures.CUBE, self.currentItem, self.scaleFactor)
        
        result = dialog.exec()
        
        '''Update item'''
        if result == QDialog.DialogCode.Accepted and (figureType in [Figures.POINT, Figures.LINE]):

            new_points: list[QPointF] = dialog.points
            newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

            if parent != None and isinstance(parent, QGraphicsMixedGroup):
                
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemInScene(scene, self.currentItem.parentItem(), newItem)
                
                elif figureType == Figures.LINE:
                    
                    self.replaceItemInScene(scene, self.currentItem, newItem)
                
                '''Replace old line by new in group'''
                if figureType == Figures.POINT:
                    
                    parent.removeFromGroup(self.currentItem.parentItem())
                
                elif figureType == Figures.LINE:
                    
                    parent.removeFromGroup(self.currentItem)
                
                parent.addToGroup(newItem)
                self.currentItem = None
                self.currentGroup = None

            else:
                #replace item everywhere
                self.replaceItemEverywhere(scene, library, self.currentGroup, newItem, new_points)
  
        if result == QDialog.DialogCode.Accepted and figureType == Figures.CUBE:
            
            cube: QGraphicsCubeGroup = dialog.cube
            new_points: list[QPointF] = cube.points

            if parent != None and isinstance(parent, QGraphicsCubeGroup):

                scene.removeItem(self.currentItem)
                parent.removeFromGroup(self.currentItem)
                parent.addToGroup(cube)
            
            else:

                self.replaceItemEverywhere(scene, library, self.currentItem, cube, new_points)

            self.currentItem = None
            self.currentGroup = None
            pass       
    def openTranslateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentItem == None:
            return
        
        figureType = AdditionalMethods.whatFigure(self.currentItem)
        parent: QGraphicsCustomItemGroup = self.currentItem.parentItem()
        dialog: TranslateDialog = None

        '''Send appropriate arguments depended on selectionMode'''
        '''Seek Mixed group'''
        if figureType == Figures.POINT:

            dialog = TranslateDialog(scene, Figures.POINT, self.currentItem, self.currentGroup, parent.points, self.scaleFactor)
            #Point can't exist without a parent line
            if parent.parentItem() != None:
                parent = parent.parentItem() #Got QMixedGroup

        elif figureType == Figures.LINE:

            dialog = TranslateDialog(scene, Figures.LINE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        elif figureType == Figures.MIXED:

            dialog = TranslateDialog(scene, Figures.MIXED, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)
        
        elif figureType == Figures.CUBE:

            dialog = TranslateDialog(scene, Figures.CUBE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)
        
        result = dialog.exec()


        '''Translate'''
        if result == QDialog.DialogCode.Accepted and (figureType in [Figures.POINT, Figures.LINE]):
            
            oldLine = self.currentItem.parentItem()
            new_points: list[QPointF] = dialog.points
            newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)
            
            if parent != None and isinstance(parent, QGraphicsMixedGroup):
                '''Replace old line by new at scene'''
                '''Replace old line by new in group'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemInScene(scene, self.currentItem.parentItem(), newItem)
                    parent.removeFromGroup(oldLine)

                elif figureType == Figures.LINE:
                    
                    self.replaceItemInScene(scene, self.currentItem, newItem)
                    parent.removeFromGroup(self.currentItem)
                
                parent.addToGroup(newItem)
                self.currentItem = None
                self.currentGroup = None

            else:
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)
                elif figureType == Figures.LINE:
                    self.replaceItemEverywhere(scene, library, self.currentItem, newItem, newItem.points)
                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.MIXED:
            
            '''Replace old group by new at scene'''
            #Get new group (In dialog old lines were removed from scene)
            newGroup = dialog.item
            #Update group in library
            self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)
            self.currentItem = None
            self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.CUBE:
            
            old_cube = self.currentItem
            new_cube = dialog.cube
            points = new_cube.points
            
            self.replaceItemEverywhere(scene, library, old_cube, new_cube, points)
            self.currentItem = None
            self.currentGroup = None
    def openScaleDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentItem == None:
            return
        
        figureType = AdditionalMethods.whatFigure(self.currentItem)
        parent: QGraphicsCustomItemGroup = self.currentItem.parentItem()
        dialog: TranslateDialog = None

        '''Send appropriate arguments depended on selectionMode'''
        '''Seek Mixed group'''
        if figureType == Figures.POINT:

            dialog = ScaleDialog(scene, Figures.POINT, self.currentItem, self.currentGroup, parent.points, self.scaleFactor)
            #Point can't exist without a parent line
            if parent.parentItem() != None:
                parent = parent.parentItem() #Got QMixedGroup
            
            #If has 3D -> prevent scaling

            mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(self.currentGroup, (QGraphicsMixedGroup))
            mixedGroups.append(self.currentGroup)

            for gr in mixedGroups:

                for item in gr.childItems():

                    if isinstance(item, QGraphicsCubeGroup):

                        return
                    
        elif figureType == Figures.LINE:

            dialog = ScaleDialog(scene, Figures.LINE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

            
                    
        elif figureType == Figures.MIXED:

            dialog = ScaleDialog(scene, Figures.MIXED, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

            
        elif figureType == Figures.CUBE:

            dialog = ScaleDialog(scene, Figures.CUBE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        result = dialog.exec()


        '''Scale'''
        if result == QDialog.DialogCode.Accepted and figureType == Figures.POINT:
            
            #Two variants: or it is a [independed item] or an [item with parent mixedgroup]
            if isinstance(self.currentGroup, QGraphicsMixedGroup):

                '''Replace old group by new at scene'''
                #Get new group (In dialog old lines were removed from scene)
                newGroup = dialog.item
                #Update group everywhere
                self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)
                self.currentItem = None
                self.currentGroup = None

            elif isinstance(self.currentGroup, QGraphicsLineGroup):
                
                oldLine = self.currentItem.parentItem()
                new_points: list[QPointF] = dialog.points
                newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)

                elif figureType == Figures.LINE:

                    self.replaceItemInLibrary(scene, library, self.currentItem, newItem, newItem.points)
                
                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.LINE:
            
            new_points: list[QPointF] = dialog.points
            newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

            if parent != None and isinstance(parent, QGraphicsMixedGroup):
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemInScene(scene, self.currentItem.parentItem(), newItem)
                
                elif figureType == Figures.LINE:
                    
                    self.replaceItemInScene(scene, self.currentItem, newItem)
                
                '''Replace old line by new in group'''
                if figureType == Figures.POINT:
                    
                    parent.removeFromGroup(self.currentItem.parentItem())
                
                elif figureType == Figures.LINE:
                    
                    parent.removeFromGroup(self.currentItem)
                
                parent.addToGroup(newItem)
                self.currentItem = None
                self.currentGroup = None

            else:
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)
                elif figureType == Figures.LINE:
                    self.replaceItemEverywhere(scene, library, self.currentItem, newItem, newItem.points)
                
                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.MIXED:
            
            '''Replace old group by new at scene'''
            #Get new group (In dialog old lines were removed from scene)
            newGroup = dialog.item
            #Update group in library
            self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)
            
            self.currentItem = None
            self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.CUBE:
            
            old_cube = self.currentItem
            new_cube = dialog.cube
            points = new_cube.points

            self.replaceItemEverywhere(scene, library, old_cube, new_cube, points)

            self.currentItem = None
            self.currentGroup = None
    def openRotateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentItem == None:
            return
        
        figureType = AdditionalMethods.whatFigure(self.currentItem)
        parent: QGraphicsCustomItemGroup = self.currentItem.parentItem()
        dialog: TranslateDialog = None

        '''Send appropriate arguments depended on selectionMode'''
        '''Seek Mixed group'''
        if figureType == Figures.POINT:
            
            dialog = RotateDialog(scene, Figures.POINT, self.currentItem, self.currentGroup, parent.points, self.scaleFactor)
            #Point can't exist without a parent line
            if parent.parentItem() != None:
                parent = parent.parentItem() #Got QMixedGroup
            
            #If has 3D -> prevent rotation

            mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(self.currentGroup, (QGraphicsMixedGroup))
            mixedGroups.append(self.currentGroup)

            for gr in mixedGroups:

                for item in gr.childItems():

                    if isinstance(item, QGraphicsCubeGroup):

                        return
    
        elif figureType == Figures.LINE:

            dialog = RotateDialog(scene, Figures.LINE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

                    
        elif figureType == Figures.MIXED:

            dialog = RotateDialog(scene, Figures.MIXED, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        elif figureType == Figures.CUBE:

            dialog = RotateDialog(scene, Figures.CUBE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        result = dialog.exec()


        '''Scale'''
        if result == QDialog.DialogCode.Accepted and figureType == Figures.POINT:
            
            #Two variants: or it is a [independed item] or an [item with parent mixedgroup]
            if isinstance(self.currentGroup, QGraphicsMixedGroup):

                '''Replace old group by new at scene'''
                #Get new group (In dialog old lines were removed from scene)
                newGroup = dialog.item
                #Update group everywhere
                self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)

                self.currentItem = None
                self.currentGroup = None

            elif isinstance(self.currentGroup, QGraphicsLineGroup):
                
                oldLine = self.currentItem.parentItem()
                new_points: list[QPointF] = dialog.points
                newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)

                elif figureType == Figures.LINE:

                    self.replaceItemEverywhere(scene, library, self.currentItem, newItem, newItem.points)

                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.LINE:
            
            new_points: list[QPointF] = dialog.points
            newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

            if parent != None and isinstance(parent, QGraphicsMixedGroup):
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemInScene(scene, self.currentItem.parentItem(), newItem)
                
                elif figureType == Figures.LINE:
                    
                    self.replaceItemInScene(scene, self.currentItem, newItem)
                
                '''Replace old line by new in group'''
                if figureType == Figures.POINT:
                    
                    parent.removeFromGroup(self.currentItem.parentItem())
                
                elif figureType == Figures.LINE:
                    
                    parent.removeFromGroup(self.currentItem)
                
                parent.addToGroup(newItem)
                self.currentItem = None
                self.currentGroup = None

            else:
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)
                elif figureType == Figures.LINE:
                    self.replaceItemEverywhere(scene, library, self.currentItem, newItem, newItem.points)

                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.MIXED:
            
            '''Replace old group by new at scene'''
            #Get new group (In dialog old lines were removed from scene)
            newGroup = dialog.item
            #Update group everywhere
            self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)

            self.currentItem = None
            self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.CUBE:
            old_cube = self.currentItem
            new_cube = dialog.cube
            points = new_cube.points

            self.replaceItemEverywhere(scene, library, old_cube, new_cube, points)

            self.currentItem = None
            self.currentGroup = None
    def openMirrorDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentItem == None:
            return
        
        figureType = AdditionalMethods.whatFigure(self.currentItem)
        parent: QGraphicsCustomItemGroup = self.currentItem.parentItem()
        dialog: TranslateDialog = None

        '''Send appropriate arguments depended on selectionMode'''
        '''Seek Mixed group'''
        if figureType == Figures.POINT:
            
            #Let the dialog be like to the line
            dialog = MirrorDialog(scene, Figures.POINT, self.currentItem, self.currentGroup, parent.points, self.scaleFactor)

            #If has 3D -> prevent rotation

            mixedGroups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(self.currentGroup, (QGraphicsMixedGroup))
            mixedGroups.append(self.currentGroup)

            for gr in mixedGroups:

                for item in gr.childItems():

                    if isinstance(item, QGraphicsCubeGroup):

                        return
    
        elif figureType == Figures.LINE:

            dialog = MirrorDialog(scene, Figures.LINE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        elif figureType == Figures.MIXED:

            dialog = MirrorDialog(scene, Figures.MIXED, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)
        
        elif figureType == Figures.CUBE:

            dialog = MirrorDialog(scene, Figures.CUBE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)
        result = dialog.exec()


        '''Mirror'''
        if result == QDialog.DialogCode.Accepted and figureType == Figures.POINT:
            
            #Two variants: or it is a [independed item] or an [item with parent mixedgroup]
            if isinstance(self.currentGroup, QGraphicsMixedGroup):
                
                oldLine = self.currentItem.parentItem()
                new_points: list[QPointF] = dialog.points
                newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)
                mixedGroup: QGraphicsCustomItemGroup = parent.parentItem() #parent group of line

                '''Replace old group by new at scene'''
                #Get new group (In dialog old lines were removed from scene)
                scene.removeItem(parent)
                mixedGroup.removeFromGroup(parent)
                mixedGroup.addToGroup(newItem)

                self.currentItem = None
                self.currentGroup = None


            elif isinstance(self.currentGroup, QGraphicsLineGroup):
                
                oldLine = self.currentItem.parentItem()
                new_points: list[QPointF] = dialog.points
                newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)

                elif figureType == Figures.LINE:

                    self.replaceItemInLibrary(scene, library, self.currentItem, newItem, newItem.points)
                
                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.LINE:
            
            new_points: list[QPointF] = dialog.points
            newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

            if parent != None and isinstance(parent, QGraphicsMixedGroup):
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemInScene(scene, self.currentItem.parentItem(), newItem)
                
                elif figureType == Figures.LINE:
                    
                    self.replaceItemInScene(scene, self.currentItem, newItem)
                
                '''Replace old line by new in group'''
                if figureType == Figures.POINT:
                    
                    parent.removeFromGroup(self.currentItem.parentItem())
                
                elif figureType == Figures.LINE:
                    
                    parent.removeFromGroup(self.currentItem)
                
                parent.addToGroup(newItem)

                self.currentItem = None
                self.currentGroup = None

            else:
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)
                elif figureType == Figures.LINE:
                    self.replaceItemEverywhere(scene, library, self.currentItem, newItem, newItem.points)
                
                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.MIXED:
            
            '''Replace old group by new at scene'''
            #Get new group (In dialog old lines were removed from scene)
            newGroup = dialog.item
            #Update group everywhere
            self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)

            self.currentItem = None
            self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.CUBE:
            old_cube = self.currentItem
            new_cube = dialog.cube
            points = new_cube.points

            self.replaceItemEverywhere(scene, library, old_cube, new_cube, points)    

            self.currentItem = None
            self.currentGroup = None  

    def openProjectionDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentItem == None:
            return
        
        figureType = AdditionalMethods.whatFigure(self.currentItem)
        parent: QGraphicsCustomItemGroup = self.currentItem.parentItem()
        dialog: TranslateDialog = None

        '''Send appropriate arguments depended on selectionMode'''
        '''Seek Mixed group'''
        if figureType == Figures.POINT:
            
            #Let the dialog be like to the line
            dialog = ProjectionDialog(scene, Figures.POINT, self.currentItem, self.currentGroup, parent.points, self.scaleFactor)
    
        elif figureType == Figures.LINE:

            dialog = ProjectionDialog(scene, Figures.LINE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        elif figureType == Figures.MIXED:

            dialog = ProjectionDialog(scene, Figures.MIXED, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)
        elif figureType == Figures.CUBE:

            dialog = ProjectionDialog(scene, Figures.CUBE, self.currentItem, self.currentGroup, self.currentItem.points, self.scaleFactor)

        result = dialog.exec()


        '''Mirror'''
        if result == QDialog.DialogCode.Accepted and figureType == Figures.POINT:
            
            #Two variants: or it is a [independed item] or an [item with parent mixedgroup]
            if isinstance(self.currentGroup, QGraphicsMixedGroup):
                
                oldLine = self.currentItem.parentItem()
                new_points: list[QPointF] = dialog.points
                newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)
                mixedGroup: QGraphicsCustomItemGroup = parent.parentItem() #parent group of line

                '''Replace old group by new at scene'''
                #Get new group (In dialog old lines were removed from scene)
                scene.removeItem(parent)
                mixedGroup.removeFromGroup(parent)
                mixedGroup.addToGroup(newItem)

                self.currentItem = None
                self.currentGroup = None


            elif isinstance(self.currentGroup, QGraphicsLineGroup):
                
                oldLine = self.currentItem.parentItem()
                new_points: list[QPointF] = dialog.points
                newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)

                elif figureType == Figures.LINE:

                    self.replaceItemInLibrary(scene, library, self.currentItem, newItem, newItem.points)

                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.LINE:
            
            new_points: list[QPointF] = dialog.points
            newItem = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)

            if parent != None and isinstance(parent, QGraphicsMixedGroup):
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    
                    self.replaceItemInScene(scene, self.currentItem.parentItem(), newItem)
                
                elif figureType == Figures.LINE:
                    
                    self.replaceItemInScene(scene, self.currentItem, newItem)
                
                '''Replace old line by new in group'''
                if figureType == Figures.POINT:
                    
                    parent.removeFromGroup(self.currentItem.parentItem())
                
                elif figureType == Figures.LINE:
                    
                    parent.removeFromGroup(self.currentItem)
                
                parent.addToGroup(newItem)

                self.currentItem = None
                self.currentGroup = None

            else:
                '''Replace old line by new at scene'''
                if figureType == Figures.POINT:
                    self.replaceItemEverywhere(scene, library, self.currentItem.parentItem(), newItem, newItem.points)
                elif figureType == Figures.LINE:
                    self.replaceItemEverywhere(scene, library, self.currentItem, newItem, newItem.points)
                
                self.currentItem = None
                self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.MIXED:
            
            '''Replace old group by new at scene'''
            #Get new group (In dialog old lines were removed from scene)
            newGroup = dialog.item
            #Update group everywhere
            self.replaceItemInLibrary(library, self.currentGroup, newGroup, newGroup.points)

            self.currentItem = None
            self.currentGroup = None

        elif result == QDialog.DialogCode.Accepted and figureType == Figures.CUBE:
            old_cube = self.currentItem
            new_cube = dialog.cube
            points = new_cube.points

            self.replaceItemEverywhere(scene, library, old_cube, new_cube, points)

            self.currentItem = None
            self.currentGroup = None
    #Setters
    def setSelectMode(self, buttons: list[QPushButton], mode: SelectModes): #buttons index: [0] - point [1] - line [2] - mixed
        print(f"SetSelectMode: {mode}")
        self.selectMode = mode
        if mode == SelectModes.POINT:
            buttons[0].setChecked(True)
            buttons[1].setChecked(False)
            buttons[2].setChecked(False)
        elif mode == SelectModes.LINE:
            buttons[1].setChecked(True)
            buttons[0].setChecked(False)
            buttons[2].setChecked(False)
        elif mode == SelectModes.MIXED:
            buttons[2].setChecked(True)
            buttons[0].setChecked(False)
            buttons[1].setChecked(False)
    def setCurrentItemByCSM(self, scene: QGraphicsScene, library: QListWidget, filteredGroups: list[QGraphicsItemGroup], point: QPointF):
        '''Method to focus at scene by given objects and selected SelecMode'''
        currentGroup = None
        currentItem = None
        if self.selectMode == SelectModes.POINT:

            currentItem = self.selectFromGroups(filteredGroups, (QGraphicsPointGroup))
            currentGroup = self.selectFromGroups(filteredGroups, (QGraphicsCubeGroup, QGraphicsMixedGroup, QGraphicsLineGroup))
            
            '''If no selected group'''
            if currentItem is None and self.currentGroup is None:
                return
            
            '''If tried to select point of cube'''
            if isinstance(currentGroup, QGraphicsCubeGroup):
                return
            '''Check if item in a preparation group'''
            if currentGroup in self.preparedGroups:
                self.preparedGroups.remove(currentGroup)
                self.paintItem(currentGroup, self.defaultPen, self.defaultBrush)
            
            '''Other checks to set focused object'''
            if currentItem is None and self.currentGroup is not None:
                
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = None
                self.currentItem = None
                library.clearFocus()
            elif currentItem is not None and self.currentGroup is None:
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
            elif currentItem is not None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
        elif self.selectMode == SelectModes.LINE:

            currentItem = self.selectFromGroups(filteredGroups, (QGraphicsLineGroup))
            currentGroup = self.selectFromGroups(filteredGroups, (QGraphicsCubeGroup, QGraphicsMixedGroup, QGraphicsLineGroup))

            '''If no selected group'''
            if currentItem is None and self.currentGroup is None:
                return
            
            '''Check if item in a preparation group'''
            if currentGroup in self.preparedGroups:
                self.preparedGroups.remove(currentGroup)
                self.paintItem(currentGroup, self.defaultPen, self.defaultBrush)
            
            
            '''Other checks to set focused object'''
            if currentItem is None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = None
                self.currentItem = None
                library.clearFocus()
            elif currentItem is not None and self.currentGroup is None:
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
            elif currentItem is not None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
        elif self.selectMode == SelectModes.MIXED:

            currentItem = self.selectFromGroups(filteredGroups, (QGraphicsCubeGroup, QGraphicsMixedGroup))
            currentGroup = self.selectFromGroups(filteredGroups, (QGraphicsCubeGroup, QGraphicsMixedGroup))

            '''If no selected'''
            if currentItem is None and self.currentGroup is None:
                return
            
            '''Check if currentItem is not a top-parent'''
            if currentItem != None:
                while True:
                    if currentItem.parentItem() != None:
                        currentItem = currentItem.parentItem()
                    if currentItem.parentItem() == None:
                        break
            
            '''Check if item in a preparation group'''
            if currentGroup in self.preparedGroups:
                self.preparedGroups.remove(currentGroup)
                self.paintItem(currentGroup, self.defaultPen, self.defaultBrush)
            
            '''Other checks to set focused object'''
            if currentItem is None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = None
                self.currentItem = None
                library.clearFocus()
            elif currentItem is not None and self.currentGroup is None:
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
            elif currentItem is not None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup) 
    def setCurrentItemByLibrary(self, scene: QGraphicsScene, library: QListWidget, listItem: QListWidgetItem):
        
        data = listItem.data(Qt.ItemDataRole.UserRole)
        item: QGraphicsItemGroup = data["item"]
        
        if item == self.currentGroup:
            return
        
        if item == None:
            if self.currentGroup != None:
                self.currentGroup = None
                library.clearFocus()
                return
            else:
                return
        
        '''Paint default old item'''
        if self.currentGroup != None:
            self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
        
        '''Set new item'''
        self.currentItem = item
        self.currentGroup = item

        '''Set appropriate select mode'''
        figureType = AdditionalMethods.whatFigure(item)
        selectMode = None

        if figureType == Figures.POINT:
            
            selectMode = SelectModes.POINT
        
        elif figureType == Figures.LINE:
            
            selectMode = SelectModes.LINE
        
        elif figureType == Figures.MIXED or figureType == Figures.CUBE:
            
            selectMode = SelectModes.MIXED
        
        self.setSelectMode(self.selectModeButtons, selectMode)
        
        '''Paint focused'''
        self.paintItem(self.currentGroup, self.focusedPen, self.focusedBrush)
    def setFocusAtLibraryByItem(self, library: QListWidget, item: QGraphicsItemGroup):
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == item:
                library.setCurrentItem(it)
                library.setFocus()
                print(f"Library focus set at {it}")
                break
    #Adders
    def addItemToLibrary(self, library: QListWidget, item: QGraphicsItemGroup, points: list[QPointF]):
        print(f"AddItemToLibrary: {item}")
        data = {
                    "item": item,
                    "points": points
                }
        
        listItem = QListWidgetItem(f"Item: {item}")
        listItem.setText(item.equation)
        listItem.setData(Qt.ItemDataRole.UserRole, data)
        library.addItem(listItem)
    def addItemToScene(self, scene: QGraphicsScene, item: QGraphicsItemGroup):
        print(f"AddItemToScene: {item}")
        scene.addItem(item)

        if isinstance(item, QGraphicsMixedGroup):
            if item not in self.groups:
                self.groups.append(item)
    def addItemEverywhere(self, scene: QGraphicsScene, library: QListWidget, item: QGraphicsItemGroup, points: list[QPointF]):
        print(f"AddItemEverywhere: {item}")
        #add to library
        self.addItemToLibrary(library, item, points)
        #add to scene
        self.addItemToScene(scene, item)
        pass
    #Replacers
    def replaceItemInLibrary(self, library: QListWidget, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup, points: list[QPointF]):
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == oldItem:
                data["item"] = newItem
                data["points"] = points
                it.setData(Qt.ItemDataRole.UserRole, data)
                it.setText(newItem.equation)
                break
        self.setFocusAtLibraryByItem(library, newItem)
    def replaceItemInScene(self, scene: QGraphicsScene, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup):
        scene.removeItem(oldItem)
        scene.addItem(newItem)

        if oldItem in self.groups:
            self.groups.remove(oldItem)
        if newItem not in self.groups:
            self.groups.append(newItem)

        pass
    def replaceItemEverywhere(self, scene: QGraphicsScene, library: QListWidget, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup, points: list[QPointF]):
        #replace in library
        self.replaceItemInLibrary(library, oldItem, newItem, points)
        #redraw line at scene
        self.replaceItemInScene(scene, oldItem, newItem)
        pass
    def moveItemsAtScene(self, scene: QGraphicsScene, library: QListWidget, view: QGraphicsView, leftMousePos: QPoint, deltaVal: QPointF):
        delta = QPointF(deltaVal.x(), deltaVal.y()*-1)
        print(f"Called moveItemsAtScene: {delta}")
        if self.currentItem == None:
            return
        
        else:
            
            '''If user try to move point or line of a cube return none'''
            if self.selectMode == SelectModes.POINT:
                if self.currentItem.parentItem() != None:
                    if self.currentItem.parentItem().parentItem() != None:
                        if isinstance(self.currentItem.parentItem().parentItem(), QGraphicsCubeGroup):
                            return
            if self.selectMode == SelectModes.LINE:
                if self.currentItem.parentItem() != None:
                    if isinstance(self.currentItem.parentItem(), QGraphicsCubeGroup):
                        return
                    
            '''Move items'''
            if isinstance(self.currentItem, QGraphicsPointGroup) and self.selectMode == SelectModes.POINT:
                
                '''Update points'''
                oldPoint = self.currentItem #QGPointGroup
                oldLine = oldPoint.parentItem() #QGLineGroup
                oldLine_parent: QGraphicsMixedGroup = oldLine.parentItem() #QGMixedGroup
                topSideParent = oldLine_parent #Main QGMixedGroup
                
                if oldLine_parent != None:
                    while topSideParent.parentItem() != None:
                        topSideParent = topSideParent.parentItem()

                old_points = oldLine.points
                new_points: list[QPointF] = []
                new_point: QPointF = None   #New point for deconstruction part

                for pt in old_points:
                    if pt == oldPoint.points[0]:
                        point = pt + delta/self.scaleFactor
                        new_points.append(point)
                        new_point = point
                    else:
                        new_points.append(pt)

                '''Create and replace old item'''
                #Create new line
                newLine = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)
                
                #Deconstruct item to get current PointGroup
                currentPointItem: QGraphicsPointGroup = None
                for chld in newLine.childItems():
                    if isinstance(chld, QGraphicsPointGroup):
                        if chld.points[0] == new_point:
                            currentPointItem = chld
                            break

                #Check if object is top-parent
                if oldLine_parent == None:
                    self.replaceItemEverywhere(scene, library, oldLine, newLine, new_points)
                    #set focus
                    self.setCurrentItemByCSM(scene, library, [currentPointItem, newLine], QPointF())
                
                else:
                    oldLine_parent.removeFromGroup(oldLine)
                    self.deleteItemFromScene(scene, oldLine)
                    oldLine_parent.addToGroup(newLine)
                    self.replaceItemInLibrary(library, oldLine, newLine, newLine.points)
                    #Set focus
                    self.setCurrentItemByCSM(scene, library, [currentPointItem, topSideParent], QPointF())
            elif isinstance(self.currentItem, QGraphicsLineGroup) and self.selectMode == SelectModes.LINE:
                
                '''Update points'''
                oldLine = self.currentItem  #QGLineGroup
                parent: QGraphicsCustomItemGroup = oldLine.parentItem()
                old_points: list[QPointF] = oldLine.points
                new_points = [old_points[0] + delta/self.scaleFactor, old_points[1] + delta/self.scaleFactor]
                
                '''Create and replace old item'''
                #Create new line
                newLine = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)
                
                #Check if object is top-parent
                if parent == None:
                    self.replaceItemEverywhere(scene, library, oldLine, newLine, new_points)
                    
                    #Set focus
                    
                    self.setCurrentItemByCSM(scene, library, [newLine], QPointF())
                else:
                    parent.removeFromGroup(oldLine)
                    self.replaceItemInScene(scene, oldLine, newLine)
                    parent.addToGroup(newLine)
                    
                    #Set focus
                    self.setCurrentItemByCSM(scene, library, [newLine, parent], QPointF())                
            elif isinstance(self.currentItem, QGraphicsMixedGroup) and self.selectMode == SelectModes.MIXED:
                '''Get all Mixed groups'''

                groups: list[QGraphicsMixedGroup] = AdditionalMethods.getAllChildItemsByCategory(self.currentGroup, (QGraphicsCubeGroup, QGraphicsMixedGroup))
                groups.append(self.currentGroup)
                
                '''Create and replace old items in mixed groups'''
                for gr in groups:
                    
                    if isinstance(gr, QGraphicsCubeGroup):

                        if gr.parentItem() == None:

                            old_cube = gr
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

                            

                            new_cube = AdditionalMethods.createCustomCube(tX + delta.x()/self.scaleFactor, tY + delta.y()/self.scaleFactor, tZ + 0, sX, sY, sZ, rX, rY, rZ, camZ, self.scaleFactor)
                            self.replaceItemEverywhere(scene, library, old_cube, new_cube, new_cube.points)
                            self.currentItem = new_cube
                            self.currentGroup = new_cube
                            continue
                        else:
                            
                            old_cube = gr
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


                            
                            parent: QGraphicsMixedGroup = old_cube.parentItem()
                            new_cube = AdditionalMethods.createCustomCube(tX + delta.x()/self.scaleFactor, tY + delta.y()/self.scaleFactor, tZ + 0, sX, sY, sZ, rX, rY, rZ, camZ, self.scaleFactor)
                            parent.removeFromGroup(old_cube)
                            self.replaceItemInScene(scene, old_cube, new_cube)
                            parent.addToGroup(new_cube)
                            continue
                    
                    for chld in gr.childItems():

                        if isinstance(chld, QGraphicsLineGroup) and not isinstance(chld.parentItem(), QGraphicsCubeGroup):

                            oldLine = chld
                            old_points: list[QPointF] = oldLine.points
                            new_points = [old_points[0] + delta/self.scaleFactor, old_points[1] + delta/self.scaleFactor]
                            
                            #Create new line
                            newLine = AdditionalMethods.createCustomLine(new_points, self.scaleFactor)
                            
                            #Replace old by new
                            gr.removeFromGroup(oldLine)
                            self.replaceItemInScene(scene, oldLine, newLine)
                            gr.addToGroup(newLine)
                        

                '''Set focus'''
                self.setCurrentItemByCSM(scene, library, [self.currentGroup], QPointF())
    #Deletors: Scene deletion sets the focus!
    def deleteCurrentItemFromScene(self, scene: QGraphicsScene):
        print(f"deleteCurrentItemFromScene: {self.currentGroup}")
        self.deleteItemFromScene(scene, self.currentGroup)
    def deleteCurrentItemFromLibrary(self, library: QListWidget):
        print(f"deleteCurrentItemFromLibrary: {self.currentGroup}")
        #remove from library
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for i in range(len(listItems)):
            data = listItems[i].data(Qt.ItemDataRole.UserRole)
            if data["item"] == self.currentGroup:
                library.takeItem(i) #removing from the library
                library.clearFocus()
                break
    def deleteCurrentItem(self, scene: QGraphicsScene, library: QListWidget):
        print(f"deleteCurrentItem: {self.currentGroup}")
        #delete from library
        self.deleteCurrentItemFromLibrary(library)
        #delete from scene
        self.deleteCurrentItemFromScene(scene)
    def deleteItemFromLibrary(self, library: QListWidget, item: QGraphicsItem):
        print(f"deleteItemFromLibrary: {item}")
        #remove from library
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for i in range(len(listItems)):
            data = listItems[i].data(Qt.ItemDataRole.UserRole)
            if data["item"] == item:
                library.takeItem(i) #removing from the library
                library.clearFocus()
                break
    def deleteItemFromScene(self, scene: QGraphicsScene, item: QGraphicsItem):
        print(f"deleteItemFromScene: {item}")
        scene.removeItem(item)
        self.currentGroup = None
        self.currentItem = None
    def deleteItemEverywhere(self, scene: QGraphicsScene, library: QListWidget, item: QGraphicsItem):
        print(f"deleteItemEverywhere: {item}")
        #delete from library
        self.deleteItemFromLibrary(library, item)
        #delete from scene
        self.deleteItemFromScene(scene, item)
    #Redraw methods for scaling
    def redrawGrid(self, scene: QGraphicsCustomScene, scaleFactor: float, gridPen: QPen, crossPen: QPen):
        print(f"redrawGrid: {scaleFactor}")
        scene.scaleFactor = scaleFactor
        scene.gridPen = gridPen
        scene.crossPen = crossPen
        scene.update()
    def redrawItems(self, scene: QGraphicsCustomScene, library: QListWidget):
        
        print(f"redrawItems:")
        sceneItems = scene.items()
        currentFocusedItem = self.currentGroup #Memorize focused object
        currentPreparedItems = self.preparedGroups
        
        savedPreparedItemsToPaint = []
        for parentItem in sceneItems:
            
            if isinstance(parentItem, QGraphicsCubeGroup):
                
                parent = parentItem.parentItem()
                old_cube: QGraphicsCubeGroup = parentItem
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
                scaleF = self.scaleFactor
                new_cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleF)
                self.cube = new_cube
                
                if parent != None:
                    #replace old cube by new cube
                    parent.removeFromGroup(old_cube)
                    self.deleteItemFromScene(scene, old_cube)
                    parent.addToGroup(new_cube)
                else:
                    self.replaceItemEverywhere(scene, library, old_cube, new_cube, new_cube.points)
                
                '''Save new prepared MixedGroup'''
                if parentItem in currentPreparedItems:
                        
                    savedPreparedItemsToPaint.append(new_cube)

                '''Replace old focused object to new'''
                if currentFocusedItem == parentItem:

                    currentFocusedItem = new_cube 

            if isinstance(parentItem, QGraphicsMixedGroup) and not isinstance(parentItem, QGraphicsCubeGroup):
                for chld in parentItem.childItems():
                    if isinstance(chld, QGraphicsCubeGroup):
                        continue
                    if isinstance(chld, QGraphicsMixedGroup):
                        
                        '''Replace old focused object to new'''
                        if currentFocusedItem == chld:
                            currentFocusedItem = chld
                        
                        '''Save new prepared MixedGroup'''
                        if chld in currentPreparedItems:
                        
                            savedPreparedItemsToPaint.append(chld)
                    
                    elif isinstance(chld, QGraphicsLineGroup):
                        
                        '''Create new item and replace old everywhere'''
                        oldItem: QGraphicsLineGroup = chld
                        points = oldItem.points
                        newItem = AdditionalMethods.createCustomLine(points, self.scaleFactor)
                        parentItem.removeFromGroup(oldItem)
                        self.replaceItemInScene(scene, oldItem, newItem)
                        parentItem.addToGroup(newItem)
                        
                        '''Save new prepared LineGroup'''
                        if chld in currentPreparedItems:
                            savedPreparedItemsToPaint.append(chld)
                        
                        '''Replace old focused item to new'''
                        if currentFocusedItem == chld:
                            currentFocusedItem = chld
                        
            elif isinstance(parentItem, QGraphicsLineGroup) and parentItem.parentItem() == None:
                
                '''Create new item and replace old everywhere'''
                oldItem: QGraphicsLineGroup = parentItem
                points = oldItem.points
                newItem = AdditionalMethods.createCustomLine(points, self.scaleFactor)
                self.replaceItemEverywhere(scene, library, oldItem, newItem, points)
                
                '''Replace old prepared item to new'''
                if oldItem in currentPreparedItems:
                    savedPreparedItemsToPaint.append(newItem)
                
                '''Replace old focused object to new'''
                if currentFocusedItem == parentItem:
                    currentFocusedItem = newItem 
        
        
        #Paint prepared and set prepared list
        self.preparedGroups = savedPreparedItemsToPaint
        for item in savedPreparedItemsToPaint:
            self.paintItem(item, self.preparedPen, self.preparedBrush)
        
        #set focus from old to new item
        self.setCurrentItemByCSM(scene, library, [currentFocusedItem], QPointF())
    def redrawEverything(self, scene: QGraphicsCustomScene, library: QListWidget, scaleFactor: float, deltaY: float, defaultPen: QPen, crossPen: QPen):
        print(f"redrawEverything:") 
        if deltaY > 0:
            if scaleFactor * 1.1 >= 90:
                return
            self.scaleFactor = scaleFactor * 1.1
        elif deltaY < 0:
            if scaleFactor * 0.9 <= 20:
                return
            self.scaleFactor = scaleFactor * 0.9
        self.redrawGrid(scene, self.scaleFactor, defaultPen, crossPen)
        self.redrawItems(scene, library)
        scene.setSceneRect(QRect(-1000*self.scaleFactor,-1000*self.scaleFactor,2000*self.scaleFactor,2000*self.scaleFactor))
    #Group
    def prepareToGroup(self, scene: QGraphicsScene, library: QListWidget, filteredGroups: list[QGraphicsItemGroup], point: QPointF):
        
        print("---prepareToGroup---")
        '''Get item from clicked area'''
        group = self.selectFromGroups(filteredGroups, (QGraphicsMixedGroup, QGraphicsLineGroup, QGraphicsCubeGroup))
        '''Check if item is currently focused'''
        if group == self.currentGroup:
            return
        if group in self.preparedGroups:
            self.preparedGroups.remove(group)
            self.paintItem(group, self.defaultPen, self.defaultBrush)
            print(f"Items in prepared group: {len(self.preparedGroups)}")
            return
        
        '''If isn't focused then add to prepare group'''
        self.preparedGroups.append(group)
        self.paintItem(group, self.preparedPen, self.preparedBrush)
        print(f"Items in prepared group: {len(self.preparedGroups)}")
    def groupPreparedItems(self, scene: QGraphicsScene, library: QListWidget):
        print(f"Подготовлено для группировки: {len(self.preparedGroups)}")
        if len(self.preparedGroups) <= 1:
            pass
        
        else:
            
            mixedGroup = QGraphicsMixedGroup()
            
            '''Add items to mixed group and replace them by one item in library'''
            for gr in self.preparedGroups:
                #Remove items everywhere
                self.deleteItemFromLibrary(library, gr)
                #Add to mixed group
                mixedGroup.addToGroup(gr)
            
            #Replace by one item
            self.addItemEverywhere(scene, library, mixedGroup, mixedGroup.points)
            #Clear prepared groups
            self.preparedGroups = []
            #Paint default
            self.paintItem(mixedGroup, self.defaultPen, self.defaultBrush)
            self.currentItem = None
            self.currentGroup = None
            #Prevent future deletion
            self.groups.append(mixedGroup)
    def ungroup(self, scene: QGraphicsScene, library: QListWidget, group: QGraphicsItem):
        if isinstance(group, QGraphicsMixedGroup) and not isinstance(group, QGraphicsCubeGroup):
            '''Add separated items to library and remove from group'''
            children = group.childItems()
            for chld in children:
                print(f"Достаем {chld} из {chld.parentItem()}")
                group.removeFromGroup(chld)
                self.addItemToLibrary(library, chld, chld.points)
                self.paintItem(chld, self.defaultPen, self.defaultBrush)
            if len(group.childItems()) == 0:
                self.deleteItemFromLibrary(library, group)
            
            self.deleteItemEverywhere(scene, library, group)
            self.groups.remove(group)
            library.clearFocus()

            '''Set to default'''
            self.currentItem = None
            self.currentGroup = None
    #Additional methods
    def getAllBaseChildItems(self, item: QGraphicsItem):
        '''Returns all base items of group'''
        '''Unpack group items'''
        all_items = []
        if not isinstance(item, QGraphicsItemGroup):
            return []
        else:
            children = item.childItems()
            for chld in children:
                if not isinstance(chld, QGraphicsItemGroup):
                    all_items.append(chld)
                else:
                    all_items.extend(self.getAllBaseChildItems(chld))
        return all_items
    def selectFromGroups(self, groups: list[QGraphicsItemGroup], class_types: tuple):   
        '''Method used with increasing order of items ierarchy'''
        group = None
        for gr in reversed(groups): #reverse because parents are last in list
            if isinstance(gr, class_types):
                group = gr
                return group
        return group