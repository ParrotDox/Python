from FIGURES import Figures
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
    QGraphicsLineItem,
    QGraphicsItemGroup
)
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QTransform

class TranslateDialog(QDialog):

    def __init__(self, figure: Figures, lineItem: QGraphicsItemGroup):
        super().__init__()
        self.initUI(figure)
        self.setWindowTitle("TranslateDialog"); self.setFixedSize(480, 320)
        self.setObjectName("TranslateDialog")

        self.line = lineItem
    
    def initUI(self, figure: Figures):
        mainLayout = QVBoxLayout(); mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        if figure == Figures.LINE:
            #widgets
            translator_X = QSpinBox(minimum=-10000, maximum=10000)
            translator_Y = QSpinBox(minimum=-10000, maximum=10000)
            confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.translateLine(translator_X.value(), translator_Y.value()))
            #layout
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(translator_X)
            mainLayout.addWidget(translator_Y)
            mainLayout.addWidget(confirm_2D)
        elif figure == Figures.CUBE:
            #widgets
            rotatorX = QSpinBox(minimum=-360, maximum=360)
            rotatorY = QSpinBox(minimum=-360, maximum=360)
            rotatorZ = QSpinBox(minimum=-360, maximum=360)
            confirm_3D = QPushButton("Confirm"); #confirm_3D.clicked()#!!!
            #layout
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(rotatorX)
            mainLayout.addWidget(rotatorY)
            mainLayout.addWidget(rotatorZ)
            mainLayout.addWidget(confirm_3D)

        self.setLayout(mainLayout)
        #StyleSheets
        pass
    
    #Slots
    def translateLine(self, translationX, translationY):
        self.line.moveBy(translationX, translationY)
        self.accept()