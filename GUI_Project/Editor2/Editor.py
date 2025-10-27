from CUD.Create import CreateDialog
from CUD.Update import UpdateDialog
from TSRM.Translate import TranslateDialog
from TSRM.Scale import ScaleDialog
from TSRM.Rotate import RotateDialog
from FIGURES import Figures
from ViewCustom import QGraphicsViewCustom
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
from PySide6.QtGui import QPen, QBrush, QColor

class EditorWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Editor"); self.setFixedSize(1280, 720)
        self.setObjectName("Editor")

        self.currentPen: QPen = None
        self.currentBrush: QBrush = None
        self.currentObject = None
        self.initColors()

    def initUI(self):
        #widgets
        buttonCreate = QPushButton("C"); buttonCreate.setFixedSize(35,35); buttonCreate.clicked.connect(lambda: self.openCreateDialog(scene, library))
        buttonUpdate = QPushButton("U"); buttonUpdate.setFixedSize(35,35); buttonUpdate.clicked.connect(lambda: self.openUpdateDialog(scene, library))
        buttonDelete = QPushButton("D"); buttonDelete.setFixedSize(35,35); buttonDelete.clicked.connect(lambda: self.deleteCurrentObject(scene, library))

        buttonTranslate = QPushButton("T"); buttonTranslate.setFixedSize(35,35); buttonTranslate.clicked.connect(lambda: self.operTranslateDialog(scene, library))
        buttonScale = QPushButton("S"); buttonScale.setFixedSize(35,35); buttonScale.clicked.connect(lambda: self.operScaleDialog(scene, library))
        buttonRotate = QPushButton("R"); buttonRotate.setFixedSize(35,35); buttonRotate.clicked.connect(lambda: self.openRotateDialog(scene, library))
        buttonMirror = QPushButton("M"); buttonMirror.setFixedSize(35,35)

        scene = QGraphicsScene(); scene.setSceneRect(-1000,-1000,2000,2000)
        view = QGraphicsViewCustom(scene); view.itemFocused.connect(lambda scene, item: self.setCurrentObjectByScene(scene, library, item))

        objectsLabel = QLabel("Objects")
        library = QListWidget(); library.itemClicked.connect(lambda item: self.setCurrentObjectByLibrary(scene, library, item))

        #layouts
        mainLayout = QHBoxLayout()

        workspaceLayout = QVBoxLayout()
        libraryLayout = QHBoxLayout()

        actionsLayout = QHBoxLayout(); actionsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cudLayout = QHBoxLayout()
        tsrmLayout = QHBoxLayout()

        objectsLayout = QVBoxLayout()

        mainLayout.addLayout(workspaceLayout); mainLayout.addLayout(libraryLayout)
        mainLayout.setStretchFactor(workspaceLayout, 3); mainLayout.setStretchFactor(libraryLayout, 1)

        actionsLayout.addLayout(cudLayout); actionsLayout.addSpacing(15); actionsLayout.addLayout(tsrmLayout)

        libraryLayout.addLayout(objectsLayout)

        cudLayout.addWidget(buttonCreate); cudLayout.addWidget(buttonUpdate); cudLayout.addWidget(buttonDelete);
        tsrmLayout.addWidget(buttonTranslate); tsrmLayout.addWidget(buttonScale); tsrmLayout.addWidget(buttonRotate); tsrmLayout.addWidget(buttonMirror)

        workspaceLayout.addLayout(actionsLayout); workspaceLayout.addWidget(view)

        objectsLayout.addWidget(objectsLabel); objectsLayout.addWidget(library)

        self.setLayout(mainLayout)


        #StyleSheets
        styleSheet = ""
        self.setStyleSheet(styleSheet)
        pass
    def initColors(self):
        self.currentPen = QPen(); self.currentBrush = QBrush()
        pen = self.currentPen
        brush = self.currentBrush
        pen.setColor(QColor(20, 20, 20)); pen.setWidth(3); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        brush.setColor(QColor(50, 50, 50))
    def paintDefault(self):
        items: list[QGraphicsItem] = self.currentObject.childItems()
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                ellipse: QGraphicsEllipseItem = it
                ellipse.setBrush(self.currentBrush)
                ellipse.setPen(self.currentPen)
            elif isinstance(it, QGraphicsLineItem):
                line: QGraphicsLineItem = it
                line.setPen(self.currentPen)
    def paintFocused(self):
        brush = QBrush(QColor(220, 0, 0))
        pen = QPen(QColor(220, 0, 0)); pen.setWidth(3); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        items: list[QGraphicsItem] = self.currentObject.childItems()
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                ellipse: QGraphicsEllipseItem = it
                ellipse.setBrush(brush)
                ellipse.setPen(pen)
            elif isinstance(it, QGraphicsLineItem):
                line: QGraphicsLineItem = it
                line.setPen(pen)
        pass
    def openCreateDialog(self, scene: QGraphicsScene, library: QListWidget):
        dialog = CreateDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            if dialog.figure == Figures.LINE:
                #Add to scene
                points: list[QPointF] = dialog.points
                line = self.createCustomLine(points) #line is a group!
                scene.addItem(line)
                
                #Add item to library
                self.addItemToLibrary(library, line, points)
                
            elif dialog.figure == Figures.CUBE:
                pass
        else:
            return
    def openUpdateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentObject == None:
            return
        
        items: list[QGraphicsItem] = self.currentObject.childItems()
        figure = self.whatFigure(items)
        
        dialog = UpdateDialog(figure)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            points: list[QPointF] = dialog.points
            newLine = self.updateCustomLine(self.currentObject, points)
            #update info in library
            self.replaceItemInLibrary(library, self.currentObject, newLine, points)
            #redraw line at scene
            scene.removeItem(self.currentObject)
            self.currentObject = newLine
            scene.addItem(newLine)
                    
        if result == QDialog.DialogCode.Accepted and figure == Figures.CUBE:
            #TODO
            pass       
    def openRotateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentObject == None:
            return
        
        #Check what figure does editor contain
        items: list[QGraphicsItem] = self.currentObject.childItems()
        figure = self.whatFigure(items)

        dialog = RotateDialog(figure, self.currentObject)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            #update text in widgetList element
            self.setLibraryItemName(library, self.currentObject, "Line rotated ")
        pass
    def operTranslateDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentObject == None:
            return
        
        #Check what figure does editor contain
        items: list[QGraphicsItem] = self.currentObject.childItems()
        figure = self.whatFigure(items)

        dialog = TranslateDialog(figure, self.currentObject)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.setLibraryItemName(library, self.currentObject, "Line translated ")
        pass
    def operScaleDialog(self, scene: QGraphicsScene, library: QListWidget):
        if self.currentObject == None:
            return
        
        #Check what figure does editor contain
        items: list[QGraphicsItem] = self.currentObject.childItems()
        figure = self.whatFigure(items)

        dialog = ScaleDialog(figure, self.currentObject)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and figure == Figures.LINE:
            self.setLibraryItemName(library, self.currentObject, f"Line scaled ")
        pass
    
    def deleteCurrentObject(self, scene: QGraphicsScene, library: QListWidget):
        #remove from library
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for i in range(len(listItems)):
            data = listItems[i].data(Qt.ItemDataRole.UserRole)
            if data["item"] == self.currentObject:
                library.takeItem(i) #removing from the library
                library.clearFocus()
                break
        #remove from scene
        scene.removeItem(self.currentObject)
        self.currentObject = None
        pass
    def setCurrentObjectByScene(self, scene: QGraphicsScene, library: QListWidget, item: QGraphicsItemGroup):
        if item == self.currentObject:
            print(f"setCurrentObjByScene: item({item}) == self.currentObj({self.currentObject})")
            return
        if item == None:
            if self.currentObject != None:
                self.paintDefault()
                self.currentObject = None
                library.clearFocus()
                return
            else:
                return
        if self.currentObject != None:
            self.paintDefault()

        self.currentObject = item
        self.paintFocused()

        #Set focus at library
        self.setFocusAtLibraryByItem(library, item)

        print(f"Current object {item}")
    def setCurrentObjectByLibrary(self, scene: QGraphicsScene, library: QListWidget, listItem: QListWidgetItem):
        data = listItem.data(Qt.ItemDataRole.UserRole)
        item: QGraphicsItemGroup = data["item"]
        if item == self.currentObject:
            return
        if item == None:
            if self.currentObject != None:
                self.paintDefault()
                self.currentObject = None
                library.clearFocus()
                return
            else:
                return
        if self.currentObject != None:
            self.paintDefault()
        
        self.currentObject = item
        self.paintFocused()
        print(f"Current object {item}")   
    
    def setFocusAtLibraryByItem(self, library: QListWidget, item: QGraphicsItemGroup):
        print(item)
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == item:
                print("setCurrentObject:", item, "scene:", bool(item.scene()), "children:", len(data["item"].childItems()))
                library.setCurrentItem(it)
                library.setFocus()
                break
    def addItemToLibrary(self, library: QListWidget, item: QGraphicsItemGroup, points: list[QPointF]):
        data = {
                    "item": item,
                    "points": points
                }
        item = QListWidgetItem(f"Item: {item}")
        item.setData(Qt.ItemDataRole.UserRole, data)
        library.addItem(item)
    def replaceItemInLibrary(self, library: QListWidget, oldItem: QGraphicsItemGroup, newItem: QGraphicsItemGroup, points: list[QPointF]):
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == oldItem:
                it.setText(f"Line updated {data['item']}")
                data["item"] = newItem
                data["points"] = points
                it.setData(Qt.ItemDataRole.UserRole, data)
                break
    def setLibraryItemName(self, library: QListWidget, item: QGraphicsItemGroup, text: str):
        #update text in widgetList element
        listItems = library.findItems("", Qt.MatchFlag.MatchContains)
        for it in listItems:
            data = it.data(Qt.ItemDataRole.UserRole)
            if data["item"] == item:
                it.setText(f"{text} {data['item']}")
            break
    
    def createCustomLine(self, points: list[QPointF]):
        pointStart = QGraphicsEllipseItem(points[0].x()-5, points[0].y()-5, 10, 10)
        pointEnd = QGraphicsEllipseItem(points[1].x()-5, points[1].y()-5, 10, 10)
        line = QGraphicsLineItem(QLineF(points[0], points[1]))
        group = QGraphicsItemGroup(); group.addToGroup(pointStart); group.addToGroup(pointEnd); group.addToGroup(line)
        return group
    def updateCustomLine(self, line: QGraphicsItemGroup, points: list[QPointF]):
        pointStart: QGraphicsEllipseItem = line.childItems()[0];  pointStart.setRect(points[0].x()-5, points[0].y()-5, 10, 10)
        pointEnd: QGraphicsEllipseItem = line.childItems()[1]; pointEnd.setRect(points[1].x()-5, points[1].y()-5, 10, 10)
        lineItem: QGraphicsLineItem = line.childItems()[2]; lineItem.setLine(QLineF(points[0], points[1]));
        group = QGraphicsItemGroup(); group.addToGroup(pointStart); group.addToGroup(pointEnd); group.addToGroup(lineItem)
        return group
    def whatFigure(self, items):
        if items == None:
            return None
        elif len(items) == 1:
            return Figures.POINT
        elif len(items) == 3:
            return Figures.LINE
        else:
            return Figures.CUBE