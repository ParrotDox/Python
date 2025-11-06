from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItemGroup
from Additional import AdditionalMethods
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtCore import Signal, QPointF, QPoint, Qt, QRect
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtGui import QIcon, QPen, QPainter

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
    def __init__(self):
        super().__init__()
        #    X    Y    Z
        self.points = [
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
            [self.points[0], self.points[1]],  
            [self.points[1], self.points[2]],  
            [self.points[2], self.points[3]],  
            [self.points[3], self.points[0]],  

            [self.points[4], self.points[5]],  
            [self.points[5], self.points[6]],  
            [self.points[6], self.points[7]],  
            [self.points[7], self.points[4]],  

            [self.points[0], self.points[4]],  
            [self.points[1], self.points[5]],  
            [self.points[2], self.points[6]],  
            [self.points[3], self.points[7]]   
        ]
        self.lines = []
    
    