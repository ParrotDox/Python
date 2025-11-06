from PySide6.QtWidgets import QDialog, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsLineItem
from PySide6.QtCore import QPointF, QLineF
from CustomClasses import (
    QGraphicsPointGroup,
    QGraphicsLineGroup,
    QGraphicsCustomItemGroup)
class AdditionalMethods():
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
        return group
    @staticmethod
    def getAllChildItemsByCategory(group: QGraphicsItemGroup, class_types: tuple):
        all_items = []

        for item in group.childItems():
            if isinstance(item, class_types):
                all_items.append(item)

            if isinstance(item, QGraphicsItemGroup):
                all_items.extend(AdditionalMethods.getAllChildItemsByCategory(item, class_types))

        return all_items