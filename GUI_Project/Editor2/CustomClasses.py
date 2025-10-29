from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItemGroup
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtCore import Signal, QPointF, QPoint, Qt
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtGui import QIcon

class QGraphicsViewCustom(QGraphicsView):
    itemFocused: Signal = Signal(QGraphicsScene, list, QPointF)
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        
        #for dragging viewport
        self.lastMousePos = None
        
    def mousePressEvent(self, event: QMouseEvent):
        pressPointF = event.position()
        if event.buttons() == Qt.MouseButton.LeftButton:
            focusPointInt = QPoint(int(pressPointF.x()), int(pressPointF.y()))
            items = self.items(focusPointInt)
            filteredGroups = []

            #filter only groups
            for it in items:
                if isinstance(it, QGraphicsItemGroup):
                    filteredGroups.append(it)

            self.itemFocused.emit(self.scene(), filteredGroups, pressPointF)
        elif event.buttons() == Qt.MouseButton.MiddleButton:
            self.lastMousePos = pressPointF
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.MiddleButton:
            
            delta = event.position() - self.lastMousePos
            self.lastMousePos = event.position()

            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

        return super().mouseMoveEvent(event)
class QGraphicsSceneCustom(QGraphicsScene):
    def __init__(self):
        super().__init__()

class QOneWayToggleButton(QPushButton):
    def __init__(self, icon: QIcon, text: str):
        super().__init__(icon, text)
    
    def mousePressEvent(self, e: QMouseEvent):
        if not self.isChecked():
            return super().mousePressEvent(e)

class QGraphicsFigureAdditional():
    def __init__(self):
        self.pen = None
        self.brush = None
class QGraphicsCustomGroupItem(QGraphicsItemGroup, QGraphicsFigureAdditional):
    def __init__(self):
        QGraphicsItemGroup.__init__(self)
        QGraphicsFigureAdditional.__init__(self)
class QGraphicsCubeGroup(QGraphicsCustomGroupItem):
    def __init__(self):
        super().__init__()
class QGraphicsLineGroup(QGraphicsCustomGroupItem):
    def __init__(self):
        super().__init__()
class QGraphicsPointGroup(QGraphicsCustomGroupItem):
    def __init__(self):
        super().__init__()
class QGraphicsMixedGroup(QGraphicsCustomGroupItem):
    def __init__(self):
        super().__init__()
        