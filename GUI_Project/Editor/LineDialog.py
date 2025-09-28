import math
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QWidget,
    QTabWidget)

class LineDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create line Dialog pop up")
        self.resize(200,150)

        #Local variables
        self.result = [0,0,0,0,0,0] #K B x1 y1 x2 y2

        self.tab = QTabWidget() #main widget
        self.coefficientWidget = QWidget(); self.tab.addTab(self.coefficientWidget, "Coef") #connect widget to tab
        self.variablesWidget = QWidget(); self.tab.addTab(self.variablesWidget, "Vars") #connect widget to tab
        
        self.mainLayout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.coefficientLayout: QVBoxLayout = QVBoxLayout(); self.coefficientLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.variablesLayout: QVBoxLayout = QVBoxLayout(); self.variablesLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.coefficientWidget.setLayout(self.coefficientLayout)
        self.variablesWidget.setLayout(self.variablesLayout)

        #CoefficientElements
        self.labelK = QLabel("Coefficient K")
        self.labelB = QLabel("Coefficient B")
        self.spinBoxK = QDoubleSpinBox(); self.spinBoxK.setRange(-10000, 10000)
        self.spinBoxB = QDoubleSpinBox(); self.spinBoxB.setRange(-10000, 10000)
        self.btnCoefficientConfirm = QPushButton("Create")

        #VariablesElements
        self.labelX1 = QLabel("X1")
        self.labelY1 = QLabel("Y1")
        self.labelX2 = QLabel("X2")
        self.labelY2 = QLabel("Y2")
        self.spinBoxX1 = QDoubleSpinBox(); self.spinBoxX1.setRange(-10000, 10000)
        self.spinBoxY1 = QDoubleSpinBox(); self.spinBoxY1.setRange(-10000, 10000)
        self.spinBoxX2 = QDoubleSpinBox(); self.spinBoxX2.setRange(-10000, 10000)
        self.spinBoxY2 = QDoubleSpinBox(); self.spinBoxY2.setRange(-10000, 10000)
        self.btnVariablesConfirm = QPushButton("Create")
        
        #Adding widgets to coefficient layout
        self.coefficientLayout.addWidget(self.labelK)
        self.coefficientLayout.addWidget(self.spinBoxK)
        self.coefficientLayout.addWidget(self.labelB)
        self.coefficientLayout.addWidget(self.spinBoxB)
        self.coefficientLayout.addWidget(self.btnCoefficientConfirm)

        #Adding widgets to variables layout
        self.variablesLayout.addWidget(self.labelX1)
        self.variablesLayout.addWidget(self.spinBoxX1)
        self.variablesLayout.addWidget(self.labelY1)
        self.variablesLayout.addWidget(self.spinBoxY1)
        self.variablesLayout.addWidget(self.labelX2)
        self.variablesLayout.addWidget(self.spinBoxX2)
        self.variablesLayout.addWidget(self.labelY2)
        self.variablesLayout.addWidget(self.spinBoxY2)
        self.variablesLayout.addWidget(self.btnVariablesConfirm)
        
        self.mainLayout.addWidget(self.tab)
        self.btnCoefficientConfirm.clicked.connect(self.confirmCoefficientAction)
        self.btnVariablesConfirm.clicked.connect(self.confirmVariablesAction)
        
    def confirmCoefficientAction(self):
        values = self.__getVariablesUsingCoefficient(-10000,10000)
        for i in range(len(values)):
            self.result[i] = values[i]
        self.accept()
    def confirmVariablesAction(self):
        x1 = self.spinBoxX1.value()
        y1 = self.spinBoxY1.value()
        x2 = self.spinBoxX2.value()
        y2 = self.spinBoxY2.value()
        if x1 == x2 and y1 == y2:   #Invalid values
            return
        values = self.__getVariablesUsingVariables(x1,y1,x2,y2)
        for i in range(len(values)):
            self.result[i] = values[i]
        self.accept()

    def closeEvent(self, arg__1):
        self.reject()
        return super().closeEvent(arg__1)
    
    #Returns list of coefficient and coordinates (kbx1x2y1y2) using x1, x2
    def __getVariablesUsingCoefficient(self, x1, x2):
        k = self.spinBoxK.value()
        b = self.spinBoxB.value()
        values = []
        values.append(k)
        values.append(b)
        values.append(x1)
        values.append(k*x1 + b)
        values.append(x2)
        values.append(k*x2 + b)
        return values 
    #Returns list of coefficient and coordinates (kbx1x2y1y2) using x1, y1, x2, y2
    def __getVariablesUsingVariables(self, x1, y1, x2, y2):
        if(x1 == x2):
            k = None
            b = None
        else:
            k = (y2-y1) / (x2 - x1)
            b = y1 - k * x1
        
        dx = x2 - x1
        dy = y2 - y1

        currentLength = math.sqrt(dx**2 + dy**2)
        scaleFactor = 10000 / currentLength
        values = []
        values.append(k)
        values.append(b)
        values.append(x1 - dx * scaleFactor / 2)
        values.append(y1 - dy * scaleFactor / 2)
        values.append(x2 + dx * scaleFactor / 2)
        values.append(y2 + dy * scaleFactor / 2)
        return values