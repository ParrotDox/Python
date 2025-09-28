from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGraphicsItem)

class QGraphicsCustomScene(QGraphicsScene):

    clickedOnItem = Signal(QGraphicsItem)

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        view: QGraphicsView = self.views()[0]
        item = self.itemAt(event.scenePos(), view.transform())
        if item != None:
            self.clickedOnItem.emit(item)
        return super().mousePressEvent(event)