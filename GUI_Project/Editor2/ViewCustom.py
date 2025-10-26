from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsItemGroup
from PySide6.QtCore import Signal, QPointF, QPoint
from PySide6.QtGui import QMouseEvent

class QGraphicsViewCustom(QGraphicsView):
    itemFocused: Signal = Signal(QGraphicsScene, QGraphicsItem)
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        
    def mousePressEvent(self, event: QMouseEvent):
        focusPointF = event.position()
        focusPointInt = QPoint(int(focusPointF.x()), int(focusPointF.y()))
        items = self.items(focusPointInt)
        item = None

        #filter only groups
        for i in items:
            if isinstance(i, QGraphicsItemGroup):
                item = i
                break

        self.itemFocused.emit(self.scene(), item)
        return super().mousePressEvent(event)