from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PySide6.QtCore import Signal, QPointF, QPoint
from PySide6.QtGui import QMouseEvent
class QGraphicsViewCustom(QGraphicsView):
    itemFocused: Signal = Signal(QGraphicsScene, QGraphicsItem)
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)

    def mousePressEvent(self, event: QMouseEvent):
        focusPointF = event.position()
        focusPointInt = QPoint(int(focusPointF.x()), int(focusPointF.y()))
        item = self.itemAt(focusPointInt)
        if item != None and item != 0:
            self.itemFocused.emit(self.scene(), item)
        return super().mousePressEvent(event)