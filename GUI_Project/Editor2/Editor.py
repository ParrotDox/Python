import os
from CUD.Create import CreateDialog
from CUD.Update import UpdateDialog
from TSRM.Translate import TranslateDialog
from TSRM.Scale import ScaleDialog
from TSRM.Rotate import RotateDialog
from TSRM.Mirror import MirrorDialog
from EditorEnum import Figures, SelectModes
from CustomClasses import (
    QGraphicsCustomScene,
    QOneWayToggleButton,
    QGraphicsCustomItemGroup,
    QGraphicsLineGroup, 
    QGraphicsCubeGroup, 
    QGraphicsPointGroup,
    QGraphicsMixedGroup, 
    QGraphicsCustomView)
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
        self.initColors()

        #Current selection
        self.currentGroup: QGraphicsCustomItemGroup = None
        self.currentItem: QGraphicsItem = None #Can be point or group

        #Current scale
        self.scaleFactor = 50

        self.initUI()
        self.setWindowTitle("Editor"); self.setFixedSize(1280, 720)
        self.setObjectName("Editor")

        
        

    def initUI(self):
        #widgets
        buttonCreate = QPushButton("C"); buttonCreate.setFixedSize(35,35); buttonCreate.clicked.connect(lambda: self.openCreateDialog(scene, library))
        buttonUpdate = QPushButton("U"); buttonUpdate.setFixedSize(35,35); buttonUpdate.clicked.connect(lambda: self.openUpdateDialog(scene, library))
        buttonDelete = QPushButton("D"); buttonDelete.setFixedSize(35,35); buttonDelete.clicked.connect(lambda: self.deleteCurrentItem(scene, library))

        buttonTranslate = QPushButton("T"); buttonTranslate.setFixedSize(35,35); buttonTranslate.clicked.connect(lambda: self.operTranslateDialog(scene, library))
        buttonScale = QPushButton("S"); buttonScale.setFixedSize(35,35); buttonScale.clicked.connect(lambda: self.openScaleDialog(scene, library))
        buttonRotate = QPushButton("R"); buttonRotate.setFixedSize(35,35); buttonRotate.clicked.connect(lambda: self.openRotateDialog(scene, library))
        buttonMirror = QPushButton("M"); buttonMirror.setFixedSize(35,35); buttonMirror.clicked.connect(lambda: self.openMirrorDialog(scene, library))

        buttonPoint = QOneWayToggleButton(self.createIcon("Icons/point.png", 35, 35), ""); buttonPoint.setFixedSize(35,35); buttonPoint.pressed.connect(lambda:self.setSelectMode(selectModeButtons, SelectModes.POINT)); buttonPoint.setCheckable(True); buttonPoint.setChecked(False)
        buttonLine = QOneWayToggleButton(self.createIcon("Icons/line.png", 35, 35), ""); buttonLine.setFixedSize(35,35); buttonLine.pressed.connect(lambda:self.setSelectMode(selectModeButtons, SelectModes.LINE)); buttonLine.setCheckable(True); buttonLine.setChecked(True)
        selectModeButtons = [buttonPoint, buttonLine]

        scene = QGraphicsCustomScene(QRect(-1000,-1000,2000,2000), self.scaleFactor, self.defaultPen, self.defaultPen)
        view = QGraphicsCustomView(scene)
        view.itemFocused.connect(lambda scene, filteredGroups, point: self.setCurrentItemByCSM(scene, library, filteredGroups, point))
        view.itemFocusedToGroup.connect(lambda scene, filteredGroups, point: self.prepareToGroup(scene, library, filteredGroups, point))
        view.itemMoved.connect(lambda leftMousePos, delta: self.moveItemsAtScene(scene, library, view, leftMousePos, delta))
        view.scaleFactorChanged.connect(lambda deltaY: self.redrawEverything(scene, library, self.scaleFactor, deltaY, self.currentPen, self.currentPen))
        
        objectsLabel = QLabel("Objects")
        library = QListWidget(); library.itemClicked.connect(lambda item: self.setCurrentItemByLibrary(scene, library, item))

        #layouts
        mainLayout = QHBoxLayout()

        workspaceLayout = QVBoxLayout()
        libraryLayout = QHBoxLayout()

        actionsLayout = QHBoxLayout(); actionsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cudLayout = QHBoxLayout()
        tsrmLayout = QHBoxLayout()
        selectModeLayout = QHBoxLayout()

        objectsLayout = QVBoxLayout()

        mainLayout.addLayout(workspaceLayout); mainLayout.addLayout(libraryLayout)
        mainLayout.setStretchFactor(workspaceLayout, 3); mainLayout.setStretchFactor(libraryLayout, 1)

        actionsLayout.addLayout(cudLayout); actionsLayout.addSpacing(15); actionsLayout.addLayout(tsrmLayout); actionsLayout.addSpacing(15); actionsLayout.addLayout(selectModeLayout)

        libraryLayout.addLayout(objectsLayout)

        cudLayout.addWidget(buttonCreate); cudLayout.addWidget(buttonUpdate); cudLayout.addWidget(buttonDelete);
        tsrmLayout.addWidget(buttonTranslate); tsrmLayout.addWidget(buttonScale); tsrmLayout.addWidget(buttonRotate); tsrmLayout.addWidget(buttonMirror)
        selectModeLayout.addWidget(buttonPoint); selectModeLayout.addWidget(buttonLine)

        workspaceLayout.addLayout(actionsLayout); workspaceLayout.addWidget(view)

        objectsLayout.addWidget(objectsLabel); objectsLayout.addWidget(library)

        self.setLayout(mainLayout)


        #StyleSheets
        styleSheet = ""
        self.setStyleSheet(styleSheet)
        pass
    #Colors
    def initColors(self):
        self.defaultPen = QPen(); self.defaultBrush = QBrush()
        self.focusedPen = QPen(); self.focusedBrush = QBrush()
        self.preparedPen = QPen(); self.preparedBrush = QBrush()

        self.defaultPen.setColor(QColor(20, 20, 20))
        self.defaultPen.setWidth(2)
        self.defaultPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.defaultBrush.setColor(QColor(50, 50, 50))

        self.focusedPen.setColor(QColor(220, 0, 0))
        self.focusedPen.setWidth(3)
        self.focusedPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.focusedBrush.setColor(QColor(220, 0, 0))

        self.preparedPen.setColor(QColor(0, 200, 0))
        self.preparedPen.setWidth(3)
        self.preparedPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.preparedBrush.setColor(QColor(0, 200, 0))

    def paintItem(self, item: QGraphicsItem, pen: QPen, brush: QBrush):
        items: list[QGraphicsItem] = self.getAllChildItems(item)
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
        dialog = CreateDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            if dialog.figure == Figures.LINE:
                #Add to scene
                points: list[QPointF] = dialog.points
                newLine = self.createCustomLine(points) #line is a group!
                #add item everywhere
                self.addItemEverywhere(scene, library, newLine, points)
            elif dialog.figure == Figures.CUBE:
                pass
        else:
            return
    def openUpdateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        figure = self.whatFigure(self.currentGroup)
        
        dialog = UpdateDialog(figure)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            points: list[QPointF] = dialog.points
            newItem = self.createCustomLine(points)
            #replace item everywhere
            self.replaceItemEverywhere(scene, library, self.currentGroup, newItem, points)
            #set focus
            self.setCurrentItemByCSM(scene, library, [newItem], QPointF())

                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass       
    def operTranslateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = TranslateDialog(figure, self.currentGroup, self.currentGroup.points)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newItem = self.createCustomLine(points)
            #update info in library
            self.replaceItemEverywhere(scene, library, self.currentGroup, newItem, points)
            #setFocus
            self.setCurrentItemByCSM(scene, library, [newItem], QPointF())
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass
    def openScaleDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = ScaleDialog(figure, self.currentGroup, self.currentGroup.points)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newItem = self.createCustomLine(points)
            #replace item everywhere
            self.replaceItemEverywhere(scene, library, self.currentGroup, newItem, points)
            #setFocus
            self.setCurrentItemByCSM(scene, library, [newItem], QPointF())
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass  
    def openRotateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = RotateDialog(figure, self.currentGroup, self.currentGroup.points)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newItem = self.createCustomLine(points)
            #replace item everywhere
            self.replaceItemEverywhere(scene, library, self.currentGroup, newItem, points)
            #setFocus
            self.setCurrentItemByCSM(scene, library, [newItem], QPointF())
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass
    def openMirrorDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = MirrorDialog(figure, self.currentGroup, self.currentGroup.points)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newItem = self.createCustomLine(points)
            #add item everywhere
            self.addItemEverywhere(scene, library, newItem, points)
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass
    #Setters
    def setSelectMode(self, buttons: list[QPushButton], mode: SelectModes): #buttons index: [0] - point [1] - line
        self.selectMode = mode
        if mode == SelectModes.POINT:
            buttons[1].setChecked(False)
        elif mode == SelectModes.LINE:
            buttons[0].setChecked(False)
    def setCurrentItemByCSM(self, scene: QGraphicsScene, library: QListWidget, filteredGroups: list[QGraphicsItemGroup], point: QPointF):
        '''Method to focus at scene by given objects and selected SelecMode'''
        print(filteredGroups)
        currentGroup = None
        currentItem = None
        if self.selectMode == SelectModes.POINT:
            currentItem = self.selectFromGroups(filteredGroups, QGraphicsPointGroup)
            currentGroup = self.selectFromGroups(filteredGroups, QGraphicsLineGroup)
            if currentItem is None and self.currentGroup is None:
                return
            elif currentItem is None and self.currentGroup is not None:
                self.paintItem(self.currentItem, self.defaultPen, self.defaultBrush)
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
            currentItem = self.selectFromGroups(filteredGroups, QGraphicsLineGroup)
            currentGroup = self.selectFromGroups(filteredGroups, QGraphicsLineGroup)
            if currentItem is None and self.currentGroup is None:
                return
            elif currentItem is None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = None
                self.currentItem = None
                library.clearFocus()
            elif currentItem is not None and self.currentGroup is None:
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentGroup, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
            elif currentItem is not None and self.currentGroup is not None:
                self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintItem(self.currentItem, self.focusedPen, self.focusedBrush)
                self.setFocusAtLibraryByItem(library, currentGroup)
        #print(f"setCurrentItemByCSM has these groups {filteredGroups}")
        print(f"setCurrentItemByCSM currentGroup is {currentGroup}")
        print(f"setCurrentItemByCSM currentItem is {currentItem}")
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
        if self.currentGroup != None:
            self.paintItem(self.currentGroup, self.defaultPen, self.defaultBrush)
        
        self.currentGroup = item
        self.paintItem(self.currentGroup, self.focusedPen, self.focusedBrush)
        print(f"Current item {item}")   
    def setLibraryItemName(self, library: QListWidget, item: QGraphicsItemGroup, text: str):
        #update text in widgetList element
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == item:
                it.setText(f"{text} {data['item']}")
            break
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
        data = {
                    "item": item,
                    "points": points
                }
        item = QListWidgetItem(f"Item: {item}")
        item.setData(Qt.ItemDataRole.UserRole, data)
        library.addItem(item)
    def addItemToScene(self, scene: QGraphicsScene, item: QGraphicsItemGroup):
        scene.addItem(item)
        pass
    def addItemEverywhere(self, scene: QGraphicsScene, library: QListWidget, item: QGraphicsItemGroup, points: list[QPointF]):
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
                self.setLibraryItemName(library, oldItem, "")
                data["item"] = newItem
                data["points"] = points
                it.setData(Qt.ItemDataRole.UserRole, data)
                break
        self.setFocusAtLibraryByItem(library, newItem)
    def replaceItemInScene(self, scene: QGraphicsScene, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup):
        scene.removeItem(oldItem)
        scene.addItem(newItem)
        pass
    def replaceItemEverywhere(self, scene: QGraphicsScene, library: QListWidget, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup, points: list[QPointF]):
        #replace in library
        self.replaceItemInLibrary(library, oldItem, newItem, points)
        #redraw line at scene
        self.replaceItemInScene(scene, oldItem, newItem)
        pass
    def moveItemsAtScene(self, scene: QGraphicsScene, library: QListWidget, view: QGraphicsView, leftMousePos: QPoint, delta: QPointF):
        if self.currentItem == None:
            return
        else:
            if isinstance(self.currentItem, QGraphicsPointGroup) and self.selectMode == SelectModes.POINT:
                '''Update points'''
                oldItem = self.currentItem #QGPointGroup
                oldGroup = self.currentGroup #QGLineGroup
                old_points = oldGroup.points
                new_points: list[QPointF] = []
                new_point: QPointF = None   #New point for deconstruction part
                for pt in old_points:
                    if pt == oldItem.points[0]:
                        point = pt + delta/self.scaleFactor
                        new_points.append(point)
                        new_point = point
                    else:
                        new_points.append(pt)
                '''Create and replace old item'''
                newItem = self.createCustomLine(new_points)
                self.replaceItemEverywhere(scene, library, oldGroup, newItem, new_points)
                '''Deconstruct item to get current PointGroup'''
                currentPointItem: QGraphicsPointGroup = None
                for chld in newItem.childItems():
                    if isinstance(chld, QGraphicsPointGroup):
                        if chld.points[0] == new_point:
                            print("EQUAL")
                            currentPointItem = chld
                            break

                #set focus
                self.setCurrentItemByCSM(scene, library, [newItem, currentPointItem], QPointF())
                pass
            elif isinstance(self.currentItem, QGraphicsLineGroup) and self.selectMode == SelectModes.LINE:
                '''Update points'''
                oldItem = self.currentItem  #QGLineGroup
                old_points: list[QPointF] = oldItem.points
                new_points = [old_points[0] + delta/self.scaleFactor, old_points[1] + delta/self.scaleFactor]
                '''Create and replace old item'''
                newItem = self.createCustomLine(new_points)
                self.replaceItemEverywhere(scene, library, oldItem, newItem, new_points)
                #set focus
                self.setCurrentItemByCSM(scene, library, [newItem], QPointF())
    #Deletors: Scene deletion sets the focus!
    def deleteCurrentItemFromScene(self, scene: QGraphicsScene):
        scene.removeItem(self.currentGroup)
        self.currentGroup = None
        self.currentItem = None
    def deleteCurrentItemFromLibrary(self, library: QListWidget):
        #remove from library
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for i in range(len(listItems)):
            data = listItems[i].data(Qt.ItemDataRole.UserRole)
            if data["item"] == self.currentGroup:
                library.takeItem(i) #removing from the library
                library.clearFocus()
                break
    def deleteCurrentItem(self, scene: QGraphicsScene, library: QListWidget):
        #delete from library
        self.deleteCurrentItemFromLibrary(library)
        #delete from scene
        self.deleteCurrentItemFromScene(scene)
        pass
    #Redraw methods for scaling
    def redrawGrid(self, scene: QGraphicsCustomScene, scaleFactor: float, defaultPen: QPen, crossPen: QPen):
        scene.scaleFactor = scaleFactor
        scene.defaultPen = defaultPen
        scene.crossPen = crossPen
        scene.update()
    def redrawItems(self, scene: QGraphicsCustomScene, library: QListWidget):
        sceneItems = scene.items()
        currentFocusedItem = self.currentGroup #Memorize focused object
        for it in sceneItems:
            if isinstance(it, QGraphicsMixedGroup):
                pass
            elif isinstance(it, QGraphicsLineGroup):
                '''Create new item and replace old everywhere'''
                oldItem: QGraphicsLineGroup = it
                points = oldItem.points
                newItem = self.createCustomLine(points)
                self.replaceItemEverywhere(scene, library, oldItem, newItem, points)
                '''Replace old focused object to new'''
                if currentFocusedItem == it:
                    currentFocusedItem = newItem 
        
        #set focus from old to new item
        self.setCurrentItemByCSM(scene, library, [currentFocusedItem], QPointF())
    def redrawEverything(self, scene: QGraphicsCustomScene, library: QListWidget, scaleFactor: float, deltaY: float, defaultPen: QPen, crossPen: QPen):
        if deltaY > 0:
            self.scaleFactor = scaleFactor * 1.1
        elif deltaY < 0:
            self.scaleFactor = scaleFactor * 0.9
        self.redrawGrid(scene, self.scaleFactor, defaultPen, crossPen)
        self.redrawItems(scene, library)
    #Group
    def prepareToGroup(self, scene: QGraphicsScene, library: QListWidget, filteredGroups: list[QGraphicsItemGroup], point: QPointF):

        pass
    #Additional methods
    def createCustomLine(self, points: list[QPointF]):
        #All points for drawing scaled by scaleFactor!
        '''Line points to draw a line'''
        linePStart = QPointF(points[0].x()*self.scaleFactor, points[0].y()*self.scaleFactor) #Start point for line
        linePEnd = QPointF(points[1].x()*self.scaleFactor, points[1].y()*self.scaleFactor) #End point for line
        '''Start point item for ellipse of line'''
        ellipseStart = QGraphicsEllipseItem(linePStart.x()-5, linePStart.y()-5, 10, 10)
        pointStartGroup = QGraphicsPointGroup(); pointStartGroup.points = [points[0]]
        pointStartGroup.addToGroup(ellipseStart)
        '''End point item for ellipse of line'''
        ellipseEnd = QGraphicsEllipseItem(linePEnd.x()-5, linePEnd.y()-5, 10, 10)
        pointEndGroup = QGraphicsPointGroup(); pointEndGroup.points = [points[1]]
        pointEndGroup.addToGroup(ellipseEnd)
        '''Line item and group gathering'''
        lineItem = QGraphicsLineItem(QLineF(linePStart, linePEnd))
        group = QGraphicsLineGroup()
        group.addToGroup(pointStartGroup); group.addToGroup(pointEndGroup); group.addToGroup(lineItem)
        '''Metainfo about group'''
        group.scaleFactor = self.scaleFactor
        group.points = points
        group.baseChildItems = ellipseStart, ellipseEnd, lineItem
        return group
    def getAllChildItems(self, item: QGraphicsItem):
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
                    all_items.extend(self.getAllChildItems(chld))
        return all_items
    def selectFromGroups(self, groups: list[QGraphicsItemGroup], class_type):
        for gr in groups:
            if isinstance(gr, class_type):
                return gr
        return None
    def whatFigure(self, items: QGraphicsItem):
        if items == None:
            return None
        elif isinstance(items, QGraphicsEllipseItem):
            return Figures.POINT
        elif isinstance(items, QGraphicsLineGroup):
            return Figures.LINE
        elif isinstance(items, QGraphicsCubeGroup):
            return Figures.CUBE