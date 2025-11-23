from CustomClasses import QGraphicsLineGroup, QGraphicsCubeGroup, QGraphicsMixedGroup, AdditionalMethods, QGraphicsLineCubeGroup
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

        creator2DLine = QWidget()
        x1_2D = QDoubleSpinBox(minimum=-10000, maximum=10000); x1_2D.setMinimumWidth(50); x1_2D.setMinimumHeight(35)
        x2_2D = QDoubleSpinBox(minimum=-10000, maximum=10000); x2_2D.setMinimumWidth(50); x2_2D.setMinimumHeight(35)
        y1_2D = QDoubleSpinBox(minimum=-10000, maximum=10000); y1_2D.setMinimumWidth(50); y1_2D.setMinimumHeight(35)
        y2_2D = QDoubleSpinBox(minimum=-10000, maximum=10000); y2_2D.setMinimumWidth(50); y2_2D.setMinimumHeight(35)
        label_2Dx1 = QLabel("x1")
        label_2Dx2 = QLabel("x2")
        label_2Dy1 = QLabel("y1")
        label_2Dy2 = QLabel("y2")
        confirm_2DLine = QPushButton("Confirm"); confirm_2DLine.clicked.connect(lambda: self.setPoints(x1_2D.value(), x2_2D.value(), y1_2D.value(), y2_2D.value()))
        confirm_2DLine.setFixedHeight(35)

        creator3DLine = QWidget()
        x1_3D = QDoubleSpinBox(minimum=-10000, maximum=10000); x1_3D.setMinimumWidth(50); x1_3D.setMinimumHeight(35)
        x2_3D = QDoubleSpinBox(minimum=-10000, maximum=10000); x2_3D.setMinimumWidth(50); x2_3D.setMinimumHeight(35)
        y1_3D = QDoubleSpinBox(minimum=-10000, maximum=10000); y1_3D.setMinimumWidth(50); y1_3D.setMinimumHeight(35)
        y2_3D = QDoubleSpinBox(minimum=-10000, maximum=10000); y2_3D.setMinimumWidth(50); y2_3D.setMinimumHeight(35)
        z1_3D = QDoubleSpinBox(minimum=-10000, maximum=10000); z1_3D.setMinimumWidth(50); z1_3D.setMinimumHeight(35)
        z2_3D = QDoubleSpinBox(minimum=-10000, maximum=10000); z2_3D.setMinimumWidth(50); z2_3D.setMinimumHeight(35)
        camZ_3DLine  = QDoubleSpinBox(minimum=0.01, maximum=100, value=1); camZ_3DLine.setMinimumWidth(50); camZ_3DLine.setMinimumHeight(35)
        label_3Dx1 = QLabel("x1")
        label_3Dx2 = QLabel("x2")
        label_3Dy1 = QLabel("y1")
        label_3Dy2 = QLabel("y2")
        label_3Dz1 = QLabel("z1")
        label_3Dz2 = QLabel("z2")
        label_camZ_3DLine = QLabel("Camera z")
        
        confirm_3DLine = QPushButton("Confirm"); confirm_3DLine.clicked.connect(lambda: self.set3DLine(x1_3D.value(), x2_3D.value(), y1_3D.value(), y2_3D.value(), z1_3D.value(), z2_3D.value(), camZ_3DLine.value(), self.scaleFactor))
        confirm_3DLine.setFixedHeight(35)

        creator3DCube = QWidget()
        tX = QDoubleSpinBox(minimum=-10000, maximum=10000, value=0); tX.setMinimumWidth(50); tX.setMinimumHeight(35); 
        tY = QDoubleSpinBox(minimum=-10000, maximum=10000, value=0); tY.setMinimumWidth(50); tY.setMinimumHeight(35)
        tZ = QDoubleSpinBox(minimum=-10000, maximum=10000, value=0); tZ.setMinimumWidth(50); tZ.setMinimumHeight(35)
        sX = QDoubleSpinBox(minimum=-10000, maximum=10000, value=1); sX.setMinimumWidth(50); sX.setMinimumHeight(35)
        sY = QDoubleSpinBox(minimum=-10000, maximum=10000, value=1); sY.setMinimumWidth(50); sY.setMinimumHeight(35)
        sZ = QDoubleSpinBox(minimum=-10000, maximum=10000, value=1); sZ.setMinimumWidth(50); sZ.setMinimumHeight(35)
        rX = QDoubleSpinBox(minimum=-360, maximum=360, value=0); rX.setMinimumWidth(50); rX.setMinimumHeight(35)
        rY = QDoubleSpinBox(minimum=-360, maximum=360, value=0); rY.setMinimumWidth(50); rY.setMinimumHeight(35)
        rZ = QDoubleSpinBox(minimum=-360, maximum=360, value=0); rZ.setMinimumWidth(50); rZ.setMinimumHeight(35)
        camZ_cube  = QDoubleSpinBox(minimum=0.01, maximum=100, value=1); camZ_cube.setMinimumWidth(50); camZ_cube.setMinimumHeight(35)
        label_tX = QLabel("Translate x")
        label_tY = QLabel("Translate y")
        label_tZ = QLabel("Translate z")
        label_sX = QLabel("Scale x")
        label_sY = QLabel("Scale y")
        label_sZ = QLabel("Scale z")
        label_rX = QLabel("Rotate x")
        label_rY = QLabel("Rotate y")
        label_rZ = QLabel("Rotate z")
        label_camZ_cube = QLabel("Camera z")

        confirm_3DCube = QPushButton("Confirm"); confirm_3DCube.clicked.connect(lambda: self.setCube(tX.value(), tY.value(), tZ.value(), sX.value(), sY.value(), sZ.value(), rX.value(), rY.value(), rZ.value(), camZ_cube.value(), self.scaleFactor))
        confirm_3DCube.setFixedHeight(30)

        tab.addTab(creator2DLine, "Line2D")
        tab.addTab(creator3DLine, "Line3D")
        tab.addTab(creator3DCube, "Cube")
        #Layouts
        mainLayout = QVBoxLayout(); mainLayout.setSpacing(10)

        creator2DLineLayout = QGridLayout(); creator2DLineLayout.setAlignment(Qt.AlignmentFlag.AlignTop); creator2DLineLayout.setSpacing(10)
        creator3DLineLayout = QGridLayout(); creator3DLineLayout.setAlignment(Qt.AlignmentFlag.AlignTop); creator3DLineLayout.setSpacing(10)
        creator3DCubeLayout = QGridLayout(); creator3DCubeLayout.setAlignment(Qt.AlignmentFlag.AlignTop); creator3DCubeLayout.setSpacing(10)


        mainLayout.addWidget(tab)

        creator2DLineLayout.addWidget(label_2Dx1, 0, 0); creator2DLineLayout.addWidget(label_2Dy1, 0, 1)
        creator2DLineLayout.addWidget(x1_2D, 1, 0); creator2DLineLayout.addWidget(y1_2D, 1, 1)
        creator2DLineLayout.addWidget(label_2Dx2, 2, 0); creator2DLineLayout.addWidget(label_2Dy2, 2, 1)
        creator2DLineLayout.addWidget(x2_2D, 3, 0); creator2DLineLayout.addWidget(y2_2D, 3, 1)
        creator2DLineLayout.addWidget(confirm_2DLine, 4, 0, 1, 2)

        creator3DLineLayout.addWidget(label_3Dx1, 0, 0); creator3DLineLayout.addWidget(label_3Dy1, 0, 1); creator3DLineLayout.addWidget(label_3Dz1, 0, 2)
        creator3DLineLayout.addWidget(x1_3D, 1, 0); creator3DLineLayout.addWidget(y1_3D, 1, 1); creator3DLineLayout.addWidget(z1_3D, 1, 2)
        creator3DLineLayout.addWidget(label_3Dx2, 2, 0); creator3DLineLayout.addWidget(label_3Dy2, 2, 1); creator3DLineLayout.addWidget(label_3Dz2, 2, 2)
        creator3DLineLayout.addWidget(x2_3D, 3, 0); creator3DLineLayout.addWidget(y2_3D, 3, 1); creator3DLineLayout.addWidget(z2_3D, 3, 2)
        creator3DLineLayout.addWidget(label_camZ_3DLine, 4, 1);
        creator3DLineLayout.addWidget(camZ_3DLine, 5, 1);
        creator3DLineLayout.addWidget(confirm_3DLine, 6, 0, 1, 3)

        creator3DCubeLayout.addWidget(label_tX, 0, 0)
        creator3DCubeLayout.addWidget(tX, 1, 0)
        creator3DCubeLayout.addWidget(label_tY, 2, 0)
        creator3DCubeLayout.addWidget(tY, 3, 0)
        creator3DCubeLayout.addWidget(label_tZ, 4, 0)
        creator3DCubeLayout.addWidget(tZ, 5, 0)
        creator3DCubeLayout.addWidget(label_sX, 0, 1)
        creator3DCubeLayout.addWidget(sX, 1, 1)
        creator3DCubeLayout.addWidget(label_sY, 2, 1)
        creator3DCubeLayout.addWidget(sY, 3, 1)
        creator3DCubeLayout.addWidget(label_sZ, 4, 1)
        creator3DCubeLayout.addWidget(sZ, 5, 1)
        creator3DCubeLayout.addWidget(label_rX, 0, 2)
        creator3DCubeLayout.addWidget(rX, 1, 2)
        creator3DCubeLayout.addWidget(label_rY, 2, 2)
        creator3DCubeLayout.addWidget(rY, 3, 2)
        creator3DCubeLayout.addWidget(label_rZ, 4, 2)
        creator3DCubeLayout.addWidget(rZ, 5, 2)
        creator3DCubeLayout.addWidget(label_camZ_cube, 6, 1)
        creator3DCubeLayout.addWidget(camZ_cube, 7, 1)
        creator3DCubeLayout.addWidget(confirm_3DCube, 8, 0, 1, 3)

        creator2DLine.setLayout(creator2DLineLayout)
        creator3DLine.setLayout(creator3DLineLayout)
        creator3DCube.setLayout(creator3DCubeLayout)
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
        elif option == 1 or option == 2:
            self.figure = Figures.CUBE
        return
    def setPoints(self, x1, x2, y1, y2):
        if x1 == x2 and y1 == y2:
            print("Points can't have equal coordinates.")
            return
        self.points = [QPointF(float(x1), float(y1)), QPointF(float(x2), float(y2))]
        self.accept()
    def setCube(self, tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ_cube, scaleFactor):

        cube = AdditionalMethods.createCustomCube(tX, tY, tZ, sX, sY, sZ, rX, rY, rZ, camZ_cube, scaleFactor)
        camZ_points = QGraphicsCubeGroup.useMatrix(cube.cubeRawPoints, QGraphicsCubeGroup.cameraZ(camZ_cube))
        projected_points = QGraphicsCubeGroup.useMatrix(camZ_points, QGraphicsCubeGroup.orthographicProjection())
        self.points = projected_points
        self.cube = cube
        self.accept()
    def set3DLine(self, x1, x2, y1, y2, z1, z2, camZ_cube, scaleFactor):

        cubeLine = AdditionalMethods.createCustomCubeLine(0,0,0,1,1,1,0,0,0,camZ_cube,scaleFactor, None, [x1,y1,z1], [x2,y2,z2])
        camZ_points = QGraphicsCubeGroup.useMatrix(cubeLine.cubeRawPoints, QGraphicsCubeGroup.cameraZ(camZ_cube))
        projected_points = QGraphicsCubeGroup.useMatrix(camZ_points, QGraphicsCubeGroup.orthographicProjection())
        self.points = projected_points
        self.cube = cubeLine
        self.accept()
