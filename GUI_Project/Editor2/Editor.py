import os
from CUD.Create import CreateDialog
from CUD.Update import UpdateDialog
from TSRM.Translate import TranslateDialog
from TSRM.Scale import ScaleDialog
from TSRM.Rotate import RotateDialog
from TSRM.Mirror import MirrorDialog
from EditorEnum import Figures, SelectModes
from CustomClasses import (
    QOneWayToggleButton,
    QGraphicsLineGroup, 
    QGraphicsCubeGroup, 
    QGraphicsPointGroup,
    QGraphicsMixedGroup, 
    QGraphicsViewCustom)
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
from PySide6.QtCore import Qt, QLineF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QIcon, QPixmap

class EditorWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Editor"); self.setFixedSize(1280, 720)
        self.setObjectName("Editor")

        #SelectMode
        self.selectMode: SelectModes = SelectModes.LINE

        #Colors
        self.currentPen: QPen = None
        self.currentBrush: QBrush = None
        self.currentGroup: QGraphicsItemGroup = None
        self.currentItem: QGraphicsItem = None #Can be point or group
        self.initColors()

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

        scene = QGraphicsScene(); scene.setSceneRect(-1000,-1000,2000,2000)
        view = QGraphicsViewCustom(scene); view.itemFocused.connect(lambda scene, filteredGroups, point: self.setCurrentItemByScene(scene, library, filteredGroups, point))

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
        self.currentPen = QPen(); self.currentBrush = QBrush()
        pen = self.currentPen
        brush = self.currentBrush
        pen.setColor(QColor(20, 20, 20)); pen.setWidth(3); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        brush.setColor(QColor(50, 50, 50))
    def paintDefault(self, item: QGraphicsItem): #item is a group or item
        items: list[QGraphicsItem] = self.getAllChildItems(item)
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                ellipse: QGraphicsEllipseItem = it
                ellipse.setBrush(self.currentBrush)
                ellipse.setPen(self.currentPen)
            elif isinstance(it, QGraphicsLineItem):
                line: QGraphicsLineItem = it
                line.setPen(self.currentPen)
    def paintFocused(self, item: QGraphicsItem): #item is a group or item
        brush = QBrush(QColor(220, 0, 0))
        pen = QPen(QColor(220, 0, 0)); pen.setWidth(3); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        items: list[QGraphicsItem] = self.getAllChildItems(item)
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                ellipse: QGraphicsEllipseItem = it
                ellipse.setBrush(brush)
                ellipse.setPen(pen)
            elif isinstance(it, QGraphicsLineItem):
                line: QGraphicsLineItem = it
                line.setPen(pen)
        pass
    #Icons
    def createIcon(self, path: str, w: int, h: int):
        absPath = os.path.dirname(os.path.abspath(__file__))
        iconPath = os.path.join(absPath, *path.split("/"))
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
            newLine = self.createCustomLine(points)
            #replace item everywhere
            self.replaceItemEverywhere(scene, library, self.currentGroup, newLine, points)
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass       
    def operTranslateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = TranslateDialog(figure, self.currentGroup)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newLine = self.createCustomLine(points)
            #update info in library
            self.replaceItemEverywhere(scene, library, self.currentGroup, newLine, points)
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass
    def openScaleDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = ScaleDialog(figure, self.currentGroup)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newLine = self.createCustomLine(points)
            #replace item everywhere
            self.replaceItemEverywhere(scene, library, self.currentGroup, newLine, points)
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass  
    def openRotateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = RotateDialog(figure, self.currentGroup)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newLine = self.createCustomLine(points)
            #replace item everywhere
            self.replaceItemEverywhere(scene, library, self.currentGroup, newLine, points)
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass
    def openMirrorDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentGroup == None:
            return
        
        #Check what figure does editor contain
        figure = self.whatFigure(self.currentGroup)

        dialog = MirrorDialog(figure, self.currentGroup)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            #create new line based at points
            points: list[QPointF] = dialog.points
            newLine = self.createCustomLine(points)
            #add item everywhere
            self.addItemEverywhere(scene, library, newLine, points)
                    
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
    def setCurrentItemByScene(self, scene: QGraphicsScene, library: QListWidget, filteredGroups: list[QGraphicsItemGroup], point: QPointF):
        currentGroup = None
        currentItem = None
        if self.selectMode == SelectModes.POINT:
            currentItem = self.selectFromGroups(filteredGroups, QGraphicsPointGroup)
            currentGroup = self.selectFromGroups(filteredGroups, QGraphicsLineGroup)
            if currentItem is None and self.currentGroup is None:
                return
            elif currentItem is None and self.currentGroup is not None:
                self.paintDefault(self.currentItem)
                self.currentGroup = None
                self.currentItem = None
                library.clearFocus()
            elif currentItem is not None and self.currentGroup is None:
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintFocused(currentItem)
                self.setFocusAtLibraryByItem(library, currentGroup)
            elif currentItem is not None and self.currentGroup is not None:
                self.paintDefault(self.currentGroup)
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintFocused(currentItem)
                self.setFocusAtLibraryByItem(library, currentGroup)
        elif self.selectMode == SelectModes.LINE:
            currentItem = self.selectFromGroups(filteredGroups, QGraphicsLineGroup)
            currentGroup = self.selectFromGroups(filteredGroups, QGraphicsLineGroup)
            if currentItem is None and self.currentGroup is None:
                return
            elif currentItem is None and self.currentGroup is not None:
                self.paintDefault(self.currentGroup)
                self.currentGroup = None
                self.currentItem = None
                library.clearFocus()
            elif currentItem is not None and self.currentGroup is None:
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintFocused(currentGroup)
                self.setFocusAtLibraryByItem(library, currentGroup)
            elif currentItem is not None and self.currentGroup is not None:
                self.paintDefault(self.currentGroup)
                self.currentGroup = currentGroup
                self.currentItem = currentItem
                self.paintFocused(currentItem)
                self.setFocusAtLibraryByItem(library, currentGroup)
        print(f"setCurrentItemByScene has these groups {filteredGroups}")
        print(f"setCurrentItemByScene currentGroup is {currentGroup}")
        print(f"setCurrentItemByScene currentItem is {currentItem}")
    def setCurrentItemByLibrary(self, scene: QGraphicsScene, library: QListWidget, listItem: QListWidgetItem):
        data = listItem.data(Qt.ItemDataRole.UserRole)
        item: QGraphicsItemGroup = data["item"]
        if item == self.currentGroup:
            return
        if item == None:
            if self.currentGroup != None:
                self.paintDefault()
                self.currentGroup = None
                library.clearFocus()
                return
            else:
                return
        if self.currentGroup != None:
            self.paintDefault(self.currentGroup)
        
        self.currentGroup = item
        self.paintFocused(self.currentGroup)
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
    #Scene addition sets the focus!
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
    #Scene replacement sets the focus!
    def replaceItemInLibrary(self, library: QListWidget, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup, points: list[QPointF]):
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == oldItem:
                self.setLibraryItemName(library, oldItem, it.text())
                data["item"] = newItem
                data["points"] = points
                it.setData(Qt.ItemDataRole.UserRole, data)
                break
        self.setFocusAtLibraryByItem(library, newItem)
    def replaceItemInScene(self, scene: QGraphicsScene, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup):
        scene.removeItem(oldItem)
        self.currentGroup = newItem; self.paintFocused(newItem)
        scene.addItem(newItem)
        pass
    def replaceItemEverywhere(self, scene: QGraphicsScene, library: QListWidget, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup, points: list[QPointF]):
        #replace in library
        self.replaceItemInLibrary(library, oldItem, newItem, points)
        #redraw line at scene
        self.replaceItemInScene(scene, oldItem, newItem)
        pass
    #Scene deletion sets the focus!
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
    #Additional methods
    def createCustomLine(self, points: list[QPointF]):
        pointStart = QGraphicsEllipseItem(points[0].x()-5, points[0].y()-5, 10, 10); pointStartGroup = QGraphicsPointGroup(); pointStartGroup.addToGroup(pointStart)
        pointEnd = QGraphicsEllipseItem(points[1].x()-5, points[1].y()-5, 10, 10); pointEndGroup = QGraphicsPointGroup(); pointEndGroup.addToGroup(pointEnd)
        line = QGraphicsLineItem(QLineF(points[0], points[1]))
        group = QGraphicsLineGroup(); group.addToGroup(pointStartGroup); group.addToGroup(pointEndGroup); group.addToGroup(line)
        return group
    def getAllChildItems(self, item: QGraphicsItem):
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