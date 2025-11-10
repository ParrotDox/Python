from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItemGroup
from EditorEnum import Figures
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtCore import Signal, QPointF, QPoint, Qt, QRect, QLineF
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtGui import QIcon, QPen, QPainter
import math

class QGraphicsCustomView(QGraphicsView):
    
    itemFocused: Signal = Signal(QGraphicsScene, list, QPointF)
    itemFocusedToGroup: Signal = Signal(QGraphicsScene, list, QPointF)
    itemMoved: Signal = Signal(QPointF, QPointF)
    scaleFactorChanged: Signal = Signal(float)

    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        #for dragging viewport
        self.lastLeftMousePos: QPointF = None
        self.lastMiddleMousePos: QPointF = None
        
    def mousePressEvent(self, event: QMouseEvent):
        pressPointF = event.position()
        pressPointInt = QPoint(int(pressPointF.x()), int(pressPointF.y()))
        
        if event.buttons() == Qt.MouseButton.MiddleButton:

            self.lastMiddleMousePos = pressPointF
        
        elif event.buttons() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            print("shiftModifier")
            items = self.items(pressPointInt)
            filteredGroups = []
            
            #filter only groups
            for it in items:
                if isinstance(it, QGraphicsItemGroup):
                    filteredGroups.append(it)
            
            self.itemFocusedToGroup.emit(self.scene(), filteredGroups, pressPointF)
            self.lastLeftMousePos = pressPointF

        elif event.buttons() == Qt.MouseButton.LeftButton:
            items = self.items(pressPointInt)
            filteredGroups = []

            #filter only groups
            for it in items:
                if isinstance(it, QGraphicsItemGroup):
                    filteredGroups.append(it)

            self.itemFocused.emit(self.scene(), filteredGroups, pressPointF)
            self.lastLeftMousePos = pressPointF

        return super().mousePressEvent(event)
    def mouseMoveEvent(self, event: QMouseEvent):
        pressPointF = event.position()
        #Move view
        if event.buttons() == Qt.MouseButton.MiddleButton:
            
            delta = event.position() - self.lastMiddleMousePos
            self.lastMiddleMousePos = pressPointF

            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
        #Move item
        elif event.buttons() == Qt.MouseButton.LeftButton:

            delta = event.position() - self.lastLeftMousePos
            self.lastLeftMousePos = pressPointF

            self.itemMoved.emit(self.lastLeftMousePos, delta)

        return super().mouseMoveEvent(event)
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.scaleFactorChanged.emit(event.angleDelta().y())
        else:
            return super().wheelEvent(event)
class QGraphicsCustomScene(QGraphicsScene):
    def __init__(self, boundingRect: QRect, scaleFactor: float, defaultPen: QPen, crossPen: QPen):
        super().__init__(boundingRect)

        self.defaultPen = defaultPen
        self.crossPen = crossPen

        self.scaleFactor = scaleFactor
    
    def drawBackground(self, painter: QPainter, rect: QRect):
        super().drawBackground(painter, rect)

        '''Draw grid'''
        painter.setPen(self.defaultPen)

        #from 0 to left
        x = 0
        while (x >= rect.left()):
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x -= self.scaleFactor

        #from 0 to right 
        x = 0
        while (x <= rect.right()):
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += self.scaleFactor

        #from zero to up (up = bottom due to GUI system coordinate)
        y = 0
        while (y <= rect.bottom()):
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += self.scaleFactor

        #from zero to bottom (bottom = up due to GUI system coordinate) 
        y = 0
        while (y >= rect.top()):
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y -= self.scaleFactor

        '''Draw cross'''
        painter.setPen(self.crossPen)
        painter.drawLine(QPointF(rect.left(), 0), QPointF(rect.right(), 0))
        painter.drawLine(QPointF(0, rect.top()), QPointF(0, rect.bottom()))

class QOneWayToggleButton(QPushButton):
    def __init__(self, icon: QIcon, text: str):
        super().__init__(icon, text)
    
    def mousePressEvent(self, e: QMouseEvent):
        if not self.isChecked():
            return super().mousePressEvent(e)


class QGraphicsCustomItemGroup(QGraphicsItemGroup):
    def __init__(self):
        super().__init__()
        self.pen = None
        self.brush = None
        self.scaleFactor = 1
        self.points: list[QPointF] = []
        self.baseChildItems = []    #Base child items (QGEllipse, QGLine etc.)
        self.equation: str = ""
'''Every class indicates to program that it works with a [line, point, cube, mixed item]'''
class QGraphicsLineGroup(QGraphicsCustomItemGroup):
    def __init__(self):
        super().__init__()
class QGraphicsPointGroup(QGraphicsCustomItemGroup):
    def __init__(self):
        super().__init__()
class QGraphicsMixedGroup(QGraphicsCustomItemGroup):
    def __init__(self):
        super().__init__()
        self.equation = "MIXED GROUP"
        
    def addToGroup(self, item):
        if isinstance(item, (QGraphicsMixedGroup, QGraphicsCubeGroup, QGraphicsLineGroup, QGraphicsPointGroup)):
            '''add items from metadata'''
            for pt in item.points:
                if pt in self.points:
                    continue
                else:
                    self.points.append(pt)
            for chld in item.childItems():
                if chld in self.baseChildItems:
                    continue
                else:
                    self.baseChildItems.append(chld)

        return super().addToGroup(item)
    def removeFromGroup(self, item):
        if isinstance(item, (QGraphicsMixedGroup, QGraphicsCubeGroup, QGraphicsLineGroup, QGraphicsPointGroup)):
            '''remove invalid items from metadata'''
            for pt in item.points:
                if pt in self.points:
                    self.points.remove(pt)
            for chld in item.childItems():
                if pt in self.baseChildItems:
                    self.baseChildItems.remove(chld)


        return super().removeFromGroup(item)
class QGraphicsCubeGroup(QGraphicsMixedGroup):
    def __init__(self, scaleFactor, tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ):
        super().__init__()

        self.equation = f"CUBE: (tX = {tX}, tY = {tY})"
        self.scaleFactor = scaleFactor
        self.tX = tX
        self.tY = tY
        self.tZ = tZ
        self.sX = sX
        self.sY = sY
        self.sZ = sZ
        self.rX = rX
        self.rY = rY
        self.rZ = rZ
        self.camZ = camZ

        #    X    Y    Z
        self.cubePoints = [
            [-1, -1, -1], 
            [ 1, -1, -1],   
            [ 1,  1, -1],  
            [-1,  1, -1],  
            [-1, -1,  1],  
            [ 1, -1,  1],  
            [ 1,  1,  1],  
            [-1,  1,  1]   
        ]
        self.pairs = [
            [self.cubePoints[0], self.cubePoints[1]],  
            [self.cubePoints[1], self.cubePoints[2]],  
            [self.cubePoints[2], self.cubePoints[3]],  
            [self.cubePoints[3], self.cubePoints[0]],  

            [self.cubePoints[4], self.cubePoints[5]],  
            [self.cubePoints[5], self.cubePoints[6]],  
            [self.cubePoints[6], self.cubePoints[7]],  
            [self.cubePoints[7], self.cubePoints[4]],  

            [self.cubePoints[0], self.cubePoints[4]],  
            [self.cubePoints[1], self.cubePoints[5]],  
            [self.cubePoints[2], self.cubePoints[6]],  
            [self.cubePoints[3], self.cubePoints[7]]   
        ]
        self.lines = self.createLines(self.cubePoints, scaleFactor)
        self.updateCube(self.cubePoints, self.lines)

    @staticmethod
    def useMatrix(points: list[list[float]], matrix: list[list[float]]):
        new_points = []
        for pt in points:
            x, y, z = pt
            x_new = matrix[0][0]*x + matrix[0][1]*y + matrix[0][2]*z + matrix[0][3]*1
            y_new = matrix[1][0]*x + matrix[1][1]*y + matrix[1][2]*z + matrix[1][3]*1
            z_new = matrix[2][0]*x + matrix[2][1]*y + matrix[2][2]*z + matrix[2][3]*1
            w_new = matrix[3][0]*x + matrix[3][1]*y + matrix[3][2]*z + matrix[3][3]*1
        
            if w_new != 0:
                new_points.append([x_new/w_new, y_new/w_new, z_new/w_new])
            else:
                new_points.append([x_new, y_new, z_new])
        return new_points
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
    @staticmethod
    def createLines(points, scaleFactor):
        pairs = [
            [points[0], points[1]],  
            [points[1], points[2]],  
            [points[2], points[3]],  
            [points[3], points[0]],  

            [points[4], points[5]],  
            [points[5], points[6]],  
            [points[6], points[7]],  
            [points[7], points[4]],  

            [points[0], points[4]],  
            [points[1], points[5]],  
            [points[2], points[6]],  
            [points[3], points[7]]   
        ]

        lines = []

        for pair in pairs:
            
            lineItem = AdditionalMethods.createCustomLine([QPointF(pair[0][0], pair[0][1]), QPointF(pair[1][0], pair[1][1])], scaleFactor)
            lines.append(lineItem)
        
        return lines
    def updateCube(self, points, lines: list[QGraphicsLineItem]):
        
        '''Update metadata points'''
        self.points = []
        for pt in points:
            self.points.append(QPointF(pt[0], pt[1]))

        '''Update children'''
        for chld in self.childItems():
            self.removeFromGroup(chld)
        for line in lines:
            self.addToGroup(line)
        
        '''Update cube points'''
        self.cubePoints = points

        '''Update pairs'''
        self.pairs = [
            [points[0], points[1]],  
            [points[1], points[2]],  
            [points[2], points[3]],  
            [points[3], points[0]],  

            [points[4], points[5]],  
            [points[5], points[6]],  
            [points[6], points[7]],  
            [points[7], points[4]],  

            [points[0], points[4]],  
            [points[1], points[5]],  
            [points[2], points[6]],  
            [points[3], points[7]]   
        ]

        '''Update lines'''
        self.lines = lines
        
        
class AdditionalMethods():
    @staticmethod
    def whatFigure(item: QGraphicsItem):
        if item == None:
            return None
        elif isinstance(item, QGraphicsPointGroup):
            return Figures.POINT
        elif isinstance(item, QGraphicsLineGroup):
            return Figures.LINE
        elif isinstance(item, QGraphicsCubeGroup):
            return Figures.CUBE
        elif isinstance(item, QGraphicsMixedGroup):
            return Figures.MIXED
    def getPoints(self, item: QGraphicsItemGroup):
        pts = []
        items = item.childItems()
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                ellipse = it
                point = ellipse.rect().center()
                pts.append(point)
        return pts
    def getLineItemFromGroup(self, group: QGraphicsItemGroup):
        items = group.childItems()
        lineItem = None
        for it in items:
           if isinstance(it, QGraphicsLineItem):
               lineItem = it
               break
        return lineItem
    @staticmethod
    def createCustomLine(points: list[QPointF], scaleFactor):
        #All points for drawing scaled by scaleFactor!
        '''Line points to draw a line'''
        linePStart = QPointF(points[0].x()*scaleFactor, points[0].y()*scaleFactor) #Start point for line
        linePEnd = QPointF(points[1].x()*scaleFactor, points[1].y()*scaleFactor) #End point for line
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
        group.scaleFactor = scaleFactor
        group.points = points
        group.baseChildItems = ellipseStart, ellipseEnd, lineItem
        group.equation = f"LINE: x - {round(points[0].x(), 2)} / {round(points[1].x() - points[0].x(), 2)} = y - {round(points[0].y(), 2)} / {round(points[1].y() - points[0].y(), 2)}"
        return group
    @staticmethod
    def createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleFactor):
        
        '''Create points'''
        cube = QGraphicsCubeGroup(scaleFactor, tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ)
        lines = None
        projected_points = None
        '''
            scaledPoints = QGraphicsCubeGroup.useMatrix(cube.cubePoints, QGraphicsCubeGroup.scaleXYZ(sX, sY, sZ))
            rX_points = QGraphicsCubeGroup.useMatrix(scaledPoints, QGraphicsCubeGroup.rotationX(rX))
            rY_points = QGraphicsCubeGroup.useMatrix(rX_points, QGraphicsCubeGroup.rotationY(rY))
            rZ_points = QGraphicsCubeGroup.useMatrix(rY_points, QGraphicsCubeGroup.rotationZ(rZ))
            translatedPoints = QGraphicsCubeGroup.useMatrix(rZ_points, QGraphicsCubeGroup.translateXYZ(tX, tY, tZ))
            camZ_points = QGraphicsCubeGroup.useMatrix(translatedPoints, QGraphicsCubeGroup.cameraZ(camZ))
            projected_points = QGraphicsCubeGroup.useMatrix(camZ_points, QGraphicsCubeGroup.orthographicProjection())
            lines = QGraphicsCubeGroup.createLines(projected_points, scaleFactor)
        '''
        rX_points = QGraphicsCubeGroup.useMatrix(cube.cubePoints, QGraphicsCubeGroup.rotationX(rX))
        rY_points = QGraphicsCubeGroup.useMatrix(rX_points, QGraphicsCubeGroup.rotationY(rY))
        rZ_points = QGraphicsCubeGroup.useMatrix(rY_points, QGraphicsCubeGroup.rotationZ(rZ))
        translatedPoints = QGraphicsCubeGroup.useMatrix(rZ_points, QGraphicsCubeGroup.translateXYZ(tX, tY, tZ))
        scaledPoints = QGraphicsCubeGroup.useMatrix(translatedPoints, QGraphicsCubeGroup.scaleXYZ(sX, sY, sZ))
        camZ_points = QGraphicsCubeGroup.useMatrix(scaledPoints, QGraphicsCubeGroup.cameraZ(camZ))
        projected_points = QGraphicsCubeGroup.useMatrix(camZ_points, QGraphicsCubeGroup.orthographicProjection())
        lines = QGraphicsCubeGroup.createLines(projected_points, scaleFactor)

        '''Update metadata'''
        cube.scaleFactor = scaleFactor
        cube.baseChildItems = lines
        cube.equation = f"CUBE: (tX = {round(tX, 2)}, tY = {round(tY, 2)})"

        '''Update group'''
        cube.updateCube(projected_points, lines)
        return cube
    @staticmethod
    def getAllChildItemsByCategory(group: QGraphicsItemGroup, class_types: tuple):
        all_items = []

        for item in group.childItems():
            if isinstance(item, class_types):
                all_items.append(item)

            if isinstance(item, QGraphicsItemGroup):
                all_items.extend(AdditionalMethods.getAllChildItemsByCategory(item, class_types))

        return all_items