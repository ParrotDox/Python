import sys 
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QSlider,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsPolygonItem)
from PySide6.QtCore import QSize, Qt, Slot, QPointF
from PySide6.QtGui import QBrush, QColor, QPolygonF
class mainWindow(QMainWindow):
    def __init__(self):
        #First configuration
        super().__init__()
        self.setWindowTitle("Robot")
        
        ###Layout
        layout = QHBoxLayout()
        self.layoutSliders = QVBoxLayout()
        self.layoutGraphics = QVBoxLayout()
        layout.addLayout(self.layoutSliders)
        layout.addLayout(self.layoutGraphics)
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        ###Widgets
        #layoutSliders
        self.sliders = [
            QSlider(), #horizontal mvmnt
            QSlider(), #lengthen and shorten
            QSlider(), #axis 1
            QSlider(), #axis 2
            QSlider()] #lengthen and shorten
        self.labels = [
            QLabel(text="Horizontal movement"),
            QLabel(text="Base rod lengthen and shorten"),
            QLabel(text="Axis 1 groups"),
            QLabel(text="Axis 2 groups"),
            QLabel(text="Claw's rod lengthen and shorten")
        ]
        self.sliders[0].setRange(-100,100)
        self.sliders[1].setRange(0,20)
        self.sliders[2].setRange(-90,90)
        self.previousValue2 = self.sliders[2].value()
        self.sliders[3].setRange(-90,90)
        self.previousValue3 = self.sliders[3].value()
        self.sliders[4].setRange(0,10)
        self.previousValue4 = self.sliders[4].value()
        for i in range(len(self.sliders)):
            self.sliders[i].setOrientation(Qt.Orientation.Horizontal)
            self.layoutSliders.addWidget(self.labels[i])
            self.layoutSliders.addWidget(self.sliders[i])

        #####layoutGraphics
        ###Scene and view
        self.scene = QGraphicsScene(0,0,600,400)
        self.view = QGraphicsView(self.scene)
        self.layoutGraphics.addWidget(self.view)
        ###Objects and brushes
        clawShape = QPolygonF()
        clawShape.append(QPointF(280, 150))
        clawShape.append(QPointF(320, 150))
        clawShape.append(QPointF(320, 120))
        clawShape.append(QPointF(315, 120))
        clawShape.append(QPointF(315, 145))
        clawShape.append(QPointF(285, 145))
        clawShape.append(QPointF(285, 120))
        clawShape.append(QPointF(280, 120))
        self.parts: QGraphicsItem = [
            QGraphicsRectItem(250,250,100,50),  #Body
            QGraphicsEllipseItem(255,285,25,25),#WheelL
            QGraphicsEllipseItem(320,285,25,25),#WheelR
            QGraphicsRectItem(290,230,20,40),   #BaseRod
            QGraphicsEllipseItem(285,215,30,30),#BaseRodJoint
            QGraphicsRectItem(290,190,20,40),   #MediumRod
            QGraphicsEllipseItem(285,175,30,30),#MediumRodJoint
            QGraphicsRectItem(290,150,20,40),   #ClawRod
            QGraphicsPolygonItem(clawShape)
        ]
        self.groups = [
            QGraphicsItemGroup(),   #Body, Wheels, other groups
            QGraphicsItemGroup(),   #BaseRod, BaseRodJoint, other group
            QGraphicsItemGroup(),   #MediumRod, MediumRodJoint, other group
            QGraphicsItemGroup()    #ClawRod, Claw
        ]
        self.groups[0].addToGroup(self.parts[0])    #Body
        self.groups[0].addToGroup(self.parts[1])    #WheelL
        self.groups[0].addToGroup(self.parts[2])    #WheelR
        self.groups[1].addToGroup(self.parts[3])    #BaseRod
        self.groups[2].addToGroup(self.parts[4])    #BaseRodJoint
        self.groups[2].addToGroup(self.parts[5])    #MediumRod
        self.groups[3].addToGroup(self.parts[6])    #MediumRodJoint
        self.groups[3].addToGroup(self.parts[7])    #ClawRod
        self.groups[3].addToGroup(self.parts[8])    #ClawRod

        self.groups[0].addToGroup(self.groups[1])
        self.groups[1].addToGroup(self.groups[2])
        self.groups[2].addToGroup(self.groups[3])

        brushes: QBrush = [
            QBrush(QColor(17, 63, 103)),  #brushDarkBlue
            QBrush(QColor(52, 105, 154)), #brushMediumBlue
            QBrush(QColor(88, 160, 200))  #brushLightBlue
        ]
        self.parts[0].setBrush(brushes[0])
        self.parts[1].setBrush(brushes[1])
        self.parts[2].setBrush(brushes[1])
        self.parts[3].setBrush(brushes[2])
        self.parts[4].setBrush(brushes[2])
        self.parts[5].setBrush(brushes[2])
        self.parts[6].setBrush(brushes[2])
        self.parts[7].setBrush(brushes[2])
        self.parts[8].setBrush(brushes[2])

        ###Connecting signals and slots
        self.sliders[0].valueChanged.connect(lambda: self.move(self.groups[0], "H", self.sliders[0]))
        self.sliders[1].valueChanged.connect(lambda: self.move(self.groups[1], "V", self.sliders[1]))
        self.sliders[2].valueChanged.connect(lambda: self.rotate(self.groups[2], self.sliders[2]))
        self.sliders[3].valueChanged.connect(lambda: self.rotate(self.groups[3], self.sliders[3]))
        self.sliders[4].valueChanged.connect(lambda: self.move(self.groups[3], "None", self.sliders[4]))

        #Drawing at scene
        self.scene.addItem(self.groups[0])
    @Slot()
    def move(self, group: QGraphicsItemGroup, orientation, slider: QSlider):
        if(orientation == "H"):
            displacementX = slider.value()
            group.setPos(displacementX, group.y())
        elif(orientation == "V"):
            displacementY = slider.value()
            group.setPos(group.x(), displacementY * -1)
        elif(orientation == "None"):
            delta = slider.value() - self.previousValue4
            print(delta, self.previousValue4)
            group.moveBy(0, delta * -1)
            self.previousValue4 = slider.value()
        
    @Slot()
    def rotate(self, group: QGraphicsItemGroup, slider: QSlider):
        joint: QGraphicsItem
        jointCenterCoordGlobal: QPointF
        jointCenterCoordLocal: QPointF
        if  group == self.groups[2]:
            joint = self.parts[4]
            pass
        if group == self.groups[3]:
            joint = self.parts[6]
            pass
        jointCenterCoordGlobal = joint.mapToScene(joint.boundingRect().center())
        jointCenterCoordLocal = group.mapFromScene(jointCenterCoordGlobal)
        group.setTransformOriginPoint(jointCenterCoordLocal)
        group.setRotation(slider.value())
        
def main():
    app = QApplication(sys.argv)
    widget = mainWindow()
    widget.show()
    sys.exit(app.exec())
main()