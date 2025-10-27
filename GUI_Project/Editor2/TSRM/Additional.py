from PySide6.QtWidgets import QDialog, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsLineItem
from PySide6.QtCore import QPointF, QLineF

class AdditionalDialogMethods():
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
    def createCustomLine(self, points: list[QPointF]):
        pointStart = QGraphicsEllipseItem(points[0].x()-5, points[0].y()-5, 10, 10)
        pointEnd = QGraphicsEllipseItem(points[1].x()-5, points[1].y()-5, 10, 10)
        line = QGraphicsLineItem(QLineF(points[0], points[1]))
        group = QGraphicsItemGroup(); group.addToGroup(pointStart); group.addToGroup(pointEnd); group.addToGroup(line)
        return group