from Create import CreateDialog
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

    currentPen: QPen = None
    currentBrush: QBrush = None
    currentObject = None

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Editor"); self.setFixedSize(1280, 720)
        self.setObjectName("Editor")

        self.initColors()

    def initUI(self):
        #widgets
        buttonCreate = QPushButton("C"); buttonCreate.setFixedSize(35,35); buttonCreate.clicked.connect(lambda: self.openCreateDialog(scene, objectsList))
        buttonUpdate = QPushButton("U"); buttonUpdate.setFixedSize(35,35)
        buttonDelete = QPushButton("D"); buttonDelete.setFixedSize(35,35)

        buttonTranslate = QPushButton("T"); buttonTranslate.setFixedSize(35,35)
        buttonScale = QPushButton("S"); buttonScale.setFixedSize(35,35)
        buttonRotate = QPushButton("R"); buttonRotate.setFixedSize(35,35)
        buttonMirror = QPushButton("M"); buttonMirror.setFixedSize(35,35)

        scene = QGraphicsScene(); scene.setSceneRect(-1000,-1000,2000,2000)
        view = QGraphicsViewCustom(scene); view.itemFocused.connect(self.setCurrentObject)

        objectsLabel = QLabel("Objects")
        objectsList = QListWidget()

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

        objectsLayout.addWidget(objectsLabel); objectsLayout.addWidget(objectsList)

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
    def openCreateDialog(self, scene: QGraphicsScene, objectsList: QListWidget):
        dialog = CreateDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            if dialog.dimension == 0:
                #Add to scene
                points: list[QPointF] = dialog.points
                line = self.createCustomLine(points)
                scene.addItem(line)
                #Add to objects library
                data = {
                    "item": line,
                    "points": points
                }
                item = QListWidgetItem(f"Line {line} {points[0]} {points[1]}")
                item.setData(Qt.ItemDataRole.UserRole, data)
                objectsList.addItem(item)
                
            elif dialog.dimension == 1:
                pass
        else:
            return
    def setCurrentObject(self, scene: QGraphicsScene, item: QGraphicsItem):
        items = scene.items()
        for it in items:
            if it == item:
                line: QGraphicsLineItem = it
                self.currentObject = line
                print(f"Current object {line}")
    def createCustomLine(self, points: list[QPointF]):
        pointStart = QGraphicsEllipseItem(points[0].x()-5, points[0].y()-5, 10, 10)
        pointEnd = QGraphicsEllipseItem(points[1].x()-5, points[1].y()-5, 10, 10)
        line = QGraphicsLineItem(QLineF(points[0], points[1]))
        group = QGraphicsItemGroup(); group.addToGroup(pointStart); group.addToGroup(pointEnd); group.addToGroup(line)
        return  group