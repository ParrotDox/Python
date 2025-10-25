
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGraphicsScene,
    QGraphicsView,
    QVBoxLayout,
    QGraphicsLineItem,
    QGraphicsEllipseItem)
from PySide6.QtGui import QColor,QPen, QBrush, QTransform

scale = 50

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def calcA3A2A1A0(x1, x2, x3, x4):
    a3 = (-x1 + 3*x2 - 3*x3 + x4) / 6
    a2 = (x1 - 2*x2 + x3) / 2
    a1 = (x3 - x1) / 2
    a0 = (x1+4*x2+x3) / 6
    return  [a0, a1, a2, a3]

def calcB3B2B1B0(y1, y2, y3, y4):
    b3 = (-y1 + 3*y2 - 3*y3 + y4) / 6
    b2 = (y1 - 2*y2 + y3) / 2
    b1 = (y3 - y1) / 2
    b0 = (y1+4*y2+y3) / 6
    return  [b0, b1, b2, b3]

def calcX(coefsA, t):
    x = coefsA[0] + coefsA[1]*t + coefsA[2]*t**2 + coefsA[3]*t**3
    return x

def calcY(coefsB, t):
    y = coefsB[0] + coefsB[1]*t + coefsB[2]*t**2 + coefsB[3]*t**3
    return y

rawPoints = [point(3,1),point(1,2),point(2,4),point(1,5),point(2,6),point(5,5),point(6,3),point(7,4),point(10,3),point(8,1)]
bakedPoints = []
for i in range(len(rawPoints)):
    q = len(rawPoints)
    cake = [rawPoints[i%q], rawPoints[(i+1)%q], rawPoints[(i+2)%q], rawPoints[(i+3)%q]]
    for d in range(0, 11):
        t = d / 10
        x = calcX(calcA3A2A1A0(cake[0].x*scale, cake[1].x*scale, cake[2].x*scale, cake[3].x*scale), t)
        y = calcY(calcB3B2B1B0(cake[0].y*scale, cake[1].y*scale, cake[2].y*scale, cake[3].y*scale), t)
        bakedPoints.append(point(x,y))

#app, widgets
app = QApplication([])
mainWindow = QWidget(); mainWindow.setFixedSize(900, 700)
scene = QGraphicsScene(); 
view = QGraphicsView(); view.setScene(scene); view.setTransform(QTransform(1,0,0,0,-1,0,0,0,1))

#Design
mainLayout = QVBoxLayout()
mainLayout.addWidget(view)
mainWindow.setLayout(mainLayout)

#functions
def setSpline(scene: QGraphicsScene, rawPoints: list[point],bakedPoints: list[point]):
    points = []
    for pt in rawPoints:
        points.append(point(pt.x*scale, pt.y*scale))
    brush = QBrush(QColor(0,0,0))
    pen = QPen(QColor(0,0,0))
    pen.setWidth(2)
    for pt in points:
        ptObj = QGraphicsEllipseItem(pt.x-scale/5/2,pt.y-scale/5/2,scale/5,scale/5)
        ptObj.setPen(pen)
        ptObj.setBrush(brush)
        scene.addItem(ptObj)

    for i in range(len(bakedPoints)-1):
        prev = bakedPoints[i]
        next = bakedPoints[i+1]
        line = QGraphicsLineItem(prev.x, prev.y, next.x, next.y)
        line.setPen(pen)
        scene.addItem(line)

def drawGrid(scene: QGraphicsScene, scale):
    pen = QPen(QColor(0,0,0))
    pen.setWidth(2)
    for d in range(-100*scale, 100*scale, scale):
        line = QGraphicsLineItem(d,-10000,d,10000)
        line.setPen(pen)
        scene.addItem(line)
        line = QGraphicsLineItem(-10000,d,10000,d)
        line.setPen(pen)
        scene.addItem(line)

    pen.setColor(QColor(220,0,0))
    pen.setWidth(3)
    Ox = QGraphicsLineItem(-10000, 0, 10000, 0)
    Oy = QGraphicsLineItem(0, -10000, 0, 10000)
    Ox.setPen(pen)
    Oy.setPen(pen)
    scene.addItem(Ox)
    scene.addItem(Oy)
#Show/run app
setSpline(scene, rawPoints, bakedPoints)
drawGrid(scene, scale)
mainWindow.show()
app.exec()