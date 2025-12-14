import sys
import math
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QSlider, QDoubleSpinBox, 
                               QSpinBox, QGroupBox, QCheckBox, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor


class FractalTreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        
        # Параметры дерева
        self.tree_height = 150
        self.branching_steps = 8
        self.branching_angle = 45
        self.length_ratio = 0.7
        self.thickness_ratio = 0.7
        self.randomness = 10
        self.color_variation = True
        self.background_color = QColor(240, 240, 240)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Заполняем фон
        painter.fillRect(self.rect(), self.background_color)
        
        # Начинаем рисовать дерево из центра нижней части
        start_x = self.width() // 2
        start_y = self.height() - 50
        
        # Устанавливаем начальную толщину и цвет
        initial_thickness = 8
        base_color = QColor(101, 67, 33)  # Коричневый цвет для ствола
        
        self.draw_branch(painter, start_x, start_y, 
                        self.tree_height, -90, 
                        initial_thickness, base_color, 0)
    
    def draw_branch(self, painter, x, y, length, angle, thickness, color, depth):
        if depth > self.branching_steps or length < 2:
            return
            
        # Вычисляем конечную точку ветки
        end_x = x + length * math.cos(math.radians(angle))
        end_y = y + length * math.sin(math.radians(angle))
        
        # Устанавливаем кисть для рисования
        pen = QPen(color)
        pen.setWidth(max(1, int(thickness)))
        painter.setPen(pen)
        
        # Рисуем ветку
        painter.drawLine(int(x), int(y), int(end_x), int(end_y))
        
        if depth < self.branching_steps:
            # Добавляем случайные вариации к углу
            random_factor = (self.randomness / 100.0) * 50
            left_angle_variation = (random.random() - 0.5) * random_factor
            right_angle_variation = (random.random() - 0.5) * random_factor
            
            # Вычисляем новые углы для левой и правой веток
            left_angle = angle - self.branching_angle + left_angle_variation
            right_angle = angle + self.branching_angle + right_angle_variation
            
            # Вычисляем новую длину и толщину
            new_length = length * self.length_ratio
            new_thickness = thickness * self.thickness_ratio
            
            # Создаем новые цвета для веток (если включена вариация цвета)
            if self.color_variation:
                # Для листьев используем зеленые оттенки
                if depth > self.branching_steps - 3:
                    green_variation = max(0, min(255, 100 + depth * 20))
                    new_color = QColor(0, green_variation, 0)
                else:
                    # Для веток - коричневые оттенки
                    brown_variation = max(50, min(150, 100 - depth * 10))
                    new_color = QColor(brown_variation, brown_variation // 2, 0)
            else:
                new_color = color
            
            # Рекурсивно рисуем левую и правую ветки
            self.draw_branch(painter, end_x, end_y, new_length, 
                           left_angle, new_thickness, new_color, depth + 1)
            self.draw_branch(painter, end_x, end_y, new_length, 
                           right_angle, new_thickness, new_color, depth + 1)
            
            # Иногда добавляем третью ветку для более естественного вида
            if depth > 2 and random.random() > 0.7:
                middle_angle = angle + (random.random() - 0.5) * 30
                self.draw_branch(painter, end_x, end_y, new_length * 0.8, 
                               middle_angle, new_thickness * 0.8, new_color, depth + 1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фрактальное Дерево - PySide")
        self.setGeometry(100, 100, 1000, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем layout
        main_layout = QHBoxLayout(central_widget)
        
        # Виджет для отображения дерева
        self.tree_widget = FractalTreeWidget()
        main_layout.addWidget(self.tree_widget, 1)
        
        # Панель управления
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 0)
        
    def create_control_panel(self):
        panel = QGroupBox("Параметры дерева")
        layout = QVBoxLayout(panel)
        
        # Высота дерева
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Высота дерева:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(50, 500)
        self.height_spin.setValue(self.tree_widget.tree_height)
        self.height_spin.valueChanged.connect(self.update_tree_height)
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)
        
        # Шаги ветвления
        steps_layout = QHBoxLayout()
        steps_layout.addWidget(QLabel("Шаги ветвления:"))
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 15)
        self.steps_spin.setValue(self.tree_widget.branching_steps)
        self.steps_spin.valueChanged.connect(self.update_branching_steps)
        steps_layout.addWidget(self.steps_spin)
        layout.addLayout(steps_layout)
        
        # Угол ветвления
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Угол ветвления:"))
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(10, 80)
        self.angle_slider.setValue(self.tree_widget.branching_angle)
        self.angle_slider.valueChanged.connect(self.update_branching_angle)
        angle_layout.addWidget(self.angle_slider)
        
        self.angle_label = QLabel(f"{self.tree_widget.branching_angle}°")
        angle_layout.addWidget(self.angle_label)
        layout.addLayout(angle_layout)
        
        # Коэффициент длины
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Коэффициент длины:"))
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0.1, 0.9)
        self.length_spin.setSingleStep(0.05)
        self.length_spin.setValue(self.tree_widget.length_ratio)
        self.length_spin.valueChanged.connect(self.update_length_ratio)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)
        
        # Коэффициент толщины
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(QLabel("Коэффициент толщины:"))
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0.1, 0.9)
        self.thickness_spin.setSingleStep(0.05)
        self.thickness_spin.setValue(self.tree_widget.thickness_ratio)
        self.thickness_spin.valueChanged.connect(self.update_thickness_ratio)
        thickness_layout.addWidget(self.thickness_spin)
        layout.addLayout(thickness_layout)
        
        # Случайные вариации
        random_layout = QHBoxLayout()
        random_layout.addWidget(QLabel("Случайные вариации:"))
        self.random_slider = QSlider(Qt.Horizontal)
        self.random_slider.setRange(0, 100)
        self.random_slider.setValue(self.tree_widget.randomness)
        self.random_slider.valueChanged.connect(self.update_randomness)
        random_layout.addWidget(self.random_slider)
        
        self.random_label = QLabel(f"{self.tree_widget.randomness}%")
        random_layout.addWidget(self.random_label)
        layout.addLayout(random_layout)
        
        # Вариация цвета
        self.color_check = QCheckBox("Вариация цвета")
        self.color_check.setChecked(self.tree_widget.color_variation)
        self.color_check.stateChanged.connect(self.update_color_variation)
        layout.addWidget(self.color_check)
        
        # Кнопка случайного дерева
        self.random_btn = QPushButton("Случайное дерево")
        self.random_btn.clicked.connect(self.generate_random_tree)
        layout.addWidget(self.random_btn)
        
        layout.addStretch()
        
        return panel
    
    def update_tree_height(self, value):
        self.tree_widget.tree_height = value
        self.tree_widget.update()
    
    def update_branching_steps(self, value):
        self.tree_widget.branching_steps = value
        self.tree_widget.update()
    
    def update_branching_angle(self, value):
        self.tree_widget.branching_angle = value
        self.angle_label.setText(f"{value}°")
        self.tree_widget.update()
    
    def update_length_ratio(self, value):
        self.tree_widget.length_ratio = value
        self.tree_widget.update()
    
    def update_thickness_ratio(self, value):
        self.tree_widget.thickness_ratio = value
        self.tree_widget.update()
    
    def update_randomness(self, value):
        self.tree_widget.randomness = value
        self.random_label.setText(f"{value}%")
        self.tree_widget.update()
    
    def update_color_variation(self, state):
        self.tree_widget.color_variation = (state == Qt.Checked)
        self.tree_widget.update()
    
    def generate_random_tree(self):
        """Генерирует дерево со случайными параметрами"""
        self.tree_widget.tree_height = random.randint(80, 300)
        self.tree_widget.branching_steps = random.randint(5, 12)
        self.tree_widget.branching_angle = random.randint(20, 60)
        self.tree_widget.length_ratio = round(random.uniform(0.5, 0.8), 2)
        self.tree_widget.thickness_ratio = round(random.uniform(0.5, 0.8), 2)
        self.tree_widget.randomness = random.randint(0, 100)
        
        # Обновляем элементы управления
        self.height_spin.setValue(self.tree_widget.tree_height)
        self.steps_spin.setValue(self.tree_widget.branching_steps)
        self.angle_slider.setValue(self.tree_widget.branching_angle)
        self.angle_label.setText(f"{self.tree_widget.branching_angle}°")
        self.length_spin.setValue(self.tree_widget.length_ratio)
        self.thickness_spin.setValue(self.tree_widget.thickness_ratio)
        self.random_slider.setValue(self.tree_widget.randomness)
        self.random_label.setText(f"{self.tree_widget.randomness}%")
        
        self.tree_widget.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())