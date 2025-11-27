import random
import math
from PySide6.QtWidgets import (
    QApplication,
    QWidget, 
    QLabel,
    QSlider, 
    QGraphicsView, 
    QGraphicsScene,
    QGraphicsLineItem,
    QHBoxLayout,
    QGridLayout)
from PySide6.QtCore import Qt, QRectF
class vertex:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        if isinstance(other, vertex):
            x = self.x + other.x
            y = self.y + other.y
            z = self.z + other.z
            return vertex(x, y, z)
        if isinstance(other, (int, float)):
            x = self.x + other
            y = self.y + other
            z = self.z + other
            return vertex(x, y, z)

    def __sub__(self, other):
        if isinstance(other, vertex):
            x = self.x - other.x
            y = self.y - other.y
            z = self.z - other.z
            return vertex(x, y, z)
        if isinstance(other, (int, float)):
            x = self.x - other
            y = self.y - other
            z = self.z - other
            return vertex(x, y, z)

    def __truediv__(self, other):
        if isinstance(other, vertex):
            x = self.x / other.x
            y = self.y / other.y
            z = self.z / other.z
            return vertex(x, y, z)
        if isinstance(other, (int, float)):
            x = self.x / other
            y = self.y / other
            z = self.z / other
            return vertex(x, y, z)

    def setXYZ(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class chunk:
    def __init__(self, data: list[list[vertex]]):
        self.data = data

class transform3D():
    @staticmethod
    def useMatrix(data: list[list[vertex]], matrix: list[list[float]]) -> list[list[vertex]]:
        new_data:list[list[vertex]] = []
        for row in data:
            new_row: list[vertex] = []
            for v in row:
                x, y, z =  v.x, v.y, v.z
                x_new = matrix[0][0]*x + matrix[0][1]*y + matrix[0][2]*z + matrix[0][3]*1
                y_new = matrix[1][0]*x + matrix[1][1]*y + matrix[1][2]*z + matrix[1][3]*1
                z_new = matrix[2][0]*x + matrix[2][1]*y + matrix[2][2]*z + matrix[2][3]*1
                w_new = matrix[3][0]*x + matrix[3][1]*y + matrix[3][2]*z + matrix[3][3]*1
        
                if w_new != 0:
                    new_row.append(vertex(x_new/w_new, y_new/w_new, z_new/w_new))
                else:
                    new_row.append(vertex(x_new, y_new, z_new))
            new_data.append(new_row)
         
        return new_data
    @staticmethod
    def translateXYZ(x, y, z):
        return [
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def scaleXYZ(x, y, z):
        return [
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def rotationX(angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return [
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def rotationY(angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return [
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def rotationZ(angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return [
            [c, s, 0, 0],
            [-s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def orthographicProjection():
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def cameraZ(Zvalue):
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, -1/Zvalue, 1]
        ]

def diamondSquare(chunk: chunk, roughness: float):
    """
    Корректная реализация алгоритма Diamond–Square.
    Работает напрямую с chunk.data (матрица vertex).
    Размер chunk.data должен быть 2^n + 1 (например 17x17).
    """

    data = chunk.data
    size = len(data)
    step = size - 1
    scale = roughness

    # START with initial random displacement on corners:
    def rand(scale):
        return random.uniform(-scale, scale)

    # === Основной цикл ===
    while step > 1:

        half = step // 2

        # ===== DIAMOND step =====
        for y in range(half, size - 1, step):
            for x in range(half, size - 1, step):

                A = data[y - half][x - half]
                B = data[y - half][x + half]
                C = data[y + half][x + half]
                D = data[y + half][x - half]

                avgZ = (A.z + B.z + C.z + D.z) * 0.25
                offset = rand(scale * step)

                data[y][x].z = avgZ + offset

        # ===== SQUARE step =====
        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):

                values = []
                if y - half >= 0:        values.append(data[y - half][x].z)
                if y + half < size:      values.append(data[y + half][x].z)
                if x - half >= 0:        values.append(data[y][x - half].z)
                if x + half < size:      values.append(data[y][x + half].z)

                avgZ = sum(values) / len(values)
                offset = rand(scale * step)

                data[y][x].z = avgZ + offset

        # уменьшение шага и roughness
        step //= 2
        scale *= 0.5

def processChunk(chunk: chunk, roughness):

    data = chunk.data
    n = len(data)
    center = n // 2

    # corners
    A = data[0][0]
    B = data[0][n - 1]
    C = data[n - 1][n - 1]
    D = data[n - 1][0]

    # square center
    center_v = data[center][center]
    length = (B - A).x

    center_v.setXYZ(*applyDiamond([A, B, C, D], length, roughness))

    # diamond — edge midpoints
    M = data[0][center]
    M.setXYZ(*applyDiamond([A, center_v, B], length, roughness))

    N = data[center][n - 1]
    N.setXYZ(*applyDiamond([B, center_v, C], length, roughness))

    P = data[n - 1][center]
    P.setXYZ(*applyDiamond([C, center_v, D], length, roughness))

    Q = data[center][0]
    Q.setXYZ(*applyDiamond([A, center_v, D], length, roughness))

def applyDiamond(vertices, length, roughness):
    avg = vertex(0,0,0)
    for v in vertices:
        avg += v
    avg = avg / len(vertices)

    rnd = random.uniform(-length * roughness, length * roughness)

    return avg.x, avg.y, avg.z + rnd

def generate_chunk(size: int, spacing: float = 1.0) -> chunk:
    """
    Генерирует квадратный chunk размером size x size.
    spacing — расстояние между вершинами по X и Y.
    """
    data = [[vertex(x * spacing, y * spacing, 0.0) for x in range(size)] for y in range(size)]
    return chunk(data)

def generate_triangle_lines(chunk):
    data = chunk.data
    lines = []

    for i in range(len(data) - 1):
        for j in range(len(data) - 1):
            A = data[i][j]
            B = data[i][j+1]
            C = data[i+1][j]
            D = data[i+1][j+1]

            # Треугольник ABD
            lines.append(QGraphicsLineItem(A.x, A.y, B.x, B.y))
            lines.append(QGraphicsLineItem(B.x, B.y, D.x, D.y))
            lines.append(QGraphicsLineItem(A.x, A.y, D.x, D.y))

            # Треугольник ACD
            lines.append(QGraphicsLineItem(A.x, A.y, D.x, D.y))
            lines.append(QGraphicsLineItem(D.x, D.y, C.x, C.y))
            lines.append(QGraphicsLineItem(A.x, A.y, C.x, C.y))

    return lines


class terrainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1280, 720)
        self.initUI()
        #DATA
        self.raw_chnk: chunk = generate_chunk(17, 50); diamondSquare(self.raw_chnk, 0)
        self.processed_chnk: chunk = None
        calculateTerrain(self)
    
    def initUI(self):
        '''Widgets'''
        #Scene and viewport
        scene_rect = QRectF(-100, -100, 500, 500)
        scene = QGraphicsScene(scene_rect)
        view = QGraphicsView(scene); view.scale(1, -1); view.setMaximumWidth(900)
        self.SCENE = scene  #For calling from other places in code
        self.VIEW = view    #For calling from other places in code
        #Labels
        label_rotation_x    = QLabel("Rotation X")
        label_rotation_y    = QLabel("Rotation Y")
        label_rotation_z    = QLabel("Rotation Z")
        label_cameraZ       = QLabel("Camera Z")
        label_roughness       = QLabel("Roughness")
        #Sliders
        slider_rotation_x   = QSlider(Qt.Orientation.Horizontal, tickInterval=45); slider_rotation_x.setRange(-180, 180); slider_rotation_x.setValue(-75)
        slider_rotation_y   = QSlider(Qt.Orientation.Horizontal, tickInterval=45); slider_rotation_y.setRange(-180, 180); slider_rotation_y.setValue(20)
        slider_rotation_z   = QSlider(Qt.Orientation.Horizontal, tickInterval=45); slider_rotation_z.setRange(-180, 180); slider_rotation_z.setValue(0)
        slider_cameraZ      = QSlider(Qt.Orientation.Horizontal, tickInterval=100); slider_cameraZ.setRange(100, 10000); slider_cameraZ.setValue(1000)
        slider_roughness    = QSlider(Qt.Orientation.Horizontal, tickInterval=10); slider_roughness.setRange(0, 10000); slider_roughness.setValue(0)
        '''ProcessEvents'''
        slider_rotation_x.valueChanged.connect(lambda: calculateTerrain(self))
        slider_rotation_y.valueChanged.connect(lambda: calculateTerrain(self))
        slider_rotation_z.valueChanged.connect(lambda: calculateTerrain(self))
        slider_cameraZ.valueChanged.connect(lambda: calculateTerrain(self))
        slider_roughness.valueChanged.connect(lambda: changeRawChunk(self))
        self.SLIDERS = [slider_rotation_x, slider_rotation_y, slider_rotation_z, slider_cameraZ, slider_roughness] #For calling from other places in code
        '''Layout'''
        #Layouts
        layout_main     = QHBoxLayout()
        layout_tools    = QGridLayout(); layout_tools.setAlignment(Qt.AlignmentFlag.AlignTop)
        #Nesting
        layout_main.addWidget(view)
        layout_main.addLayout(layout_tools)

        layout_tools.addWidget(label_rotation_x,    0, 0, 1, 3)
        layout_tools.addWidget(slider_rotation_x,   1, 0, 1, 3)
        layout_tools.addWidget(label_rotation_y,    2, 0, 1, 3)
        layout_tools.addWidget(slider_rotation_y,   3, 0, 1, 3)
        layout_tools.addWidget(label_rotation_z,    4, 0, 1, 3)
        layout_tools.addWidget(slider_rotation_z,   5, 0, 1, 3)
        layout_tools.addWidget(label_cameraZ,       6, 0, 1, 3)
        layout_tools.addWidget(slider_cameraZ,      7, 0, 1, 3)
        layout_tools.addWidget(label_roughness,     8, 0, 1, 3)
        layout_tools.addWidget(slider_roughness,    9, 0, 1, 3)
        
        '''General linking'''
        self.setLayout(layout_main)
    
def calculateTerrain(terWidget: terrainWidget):
    #Update vertexes
    sliders: QSlider = terWidget.SLIDERS
    raw_chunk = terWidget.raw_chnk
    processed_chunk_data = raw_chunk.data
    processed_chunk_data = transform3D.useMatrix(processed_chunk_data, transform3D.translateXYZ(-150,0,0))
    processed_chunk_data = transform3D.useMatrix(processed_chunk_data, transform3D.rotationX(sliders[0].value()))
    processed_chunk_data = transform3D.useMatrix(processed_chunk_data, transform3D.rotationY(sliders[1].value()))
    processed_chunk_data = transform3D.useMatrix(processed_chunk_data, transform3D.rotationZ(sliders[2].value()))
    processed_chunk_data = transform3D.useMatrix(processed_chunk_data, transform3D.cameraZ(sliders[3].value()))
    processed_chunk_data = transform3D.useMatrix(processed_chunk_data, transform3D.orthographicProjection())
    processed_chunk = chunk(processed_chunk_data)
    terWidget.processed_chnk = processed_chunk
    #Draw lines
    lines = generate_triangle_lines(processed_chunk)
    scene = terWidget.SCENE
    scene.clear()
    for line in lines:
        scene.addItem(line)
def changeRawChunk(terWidget: terrainWidget):
    sliders: QSlider = terWidget.SLIDERS
    raw_chnk: chunk = generate_chunk(17, 50); diamondSquare(raw_chnk, sliders[4].value()*0.01)
    terWidget.raw_chnk = raw_chnk
    calculateTerrain(terWidget)

if __name__ == "__main__":
    app = QApplication([])
    mainWindow = terrainWidget()
    mainWindow.show()
    app.exec()