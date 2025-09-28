from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsLineItem
class LineInfo():
    defaultPen: QPen = None

    def __init__(self, k, b, lineGE: QGraphicsLineItem):
        self.k = k
        self.b = b
        self.lineGE = lineGE

    def setDefaultPen(self):
        self.lineGE.setPen(self.defaultPen)
    