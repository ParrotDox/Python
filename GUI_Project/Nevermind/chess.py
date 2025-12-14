import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QSlider, QDoubleSpinBox, 
                               QPushButton, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt
import pyqtgraph.opengl as gl

# --- Математическое ядро ---

def heaviside(x):
    """Функция Хэвисайда: возвращает 1, если x >= 0, иначе 0."""
    return 1.0 if x >= 0 else 0.0

class PawnLogic:
    """Класс для проверки попадания точки внутрь пешки."""
    
    def __init__(self):
        # Параметры по умолчанию
        self.sphere_r = 0.8
        self.ellip_rx = 0.8
        self.ellip_ry = 0.4  # Высота эллипсоида
        self.ellip_rz = 0.8
        self.parab_a = 1.0
        self.parab_b = 1.0
        self.parab_h = 2.0
        self.cyl_r = 1.8
        self.cyl_h = 0.6

    def is_point_in_pawn(self, x, y, z):
        """
        Проверка вхождения точки. Z - высота.
        """
        
        # 1. Цилиндр (основание)
        cyl_base = 0
        cyl_top = self.cyl_h
        in_cylinder = (heaviside(self.cyl_r**2 - (x**2 + y**2)) * heaviside(z - cyl_base) * heaviside(cyl_top - z))

        # 2. Параболоид
        parab_base = cyl_top
        local_z = z - parab_base
        val_parabolic = (x**2)/(self.parab_a**2) + (y**2)/(self.parab_b**2)
        max_h_at_xy = self.parab_h - val_parabolic
        in_paraboloid = (heaviside(max_h_at_xy - local_z) * heaviside(local_z) * heaviside(self.parab_h - local_z))

        # 3. Эллипсоид
        ellip_base = parab_base + self.parab_h
        ellip_center_z = ellip_base + self.ellip_ry
        local_z_ellip = z - ellip_center_z
        ellip_val = (x/self.ellip_rx)**2 + (y/self.ellip_rz)**2 + (local_z_ellip/self.ellip_ry)**2
        in_ellipsoid = (heaviside(1 - ellip_val) * heaviside(z - ellip_base) * heaviside(ellip_base + self.ellip_ry * 2 - z))

        # 4. Шар
        sphere_base = ellip_base + self.ellip_ry * 2
        sphere_center_z = sphere_base + self.sphere_r
        local_z_sphere = z - sphere_center_z
        dist_sq = x**2 + y**2 + local_z_sphere**2
        in_sphere = (heaviside(self.sphere_r**2 - dist_sq) * heaviside(z - sphere_base))

        return (in_cylinder + in_paraboloid + in_ellipsoid + in_sphere) > 0

# --- Генерация 3D Мешей ---

def create_cylinder_mesh(r, h, offset_z):
    # Увеличиваем детализацию (cols=80)
    md = gl.MeshData.cylinder(rows=1, cols=80, radius=[r, r], length=h)
    verts = md.vertexes()
    verts[:, 2] += offset_z
    md.setVertexes(verts)
    return md

def create_paraboloid_mesh(a, b, h, offset_z):
    cols = 80 # Увеличили детализацию
    rows = 40 # Увеличили детализацию
    verts = []
    faces = []
    
    # Генерация вершин
    for i in range(rows + 1):
        v = i / rows # от 0 до 1
        z_curr = v * h 
        r_factor = np.sqrt(max(0, h - z_curr))
        
        for j in range(cols):
            theta = 2 * np.pi * j / cols
            x = a * r_factor * np.cos(theta)
            y = b * r_factor * np.sin(theta)
            verts.append([x, y, z_curr + offset_z])
            
    # Генерация граней 
    for i in range(rows):
        for j in range(cols):
            p1 = i * cols + j
            p2 = p1 + 1 if (j < cols - 1) else i * cols
            p3 = (i + 1) * cols + j
            p4 = p3 + 1 if (j < cols - 1) else (i + 1) * cols
            
            # Одна сторона для полупрозрачности
            faces.append([p1, p2, p3])
            faces.append([p3, p2, p4])
    
    md = gl.MeshData(vertexes=np.array(verts), faces=np.array(faces))
    # Удалили md.computeNormals(), чтобы избежать ошибки
    return md

def create_ellipsoid_mesh(rx, ry, rz, offset_z):
    md = gl.MeshData.sphere(rows=40, cols=80, radius=1.0) # Увеличили детализацию
    verts = md.vertexes()
    verts[:, 0] *= rx
    verts[:, 1] *= rz 
    verts[:, 2] *= ry
    verts[:, 2] += offset_z + ry 
    md.setVertexes(verts)
    return md

def create_sphere_mesh(r, offset_z):
    md = gl.MeshData.sphere(rows=40, cols=80, radius=r) # Увеличили детализацию
    verts = md.vertexes()
    verts[:, 2] += offset_z + r
    md.setVertexes(verts)
    return md


# --- Основное окно ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Пешка (Glass Style)")
        self.resize(1000, 850)

        self.logic = PawnLogic()
        self.current_point_item = None
        self.mesh_items = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # --- 1. 3D View ---
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor(40, 44, 52) 
        self.view.setCameraPosition(distance=15, elevation=20, azimuth=45)
        
        # Сетка
        g = gl.GLGridItem()
        g.setSize(20, 20, 1)
        g.setSpacing(1, 1, 1)
        g.setColor((255, 255, 255, 60)) 
        self.view.addItem(g)
        
        # Оси
        axis = gl.GLAxisItem()
        axis.setSize(5, 5, 5)
        self.view.addItem(axis)
        
        self.main_layout.addWidget(self.view, stretch=2)

        # --- 2. Панель управления ---
        self.controls_group = QGroupBox("Настройки параметров")
        self.controls_layout = QGridLayout()
        self.controls_group.setLayout(self.controls_layout)
        self.controls_group.setMaximumHeight(350)
        
        self.main_layout.addWidget(self.controls_group, stretch=1)

        row = 0
        self.sliders = {}

        # Добавляем слайдеры
        row = self.add_slider("Шар Radius", "sphere_r", 0.3, 1.5, 0.8, row, 0)
        
        row = 0
        row = self.add_slider("Эллипсоид Rx (Ширина)", "ellip_rx", 0.3, 1.5, 0.8, row, 1)
        row = self.add_slider("Эллипсоид Ry (Высота)", "ellip_ry", 0.1, 1.0, 0.4, row, 1)
        row = self.add_slider("Эллипсоид Rz (Глубина)", "ellip_rz", 0.3, 1.5, 0.8, row, 1)

        row = 0
        row = self.add_slider("Параболоид A", "parab_a", 0.5, 2.0, 1.0, row, 2)
        row = self.add_slider("Параболоид B", "parab_b", 0.5, 2.0, 1.0, row, 2)
        row = self.add_slider("Параболоид H", "parab_h", 1.0, 3.0, 2.0, row, 2)

        row = 0
        row = self.add_slider("Цилиндр R", "cyl_r", 0.5, 3.0, 1.8, row, 3)
        row = self.add_slider("Цилиндр H", "cyl_h", 0.2, 1.5, 0.6, row, 3)

        # --- Секция проверки точки ---
        point_box = QGroupBox("Проверка точки")
        point_layout = QHBoxLayout()
        point_box.setLayout(point_layout)
        
        style_spin = "QDoubleSpinBox { font-size: 14px; padding: 5px; }"
        
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10, 10)
        self.spin_x.setSingleStep(0.1)
        self.spin_x.setPrefix("X: ")
        self.spin_x.setStyleSheet(style_spin)
        
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10, 10)
        self.spin_y.setSingleStep(0.1)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.setStyleSheet(style_spin)
        
        self.spin_z = QDoubleSpinBox()
        self.spin_z.setRange(-2, 15)
        self.spin_z.setValue(2.0)
        self.spin_z.setSingleStep(0.1)
        self.spin_z.setPrefix("Z (Высота): ")
        self.spin_z.setStyleSheet(style_spin)

        btn_check = QPushButton("Проверить")
        btn_check.setMinimumHeight(35)
        btn_check.clicked.connect(self.check_point)
        
        btn_random = QPushButton("Случайная")
        btn_random.setMinimumHeight(35)
        btn_random.clicked.connect(self.add_random_point)

        self.lbl_result = QLabel("...")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setStyleSheet("font-weight: bold; color: gray; border: 1px solid #555; border-radius: 4px; padding: 5px;")
        self.lbl_result.setMinimumWidth(120)

        point_layout.addWidget(self.spin_x)
        point_layout.addWidget(self.spin_y)
        point_layout.addWidget(self.spin_z)
        point_layout.addWidget(btn_check)
        point_layout.addWidget(btn_random)
        point_layout.addWidget(self.lbl_result)

        self.main_layout.addWidget(point_box)

        self.update_pawn_visuals()

    def add_slider(self, label, param_name, min_v, max_v, def_v, row, col):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 0, 5, 10)
        
        lbl = QLabel(f"{label}: {def_v}")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(int(min_v*10), int(max_v*10))
        slider.setValue(int(def_v*10))
        
        def on_change(val):
            real_val = val / 10.0
            lbl.setText(f"{label}: {real_val}")
            setattr(self.logic, param_name, real_val)
            self.update_pawn_visuals()
            if self.current_point_item:
                self.check_point()

        slider.valueChanged.connect(on_change)
        
        self.sliders[param_name] = slider
        layout.addWidget(lbl)
        layout.addWidget(slider)
        
        self.controls_layout.addWidget(container, row, col)
        return row + 1

    def create_glass_item(self, mesh_data):
        """Создает полупрозрачный (стеклянный) элемент"""
        # RGBA: Светло-серый, 30% непрозрачности
        glass_color = (0.8, 0.8, 0.8, 1)
        
        item = gl.GLMeshItem(
            meshdata=mesh_data, 
            smooth=True, 
            color=glass_color, 
            shader='shaded', 
            glOptions='translucent' # параметр для прозрачности
        )
        return item

    def update_pawn_visuals(self):
        # Удаление старых элементов
        for item in self.mesh_items:
            try:
                self.view.removeItem(item)
            except:
                pass
        self.mesh_items.clear()

        p = self.logic
        
        # 1. Цилиндр
        md_cyl = create_cylinder_mesh(p.cyl_r, p.cyl_h, 0)
        item_cyl = self.create_glass_item(md_cyl)
        self.view.addItem(item_cyl)
        self.mesh_items.append(item_cyl)
        
        current_z = p.cyl_h

        # 2. Параболоид
        md_par = create_paraboloid_mesh(p.parab_a, p.parab_b, p.parab_h, current_z)
        item_par = self.create_glass_item(md_par)
        self.view.addItem(item_par)
        self.mesh_items.append(item_par)
        
        current_z += p.parab_h

        # 3. Эллипсоид
        md_ell = create_ellipsoid_mesh(p.ellip_rx, p.ellip_ry, p.ellip_rz, current_z)
        item_ell = self.create_glass_item(md_ell)
        self.view.addItem(item_ell)
        self.mesh_items.append(item_ell)
        
        current_z += p.ellip_ry * 2

        # 4. Шар
        md_sph = create_sphere_mesh(p.sphere_r, current_z)
        item_sph = self.create_glass_item(md_sph)
        self.view.addItem(item_sph)
        self.mesh_items.append(item_sph)

    def add_random_point(self):
        max_r = max(self.logic.cyl_r, self.logic.parab_a, self.logic.sphere_r) * 1.2
        total_h = (self.logic.cyl_h + self.logic.parab_h + 
                   self.logic.ellip_ry * 2 + self.logic.sphere_r * 2)
        
        angle = np.random.uniform(0, 2*np.pi)
        r = np.random.uniform(0, max_r)
        
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        z = np.random.uniform(0, total_h * 1.1)
        
        self.spin_x.setValue(x)
        self.spin_y.setValue(y)
        self.spin_z.setValue(z)
        self.check_point()

    def check_point(self):
        x = self.spin_x.value()
        y = self.spin_y.value()
        z = self.spin_z.value()

        if self.current_point_item:
            try:
                self.view.removeItem(self.current_point_item)
            except:
                pass

        is_inside = self.logic.is_point_in_pawn(x, y, z)

        # Яркий непрозрачный шарик для точки
        color = (0.2, 1.0, 0.2, 1.0) if is_inside else (1.0, 0.2, 0.2, 1.0) 
        
        md_point = gl.MeshData.sphere(rows=10, cols=10, radius=0.15)
        self.current_point_item = gl.GLMeshItem(meshdata=md_point, color=color, shader='shaded')
        self.current_point_item.translate(x, y, z)
        self.view.addItem(self.current_point_item)

        if is_inside:
            self.lbl_result.setText("ВНУТРИ")
            self.lbl_result.setStyleSheet("font-weight: bold; color: #4CAF50; border: 2px solid #4CAF50; background: #E8F5E9; border-radius: 4px; padding: 5px;")
        else:
            self.lbl_result.setText("СНАРУЖИ")
            self.lbl_result.setStyleSheet("font-weight: bold; color: #F44336; border: 2px solid #F44336; background: #FFEBEE; border-radius: 4px; padding: 5px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())