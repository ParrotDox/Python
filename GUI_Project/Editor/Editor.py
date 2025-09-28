import sys
from LineDialog import LineDialog
from LineInfo import LineInfo
from QGraphicsCustom import QGraphicsCustomScene
from PySide6.QtCore import Qt, Slot, QObject, QEvent, QLineF
from PySide6.QtGui import QPen, QBrush, QColor, QTransform
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QStyle,
    QMainWindow,
    QWidget,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QLayout,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsLineItem
)

class EditorWindow(QMainWindow):
    def __init__(self):
        ###Widget init and layouts
        super().__init__()
        self.setWindowTitle("Editor")
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        ###local variables
        #Lines
        self.lines: list[LineInfo] = []
        self.focusedLineInfo: LineInfo = None
        #Pens
        self.specialPens = []
        pen = QPen(QColor(255, 0, 0)); pen.setWidth(3); self.specialPens.append(pen)
        self.defaultPen = QPen(QColor(20,20,20)); self.defaultPen.setWidth(3)
        ###Layouts
        layouts: list[QLayout] = self.__createLayouts(mainWidget)   # 0 - main | 1 - viewport | 2 - actionPanel
        ###Add widgets and layouts
        self.__DIC(layouts)
        self.__createGrid()
        ###Signals and slots
        self.btnAdd.clicked.connect(self.createLine)
        self.btnUpd.clicked.connect(self.updateLine)
        self.btnDel.clicked.connect(self.deleteLine)
        self.scene.clickedOnItem.connect(self.focusOnLine)
    ### Private
    #Create layouts and insert layouts into layouts
    def __createLayouts(self, mainWidget: QWidget):
        self.mainLayout = QHBoxLayout()
        self.viewportLayout = QVBoxLayout()
        self.actionPanelLayout = QVBoxLayout()
        self.actionPanelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainWidget.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.viewportLayout)
        self.mainLayout.addLayout(self.actionPanelLayout)

        layouts = []
        layouts.append(self.mainLayout)
        layouts.append(self.viewportLayout)
        layouts.append(self.actionPanelLayout)
        return layouts
    #Define Init Connect elements to layouts
    def __DIC(self, layouts: list[QLayout]):
        #1 - viewport
        self.scene = QGraphicsCustomScene(0,0,600,400)
        self.scene.setBackgroundBrush(QColor(200,200,200))
        self.view = QGraphicsView(self.scene)
        self.view.scale(1, -1)
        self.scene.setSceneRect(-self.view.width()/2, -self.view.height()/2, self.view.width(), self.view.height()) #Centered viewport
        #2 - actionpanel
        self.btnAdd = QPushButton("Create line")
        self.btnUpd = QPushButton("Update line")
        self.btnDel = QPushButton("Delete line")

        #Connect elements with layouts
        layouts[1].addWidget(self.view)
        layouts[2].addWidget(self.btnAdd)
        layouts[2].addWidget(self.btnUpd)
        layouts[2].addWidget(self.btnDel)
        return True
    #Creates grid at scene
    def __createGrid(self):
        width = self.scene.width()
        height = self.scene.height()
        startX = width/2 * -1
        startY = height/2 * -1
        #Horizontal lines
        for i in range(0, int(height)+1, 20):
            y = startY + i
            line = QGraphicsLineItem(startX, y, startX + width, y)
            if y == 0:
                pen = QPen()
                pen.setWidth(4)
                line.setPen(pen)
            self.scene.addItem(line)
        #Vertical lines
        for i in range(0, int(width)+1, 20):
            x = startX + i
            line = QGraphicsLineItem(x, startY, x, startY + height)
            if x == 0:
                pen = QPen()
                pen.setWidth(4)
                line.setPen(pen)
            self.scene.addItem(line)
        pass 
    #Dialog -> creates LineInfo using k and b
    def __createLineInfo(self):
        dialog = LineDialog()
        if dialog.exec() == QDialog.Accepted:
            k, b, x1, y1, x2, y2 = dialog.result
            line = QLineF(x1,y1,x2,y2)
            lineGE = QGraphicsLineItem(line)
            lineGE.setPen(self.defaultPen)
            lineInfo = LineInfo(k, b, lineGE)
            lineInfo.defaultPen = self.defaultPen
            return lineInfo
        else:
            return None
    def __addLine(self, lineInfo: LineInfo):
        self.scene.addItem(lineInfo.lineGE)
        self.lines.append(lineInfo)
    #Replaces focusedLine with sample line
    def __replaceFocusedLine(self, lineInfo: LineInfo):
        if self.focusedLineInfo == None:
            return
        for infoSample in self.lines:
            if infoSample == self.focusedLineInfo:
                self.scene.removeItem(infoSample.lineGE)
                self.lines.remove(infoSample)
                break
        self.__addLine(lineInfo)
        self.focusedLineInfo = None
    ### Public
    def createLine(self):
        lineInfo: LineInfo = self.__createLineInfo()
        if lineInfo != None:
            self.__addLine(lineInfo)
        else:
            print("creating rejected")
    #Called when the object in scene is focused (Slot)
    def focusOnLine(self, item):
        for infoSamle in self.lines:
            if item == infoSamle.lineGE:
                if(self.focusedLineInfo != None):
                    self.focusedLineInfo.setDefaultPen()
                self.focusedLineInfo = infoSamle
                self.focusedLineInfo.lineGE.setPen(self.specialPens[0])
                break
    def updateLine(self):
        #If has no focused line
        if self.focusedLineInfo == None:
            return
        #If has focused line
        lineInfo: LineInfo = self.__createLineInfo()
        if lineInfo != None:
            self.__replaceFocusedLine(lineInfo)
        else:
            print("updating rejected")
            
    def deleteLine(self):
        if self.focusedLineInfo == None:
            return
        for infoSample in self.lines:
            if self.focusedLineInfo == infoSample:
                self.scene.removeItem(infoSample.lineGE)
                self.lines.remove(infoSample)
                self.focusedLineInfo = None
                break



def main():
    app = QApplication()
    editor = EditorWindow()
    editor.show()
    sys.exit(app.exec())
main()