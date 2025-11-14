# view_3d_projection.py
import sys, math
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt

# ---------- твой класс ----------
class matrixTransformationClass:
    def __init__(self):
        self.points = [
            [0,0,3],[1,0,3],[2,0,3],[3,0,3],[3,0,0],[0,0,0],
            [1,1,3],[2,1,3],[0,2,3],[3,2,3],[3,2,0],[0,2,0],[2,3,0],[2,3,3]
        ]
    @staticmethod
    def useMatrix(points, matrix):
        out=[]
        for x,y,z in points:
            x1=matrix[0][0]*x+matrix[0][1]*y+matrix[0][2]*z+matrix[0][3]
            y1=matrix[1][0]*x+matrix[1][1]*y+matrix[1][2]*z+matrix[1][3]
            z1=matrix[2][0]*x+matrix[2][1]*y+matrix[2][2]*z+matrix[2][3]
            w = matrix[3][0]*x+matrix[3][1]*y+matrix[3][2]*z+matrix[3][3]
            if w != 0: out.append([x1/w, y1/w, z1/w])
            else: out.append([x1,y1,z1])
        return out
    @staticmethod
    def rotationX(a):
        c,s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return [[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]]
    @staticmethod
    def rotationY(a):
        c,s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return [[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]]
    @staticmethod
    def orthographicProjection():
        return [[1,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,0,1]]
    @staticmethod
    def cameraZ(zv):
        return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,-1/zv,1]]

# ---------- исходные данные ----------
LINES = [
 ("A","B"),("B","C"),("C","D"),("D","E"),("E","F"),("A","F"),
 ("A","G"),("B","M"),("C","N"),("D","H"),("E","I"),("F","J"),
 ("M","N"),("G","H"),("H","I"),("I","J"),("G","J"),("G","L"),
 ("L","H"),("J","K"),("K","I"),("L","K")
]
POINTS_LABELS = ["A","B","C","D","E","F","M","N","G","H","I","J","K","L"]

# ---------- получение проекции ----------
a,b,camZ = 30,60,8
f = matrixTransformationClass()
pts = f.points
pts = f.useMatrix(pts, f.rotationX(a))
pts = f.useMatrix(pts, f.rotationY(b))
pts = f.useMatrix(pts, f.cameraZ(camZ))
pts = f.useMatrix(pts, f.orthographicProjection())

# ---------- PySide отрисовка ----------
app = QApplication(sys.argv)
scene = QGraphicsScene()
view = QGraphicsView(scene)
view.resize(800,600)
view.setWindowTitle("3D -> Orthographic projection (rotX=30, rotY=60, camZ=8)")

# Сетка
pen_grid = QPen(QColor(220,220,220))
for i in range(-10,11):
    scene.addLine(-10,i,10,i,pen_grid)
    scene.addLine(i,-10,i,10,pen_grid)
# Оси
scene.addLine(-10,0,10,0,QPen(Qt.black))
scene.addLine(0,-10,0,10,QPen(Qt.black))

# Масштаб
scale = 80
# Центр
cx,cy = 400,300

# Словарь точек
P = {name:(p[0],p[1]) for name,p in zip(POINTS_LABELS, pts)}

# Линии
pen_edge = QPen(QColor(50,80,200))
for a,b in LINES:
    if a in P and b in P:
        x1,y1=P[a]; x2,y2=P[b]
        scene.addLine(cx+x1*scale, cy-y1*scale, cx+x2*scale, cy-y2*scale, pen_edge)

# Точки
for name,(x,y) in P.items():
    scene.addEllipse(cx+x*scale-3, cy-y*scale-3, 6,6, QPen(Qt.black), QBrush(Qt.red))
    text = scene.addText(name, QFont("Arial",8))
    text.setPos(cx+x*scale+4, cy-y*scale-4)

view.setBackgroundBrush(QColor(245,245,245))
view.show()
sys.exit(app.exec())
