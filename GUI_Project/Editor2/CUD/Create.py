from CustomClasses import QGraphicsLineGroup, QGraphicsCubeGroup, QGraphicsMixedGroup, AdditionalMethods
from EditorEnum import Figures
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QTabWidget,
    QGridLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPointF

class CreateDialog(QDialog):
    
    def __init__(self, scaleFactor):
        super().__init__()
        self.initUI()
        self.setWindowTitle("CreateDialog")
        self.setObjectName("CreateDialog")
        self.setMinimumWidth(200)

        self.scaleFactor = scaleFactor
        self.figure: int = Figures.LINE
        self.points: list[QPointF] = []
        self.cube: QGraphicsCubeGroup = None

    def initUI(self):
        #Widgets
        tab = QTabWidget(); tab.currentChanged.connect(lambda: self.setDimension(tab))

        creator2D = QWidget()
        x1 = QDoubleSpinBox(minimum=-10000, maximum=10000); x1.setMinimumWidth(50); x1.setMinimumHeight(35)
        x2 = QDoubleSpinBox(minimum=-10000, maximum=10000); x2.setMinimumWidth(50); x2.setMinimumHeight(35)
        y1 = QDoubleSpinBox(minimum=-10000, maximum=10000); y1.setMinimumWidth(50); y1.setMinimumHeight(35)
        y2 = QDoubleSpinBox(minimum=-10000, maximum=10000); y2.setMinimumWidth(50); y2.setMinimumHeight(35)
        label_x1 = QLabel("x1")
        label_x2 = QLabel("x2")
        label_y1 = QLabel("y1")
        label_y2 = QLabel("y2")
        confirm_2D = QPushButton("Confirm"); confirm_2D.clicked.connect(lambda: self.setPoints(x1.value(), x2.value(), y1.value(), y2.value()))
        confirm_2D.setFixedHeight(35)

        creator3D = QWidget()
        tX = QDoubleSpinBox(minimum=-10000, maximum=10000, value=0); tX.setMinimumWidth(50); tX.setMinimumHeight(35); 
        tY = QDoubleSpinBox(minimum=-10000, maximum=10000, value=0); tY.setMinimumWidth(50); tY.setMinimumHeight(35)
        tZ = QDoubleSpinBox(minimum=-10000, maximum=10000, value=0); tZ.setMinimumWidth(50); tZ.setMinimumHeight(35)
        sX = QDoubleSpinBox(minimum=-10000, maximum=10000, value=1); sX.setMinimumWidth(50); sX.setMinimumHeight(35)
        sY = QDoubleSpinBox(minimum=-10000, maximum=10000, value=1); sY.setMinimumWidth(50); sY.setMinimumHeight(35)
        sZ = QDoubleSpinBox(minimum=-10000, maximum=10000, value=1); sZ.setMinimumWidth(50); sZ.setMinimumHeight(35)
        rX = QDoubleSpinBox(minimum=-360, maximum=360, value=0); rX.setMinimumWidth(50); rX.setMinimumHeight(35)
        rY = QDoubleSpinBox(minimum=-360, maximum=360, value=0); rY.setMinimumWidth(50); rY.setMinimumHeight(35)
        rZ = QDoubleSpinBox(minimum=-360, maximum=360, value=0); rZ.setMinimumWidth(50); rZ.setMinimumHeight(35)
        camZ  = QDoubleSpinBox(minimum=0.01, maximum=100, value=1); camZ.setMinimumWidth(50); camZ.setMinimumHeight(35)
        label_tX = QLabel("Translate x")
        label_tY = QLabel("Translate y")
        label_tZ = QLabel("Translate z")
        label_sX = QLabel("Scale x")
        label_sY = QLabel("Scale y")
        label_sZ = QLabel("Scale z")
        label_rX = QLabel("Rotate x")
        label_rY = QLabel("Rotate y")
        label_rZ = QLabel("Rotate z")
        label_camZ = QLabel("Camera z")

        confirm_3D = QPushButton("Confirm"); confirm_3D.clicked.connect(lambda: self.setCube(tX.value(), tY.value(), tZ.value(), sX.value(), sY.value(), sZ.value(), rX.value(), rY.value(), rZ.value(), camZ.value(), self.scaleFactor))
        confirm_3D.setFixedHeight(30)

        tab.addTab(creator2D, "Line")
        tab.addTab(creator3D, "Cube")
        #Layouts
        mainLayout = QVBoxLayout(); mainLayout.setSpacing(10)

        creator2DLayout = QGridLayout(); creator2DLayout.setAlignment(Qt.AlignmentFlag.AlignTop); creator2DLayout.setSpacing(10)
        creator3DLayout = QGridLayout(); creator3DLayout.setAlignment(Qt.AlignmentFlag.AlignTop); creator3DLayout.setSpacing(10)


        mainLayout.addWidget(tab)

        creator2DLayout.addWidget(label_x1, 0, 0); creator2DLayout.addWidget(label_y1, 0, 1)
        creator2DLayout.addWidget(x1, 1, 0); creator2DLayout.addWidget(y1, 1, 1)
        creator2DLayout.addWidget(label_x2, 2, 0); creator2DLayout.addWidget(label_y2, 2, 1)
        creator2DLayout.addWidget(x2, 3, 0); creator2DLayout.addWidget(y2, 3, 1)
        creator2DLayout.addWidget(confirm_2D, 4, 0, 1, 2)

        creator3DLayout.addWidget(label_tX, 0, 0)
        creator3DLayout.addWidget(tX, 1, 0)
        creator3DLayout.addWidget(label_tY, 2, 0)
        creator3DLayout.addWidget(tY, 3, 0)
        creator3DLayout.addWidget(label_tZ, 4, 0)
        creator3DLayout.addWidget(tZ, 5, 0)
        creator3DLayout.addWidget(label_sX, 0, 1)
        creator3DLayout.addWidget(sX, 1, 1)
        creator3DLayout.addWidget(label_sY, 2, 1)
        creator3DLayout.addWidget(sY, 3, 1)
        creator3DLayout.addWidget(label_sZ, 4, 1)
        creator3DLayout.addWidget(sZ, 5, 1)
        creator3DLayout.addWidget(label_rX, 0, 2)
        creator3DLayout.addWidget(rX, 1, 2)
        creator3DLayout.addWidget(label_rY, 2, 2)
        creator3DLayout.addWidget(rY, 3, 2)
        creator3DLayout.addWidget(label_rZ, 4, 2)
        creator3DLayout.addWidget(rZ, 5, 2)
        creator3DLayout.addWidget(label_camZ, 6, 1)
        creator3DLayout.addWidget(camZ, 7, 1)
        creator3DLayout.addWidget(confirm_3D, 8, 0, 1, 3)

        creator2D.setLayout(creator2DLayout)
        creator3D.setLayout(creator3DLayout)
        self.setLayout(mainLayout)
        
        #StyleSheets
        dialog_stylesheet = (
            'QDialog {'
            'background-color: #FFFFFF;'
            '}'
        )
        label_stylesheet = (
            'QLabel {'
            'color: #132238;'
            'font-family: "Work Sans";'
            'font-size: 18px;' 
            '}'
        )
        button_stylesheet = (
            'QPushButton {'
            'background-color: #EEEEEE;'
            'color: #132238;'
            'border-radius: 12px;'
            'font-family: "Work Sans";'
            'font-size: 12px;' 
            'font-weight: bold;'
            '}'
            
            'QPushButton:hover {'
            'background-color: #A53DFF;'
            'color: #FFFFFF;'
            'font-size: 16px;}'
            'QPushButton:pressed {'
            'background-color: #632599;'
            'color: #FFFFFF;'
            'font-size: 16px;}'

            'QPushButton:checked {'
            'background-color: #DBB1FF;'
            'color: #FFFFFF;'
            'font-size: 16px;}'
        )
        spinBox_stylesheet = (
            'QDoubleSpinBox {'
                'font-size: 16px;'
                'color: #632599;'
                'background-color: #DBB1FF;'
                'border: 0x solid #DBB1FF;'
                'border-radius: 2px;' \
                'padding-left: 5px;'
            '}'
            )
        styleSheet =  dialog_stylesheet + label_stylesheet + button_stylesheet + spinBox_stylesheet
        self.setStyleSheet(styleSheet)
        pass
    
    #Slots
    def setDimension(self, tab: QTabWidget):
        option = tab.currentIndex()
        if option == 0:
            self.figure = Figures.LINE
        elif option == 1:
            self.figure = Figures.CUBE
        return
    def setPoints(self, x1, x2, y1, y2):
        if x1 == x2 and y1 == y2:
            print("Points can't have equal coordinates.")
            return
        self.points = [QPointF(float(x1), float(y1)), QPointF(float(x2), float(y2))]
        self.accept()
    def setCube(self, tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleFactor):

        cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ, scaleFactor)
        self.points = cube.cubePoints
        self.cube = cube
        self.accept()
