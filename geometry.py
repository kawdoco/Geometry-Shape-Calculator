# geometry_oop_with_astronomy.py (Enhanced Version)
import sys
import math
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QPainter
from abc import ABC, abstractmethod
from enum import Enum
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView,
    QSizePolicy, QCheckBox, QGroupBox, QTextEdit, QTabWidget, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QPixmap, QIcon
from PyQt5.QtCore import QPointF, QRectF, Qt, QSize

# ----------------- Enums for better code readability -----------------
class ShapeType(Enum):
    CIRCLE = "Circle"
    RECTANGLE = "Rectangle"
    TRIANGLE = "Triangle"
    SQUARE = "Square"
    ELLIPSE = "Ellipse"
    PARALLELOGRAM = "Parallelogram"
    RHOMBUS = "Rhombus"
    PENTAGON = "Pentagon"
    SPHERE = "Sphere"  # 3D shape
    CUBE = "Cube"      # 3D shape


class AlignmentType(Enum):
    CENTER = "Center"
    TOP = "Top"
    BOTTOM = "Bottom"
    LEFT = "Left"
    RIGHT = "Right"
    OVERLAP = "Overlap"
    ORBIT = "Orbit"  # New alignment type


# ----------------- Base / Abstract classes -----------------
class Shape(ABC):
    """Abstract base class for all shapes."""
    
    @abstractmethod
    def area(self):
        pass
        
    @abstractmethod
    def perimeter(self):
        pass
        
    @abstractmethod
    def volume(self):
        """For 3D shapes, returns volume. For 2D shapes, returns 0."""
        pass
        
    @abstractmethod
    def natural_size(self):
        """Return (width, height, depth) in the shape's own units (unscaled)."""
        pass
        
    @abstractmethod
    def draw(self, scene: QGraphicsScene, cx: float, cy: float, scale: float):
        """Draw shape centered at (cx, cy) with a scale factor (units -> pixels)."""
        pass
        
    def bounding_box(self, cx: float, cy: float, scale: float):
        """Return (x_min, y_min, x_max, y_max) in pixels for overlap detection."""
        w, h, _ = self.natural_size()
        w_px = w * scale
        h_px = h * scale
        return (cx - w_px/2, cy - h_px/2, cx + w_px/2, cy + h_px/2)
        
    def __str__(self):
        """String representation of the shape with its properties."""
        return f"{self.__class__.__name__}: Area={self.area():.2f}, Perimeter={self.perimeter():.2f}"


class Shape2D(Shape, ABC):
    """Abstract base class for 2D shapes."""
    
    def volume(self):
        return 0  # 2D shapes have no volume


class Shape3D(Shape, ABC):
    """Abstract base class for 3D shapes."""
    
    def perimeter(self):
        return 0  # 3D shapes typically don't have perimeter in the same sense


# ----------------- 2D Shapes -----------------
class Circle(Shape2D):
    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self._radius = radius

    def area(self):
        return math.pi * self._radius ** 2

    def perimeter(self):
        return 2 * math.pi * self._radius

    def natural_size(self):
        d = 2 * self._radius
        return (d, d, 0)  # 2D shape has depth=0

    def draw(self, scene, cx, cy, scale):
        diameter_px = 2 * self._radius * scale
        x = cx - diameter_px/2
        y = cy - diameter_px/2
        ellipse = scene.addEllipse(x, y, diameter_px, diameter_px)
        ellipse.setBrush(QBrush(QColor("lightblue")))
        ellipse.setPen(QPen(QColor("blue"), 3))
        ellipse.setZValue(1)


class Rectangle(Shape2D):
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self._width = width
        self._height = height

    def area(self):
        return self._width * self._height

    def perimeter(self):
        return 2 * (self._width + self._height)

    def natural_size(self):
        return (self._width, self._height, 0)

    def draw(self, scene, cx, cy, scale):
        w_px = self._width * scale
        h_px = self._height * scale
        x = cx - w_px/2
        y = cy - h_px/2
        rect = scene.addRect(x, y, w_px, h_px)
        rect.setBrush(QBrush(QColor("lightgreen")))
        rect.setPen(QPen(QColor("green"), 3))
        rect.setZValue(1)


class Triangle(Shape2D):
    def __init__(self, base, height):
        if base <= 0 or height <= 0:
            raise ValueError("Base and height must be positive")
        self._base = base
        self._height = height

    def area(self):
        return 0.5 * self._base * self._height

    def perimeter(self):
        hyp = math.sqrt(self._base**2 + self._height**2)
        return self._base + self._height + hyp

    def natural_size(self):
        return (self._base, self._height, 0)

    def draw(self, scene, cx, cy, scale):
        base_px = self._base * scale
        height_px = self._height * scale
        # center the triangle vertically at cy (apex up)
        points = [
            QPointF(cx, cy - height_px/2),
            QPointF(cx - base_px/2, cy + height_px/2),
            QPointF(cx + base_px/2, cy + height_px/2)
        ]
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(QColor("yellow")))
        item.setPen(QPen(QColor("orange"), 3))
        item.setZValue(1)


class Square(Shape2D):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return self._side ** 2

    def perimeter(self):
        return 4 * self._side

    def natural_size(self):
        return (self._side, self._side, 0)

    def draw(self, scene, cx, cy, scale):
        s_px = self._side * scale
        x = cx - s_px/2
        y = cy - s_px/2
        rect = scene.addRect(x, y, s_px, s_px)
        rect.setBrush(QBrush(QColor("pink")))
        rect.setPen(QPen(QColor("red"), 3))
        rect.setZValue(1)


class Ellipse(Shape2D):
    def __init__(self, a, b):
        if a <= 0 or b <= 0:
            raise ValueError("Axes must be positive")
        self._a = a  # semi-major
        self._b = b  # semi-minor

    def area(self):
        return math.pi * self._a * self._b

    def perimeter(self):
        h = ((self._a - self._b) ** 2) / ((self._a + self._b) ** 2)
        return math.pi * (self._a + self._b) * (1 + (3*h) / (10 + math.sqrt(4 - 3*h)))

    def natural_size(self):
        return (2 * self._a, 2 * self._b, 0)

    def draw(self, scene, cx, cy, scale):
        w_px = 2 * self._a * scale
        h_px = 2 * self._b * scale
        x = cx - w_px/2
        y = cy - h_px/2
        ellipse = scene.addEllipse(x, y, w_px, h_px)
        ellipse.setBrush(QBrush(QColor("lightyellow")))
        ellipse.setPen(QPen(QColor("brown"), 3))
        ellipse.setZValue(1)


class Parallelogram(Shape2D):
    def __init__(self, base, side, height):
        if base <= 0 or side <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")
        self._base = base
        self._side = side
        self._height = height

    def area(self):
        return self._base * self._height

    def perimeter(self):
        return 2 * (self._base + self._side)

    def natural_size(self):
        # give some horizontal extra for shear
        return (self._base + self._base * 0.2, self._height, 0)

    def draw(self, scene, cx, cy, scale):
        base_px = self._base * scale
        height_px = self._height * scale
        shear = base_px * 0.2
        x0 = cx - base_px/2
        y0 = cy - height_px/2
        points = [
            QPointF(x0, y0),
            QPointF(x0 + base_px, y0),
            QPointF(x0 + base_px + shear, y0 + height_px),
            QPointF(x0 + shear, y0 + height_px)
        ]
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(QColor("cyan")))
        item.setPen(QPen(QColor("darkblue"), 3))
        item.setZValue(1)


class Rhombus(Shape2D):
    def __init__(self, d1, d2):
        if d1 <= 0 or d2 <= 0:
            raise ValueError("Diagonals must be positive")
        self._d1 = d1
        self._d2 = d2

    def area(self):
        return (self._d1 * self._d2) / 2

    def perimeter(self):
        side = math.sqrt((self._d1/2)**2 + (self._d2/2)**2)
        return 4 * side

    def natural_size(self):
        return (self._d1, self._d2, 0)

    def draw(self, scene, cx, cy, scale):
        d1_px = self._d1 * scale
        d2_px = self._d2 * scale
        points = [
            QPointF(cx, cy - d2_px / 2),
            QPointF(cx + d1_px / 2, cy),
            QPointF(cx, cy + d2_px / 2),
            QPointF(cx - d1_px / 2, cy)
        ]
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(QColor("violet")))
        item.setPen(QPen(QColor("purple"), 3))
        item.setZValue(1)


class Pentagon(Shape2D):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return (5 * self._side**2) / (4 * math.tan(math.pi/5))

    def perimeter(self):
        return 5 * self._side

    def natural_size(self):
        # approximate bounding box using circumradius ≈ 1.539 * side
        r = 1.539 * self._side
        return (2*r, 2*r, 0)

    def draw(self, scene, cx, cy, scale):
        r_px = 1.539 * self._side * scale
        points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5 - math.pi/2
            x = cx + r_px * math.cos(angle)
            y = cy + r_px * math.sin(angle)
            points.append(QPointF(x, y))
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(QColor("orange")))
        item.setPen(QPen(QColor("darkred"), 3))
        item.setZValue(1)


# ----------------- 3D Shapes -----------------
class Sphere(Shape3D):
    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self._radius = radius

    def area(self):
        return 4 * math.pi * self._radius ** 2

    def volume(self):
        return (4/3) * math.pi * self._radius ** 3

    def natural_size(self):
        d = 2 * self._radius
        return (d, d, d)

    def draw(self, scene, cx, cy, scale):
        # Represent 3D sphere as a circle with shading
        diameter_px = 2 * self._radius * scale
        x = cx - diameter_px/2
        y = cy - diameter_px/2
        
        # Draw main circle
        ellipse = scene.addEllipse(x, y, diameter_px, diameter_px)
        ellipse.setBrush(QBrush(QColor(100, 100, 200)))  # Darker blue
        ellipse.setPen(QPen(QColor(50, 50, 150), 3))
        ellipse.setZValue(1)
        
        # Draw highlight to give 3D effect
        highlight_diameter = diameter_px * 0.6
        highlight_x = x + diameter_px * 0.2
        highlight_y = y + diameter_px * 0.2
        highlight = scene.addEllipse(highlight_x, highlight_y, 
                                    highlight_diameter, highlight_diameter)
        highlight.setBrush(QBrush(QColor(150, 150, 255, 100)))  # Semi-transparent
        highlight.setPen(QPen(Qt.NoPen))
        highlight.setZValue(2)


class Cube(Shape3D):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return 6 * self._side ** 2

    def volume(self):
        return self._side ** 3

    def natural_size(self):
        return (self._side, self._side, self._side)

    def draw(self, scene, cx, cy, scale):
        side_px = self._side * scale
        x = cx - side_px/2
        y = cy - side_px/2
        
        # Draw front face
        front = scene.addRect(x, y, side_px, side_px)
        front.setBrush(QBrush(QColor(200, 100, 100)))  # Reddish
        front.setPen(QPen(QColor(150, 50, 50), 3))
        front.setZValue(1)
        
        # Draw top face (perspective)
        top_points = [
            QPointF(x, y),
            QPointF(x + side_px, y),
            QPointF(x + side_px * 0.8, y - side_px * 0.2),
            QPointF(x - side_px * 0.2, y - side_px * 0.2)
        ]
        top = scene.addPolygon(QPolygonF(top_points))
        top.setBrush(QBrush(QColor(180, 80, 80)))  # Slightly darker
        top.setPen(QPen(QColor(130, 40, 40), 3))
        top.setZValue(0)
        
        # Draw side face (perspective)
        side_points = [
            QPointF(x + side_px, y),
            QPointF(x + side_px, y + side_px),
            QPointF(x + side_px * 0.8, y + side_px * 0.8),
            QPointF(x + side_px * 0.8, y - side_px * 0.2)
        ]
        side = scene.addPolygon(QPolygonF(side_points))
        side.setBrush(QBrush(QColor(170, 70, 70)))  # Even darker
        side.setPen(QPen(QColor(120, 30, 30), 3))
        side.setZValue(0)


# ----------------- Astronomical Object -----------------
class AstronomicalObject:
    """Represents astronomical objects for alignment demonstration."""
    
    def __init__(self, radius, color="lightgray", name="Planet"):
        if radius <= 0:
            raise ValueError("Astronomical radius must be positive")
        self._radius = radius
        self._color = color
        self._name = name

    def natural_size(self):
        return (2 * self._radius, 2 * self._radius, 2 * self._radius)

    def draw(self, scene, cx, cy, scale):
        diameter_px = 2 * self._radius * scale
        x = cx - diameter_px/2
        y = cy - diameter_px/2
        
        # Draw the astronomical object
        item = scene.addEllipse(x, y, diameter_px, diameter_px)
        item.setBrush(QBrush(QColor(self._color)))
        item.setPen(QPen(QColor("black"), 2))
        item.setZValue(0)  # behind shapes
        
        # Add a label
        text = scene.addText(self._name)
        text.setDefaultTextColor(QColor("white"))
        text.setPos(cx - text.boundingRect().width()/2, 
                   cy - text.boundingRect().height()/2)
        text.setZValue(1)

    def bounding_box(self, cx, cy, scale):
        d = 2 * self._radius * scale
        return (cx - d/2, cy - d/2, cx + d/2, cy + d/2)
        
    def calculate_alignment_position(self, shape, alignment, scene_rect, scale):
        """Calculate position for shape based on alignment with this astronomical object."""
        scene_w = scene_rect.width()
        scene_h = scene_rect.height()
        
        # Center of astronomical object
        astro_cx = scene_w / 2
        astro_cy = scene_h / 2
        
        # Shape dimensions in pixels
        shape_w, shape_h, _ = shape.natural_size()
        shape_w_px = shape_w * scale
        shape_h_px = shape_h * scale
        
        # Astronomical object radius in pixels
        astro_radius_px = self._radius * scale
        
        margin = 10  # Pixel margin
        
        if alignment == AlignmentType.CENTER:
            return (astro_cx, astro_cy)
        elif alignment == AlignmentType.TOP:
            return (astro_cx, astro_cy - astro_radius_px - shape_h_px/2 - margin)
        elif alignment == AlignmentType.BOTTOM:
            return (astro_cx, astro_cy + astro_radius_px + shape_h_px/2 + margin)
        elif alignment == AlignmentType.LEFT:
            return (astro_cx - astro_radius_px - shape_w_px/2 - margin, astro_cy)
        elif alignment == AlignmentType.RIGHT:
            return (astro_cx + astro_radius_px + shape_w_px/2 + margin, astro_cy)
        elif alignment == AlignmentType.OVERLAP:
            return (astro_cx + 0.15 * astro_radius_px, astro_cy + 0.10 * astro_radius_px)
        elif alignment == AlignmentType.ORBIT:
            # Position in a circular orbit around the astronomical object
            angle = 45  # 45 degree angle for demonstration
            orbit_radius = astro_radius_px + shape_w_px/2 + margin
            x = astro_cx + orbit_radius * math.cos(math.radians(angle))
            y = astro_cy + orbit_radius * math.sin(math.radians(angle))
            return (x, y)
        else:
            return (astro_cx, astro_cy)


# ----------------- Shape Factory -----------------
class ShapeFactory:
    """Factory class to create shape instances based on type and parameters."""
    
    @staticmethod
    def create_shape(shape_type, params):
        if shape_type == ShapeType.CIRCLE:
            return Circle(params[0])
        elif shape_type == ShapeType.RECTANGLE:
            return Rectangle(params[0], params[1])
        elif shape_type == ShapeType.TRIANGLE:
            return Triangle(params[0], params[1])
        elif shape_type == ShapeType.SQUARE:
            return Square(params[0])
        elif shape_type == ShapeType.ELLIPSE:
            return Ellipse(params[0], params[1])
        elif shape_type == ShapeType.PARALLELOGRAM:
            return Parallelogram(params[0], params[1], params[2])
        elif shape_type == ShapeType.RHOMBUS:
            return Rhombus(params[0], params[1])
        elif shape_type == ShapeType.PENTAGON:
            return Pentagon(params[0])
        elif shape_type == ShapeType.SPHERE:
            return Sphere(params[0])
        elif shape_type == ShapeType.CUBE:
            return Cube(params[0])
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")


# ----------------- GUI Application -----------------
class GeometryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌌 Geometric Universe Explorer")
        self.setGeometry(100, 100, 1200, 900)  # Larger window for better layout
        
        # Initialize attributes
        self.current_shape = None
        self.astro_object = None
        self.history = []  # Store calculation history
        
        # Set application style
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #555555;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton#special {
                background-color: #e67c73;
            }
            QPushButton#special:hover {
                background-color: #d66c63;
            }
            QPushButton#save {
                background-color: #0f9d58;
            }
            QPushButton#save:hover {
                background-color: #0e8d48;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                color: #333333;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #6a11cb, stop: 1 #2575fc);
                border-radius: 8px;
                color: white;
            }
            QTextEdit, QGraphicsView {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QHBoxLayout()
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout()
        
        # Title
        title = QLabel("🌌 Geometric Universe Explorer")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # Create tabs for better organization
        tabs = QTabWidget()
        
        # Shape tab
        shape_tab = QWidget()
        shape_layout = QVBoxLayout(shape_tab)
        
        # Shape selection
        shape_group = QGroupBox("🔷 Shape Properties")
        shape_group_layout = QVBoxLayout()
        
        shape_type_row = QHBoxLayout()
        shape_type_row.addWidget(QLabel("Shape Type:"))
        self.shape_menu = QComboBox()
        self.shape_menu.addItems([shape.value for shape in ShapeType])
        self.shape_menu.currentIndexChanged.connect(self.update_input_fields)
        shape_type_row.addWidget(self.shape_menu)
        shape_group_layout.addLayout(shape_type_row)
        
        # Input fields
        self.inputs_layout = QVBoxLayout()
        self.setup_input_fields()
        shape_group_layout.addLayout(self.inputs_layout)
        
        shape_group.setLayout(shape_group_layout)
        shape_layout.addWidget(shape_group)
        
        tabs.addTab(shape_tab, "🟦 Shape")
        
        # Astronomy tab
        astro_tab = QWidget()
        astro_layout = QVBoxLayout(astro_tab)
        
        astro_group = QGroupBox("🌠 Astronomy Settings")
        astro_group_layout = QVBoxLayout()
        
        astro_type_row = QHBoxLayout()
        astro_type_row.addWidget(QLabel("Celestial Body:"))
        self.astro_menu = QComboBox()
        self.astro_menu.addItems(["None", "Planet", "Star", "Moon", "Black Hole"])
        self.astro_menu.currentIndexChanged.connect(self.update_astro_fields)
        astro_type_row.addWidget(self.astro_menu)
        astro_group_layout.addLayout(astro_type_row)
        
        astro_params_row = QHBoxLayout()
        astro_params_row.addWidget(QLabel("Radius:"))
        self.astro_radius_entry = QLineEdit()
        self.astro_radius_entry.setPlaceholderText("50-200")
        astro_params_row.addWidget(self.astro_radius_entry)
        astro_group_layout.addLayout(astro_params_row)
        
        alignment_row = QHBoxLayout()
        alignment_row.addWidget(QLabel("Alignment:"))
        self.align_menu = QComboBox()
        self.align_menu.addItems([align.value for align in AlignmentType])
        alignment_row.addWidget(self.align_menu)
        astro_group_layout.addLayout(alignment_row)
        
        astro_group.setLayout(astro_group_layout)
        astro_layout.addWidget(astro_group)
        
        tabs.addTab(astro_tab, "🌌 Astronomy")
        
        left_layout.addWidget(tabs)
        
        # Action buttons
        button_row = QHBoxLayout()
        self.calc_btn = QPushButton("🖌️ Draw & Calculate")
        self.calc_btn.clicked.connect(self.calculate)
        self.calc_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        button_row.addWidget(self.calc_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setObjectName("special")
        button_row.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setObjectName("save")
        button_row.addWidget(self.save_btn)
        
        left_layout.addLayout(button_row)
        
        # Results display
        results_group = QGroupBox("📊 Results")
        results_layout = QVBoxLayout()
        self.result_label = QLabel("⏳ Results will be shown here.")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(120)
        self.result_label.setStyleSheet("background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd; border-radius: 4px;")
        results_layout.addWidget(self.result_label)
        results_group.setLayout(results_layout)
        left_layout.addWidget(results_group)
        
        # Status bar
        self.status_label = QLabel("🚀 Ready to explore the geometric universe!")
        self.status_label.setStyleSheet("background-color: #e8e8e8; padding: 8px; border-radius: 4px; color: #555;")
        left_layout.addWidget(self.status_label)
        
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)
        
        # Right panel for visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Visualization title
        viz_title = QLabel("🔭 Visualization Canvas")
        viz_title.setStyleSheet("font-weight: bold; font-size: 16px; padding: 5px; background-color: #e0e0ff; border-radius: 4px;")
        viz_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(viz_title)
        
        # Graphics area
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(700, 600)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("background-color: #f0f0f0; border: 2px solid #cccccc;")
        right_layout.addWidget(self.view)
        
        # Info panel below visualization
        info_group = QGroupBox("ℹ️ Visualization Info")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("• Select a shape and astronomical object\n• Choose an alignment type\n• Click 'Draw & Calculate' to visualize")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("padding: 8px;")
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)
        
        # Initialize UI state
        self.update_input_fields()
        self.update_astro_fields()
        
        # Initialize scene rect
        self.scene.setSceneRect(0, 0, 700, 600)
        
    def setup_input_fields(self):
        """Setup the input fields based on current shape selection."""
        # Clear existing fields
        for i in reversed(range(self.inputs_layout.count())):
            item = self.inputs_layout.itemAt(i)
            if item.layout():
                # Clear layout and its widgets
                for j in reversed(range(item.layout().count())):
                    widget = item.layout().itemAt(j).widget()
                    if widget:
                        widget.deleteLater()
                self.inputs_layout.removeItem(item)
            elif item.widget():
                # Remove widget directly
                item.widget().deleteLater()
        
        shape_type = ShapeType(self.shape_menu.currentText())
        
        # Add appropriate input fields based on shape type
        if shape_type in [ShapeType.CIRCLE, ShapeType.SPHERE]:
            # One parameter needed - radius
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel("Radius:"))
            entry = QLineEdit()
            entry.setPlaceholderText("Enter radius")
            field_layout.addWidget(entry)
            self.inputs_layout.addLayout(field_layout)
            
        elif shape_type in [ShapeType.SQUARE, ShapeType.CUBE, ShapeType.PENTAGON]:
            # One parameter needed - side
            param_name = "Side"
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(f"{param_name}:"))
            entry = QLineEdit()
            entry.setPlaceholderText(f"Enter {param_name.lower()}")
            field_layout.addWidget(entry)
            self.inputs_layout.addLayout(field_layout)
            
        elif shape_type == ShapeType.RECTANGLE:
            # Two parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Width:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter width")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)
            
            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Height:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter height")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)
            
        elif shape_type == ShapeType.TRIANGLE:
            # Two parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Base:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter base")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)
            
            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Height:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter height")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)
            
        elif shape_type == ShapeType.ELLIPSE:
            # Two parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Major axis:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter major axis")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)
            
            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Minor axis:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter minor axis")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)
            
        elif shape_type == ShapeType.RHOMBUS:
            # Two parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Diagonal 1:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter diagonal 1")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)
            
            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Diagonal 2:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter diagonal 2")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)
            
        elif shape_type == ShapeType.PARALLELOGRAM:
            # Three parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Base:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter base")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)
            
            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Side:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter side")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)
            
            field_layout3 = QHBoxLayout()
            field_layout3.addWidget(QLabel("Height:"))
            entry3 = QLineEdit()
            entry3.setPlaceholderText("Enter height")
            field_layout3.addWidget(entry3)
            self.inputs_layout.addLayout(field_layout3)
    
    def update_input_fields(self):
        """Update the input fields when shape selection changes."""
        self.setup_input_fields()
        
    def update_astro_fields(self):
        """Show/hide astronomical object fields based on selection."""
        show_astro = self.astro_menu.currentText() != "None"
        self.astro_radius_entry.setVisible(show_astro)
        self.align_menu.setVisible(show_astro)
        
    def get_shape_parameters(self):
        """Get parameters from input fields based on current shape selection."""
        shape_type = ShapeType(self.shape_menu.currentText())
        params = []

        # Collect all numeric values from input fields
        for i in range(self.inputs_layout.count()):
            layout = self.inputs_layout.itemAt(i)
            if isinstance(layout, QHBoxLayout):
                # Get the input field (should be at position 1 in the layout)
                if layout.count() > 1:
                    widget = layout.itemAt(1).widget()
                    if isinstance(widget, QLineEdit) and widget.text():
                        try:
                            param_value = float(widget.text())
                            if param_value <= 0:
                                raise ValueError("All values must be positive")
                            if param_value > 10000:
                                reply = QMessageBox.question(self, "Large Value", 
                                                           f"Value {param_value} is very large. This may cause visualization issues. Continue?",
                                                           QMessageBox.Yes | QMessageBox.No)
                                if reply == QMessageBox.No:
                                    return []
                            params.append(param_value)
                        except ValueError:
                            raise ValueError(f"Invalid number: {widget.text()}")

        # Validate parameter count
        required_params = 1
        if shape_type in [ShapeType.RECTANGLE, ShapeType.TRIANGLE, ShapeType.ELLIPSE, ShapeType.RHOMBUS]:
            required_params = 2
        elif shape_type == ShapeType.PARALLELOGRAM:
            required_params = 3

        if len(params) != required_params:
            raise ValueError(f"This shape requires {required_params} parameters")

        return params
        
    def calculate(self):
        """Main calculation and drawing method."""
        try:
            # Get shape parameters and create shape
            shape_type = ShapeType(self.shape_menu.currentText())
            params = self.get_shape_parameters()
            if not params:  # User cancelled due to large values
                return
                
            self.current_shape = ShapeFactory.create_shape(shape_type, params)
            
            # Create astronomical object if selected
            self.astro_object = None
            if self.astro_menu.currentText() != "None":
                if not self.astro_radius_entry.text():
                    raise ValueError("Please enter astronomical object radius")
                astro_radius = float(self.astro_radius_entry.text())
                if astro_radius <= 0:
                    raise ValueError("Astronomical radius must be positive")
                self.astro_object = AstronomicalObject(astro_radius, name=self.astro_menu.currentText())
            
            # Calculate scale and positions
            scene_rect = self.scene.sceneRect()
            if scene_rect.width() == 0 or scene_rect.height() == 0:
                scene_rect = QRectF(0, 0, self.view.width(), self.view.height())
                self.scene.setSceneRect(scene_rect)
                
            scale = self.calculate_scale(scene_rect)
            alignment = AlignmentType(self.align_menu.currentText())
            
            # Calculate positions
            if self.astro_object:
                astro_x, astro_y = scene_rect.width() / 2, scene_rect.height() / 2
                shape_x, shape_y = self.astro_object.calculate_alignment_position(
                    self.current_shape, alignment, scene_rect, scale)
            else:
                astro_x = astro_y = None
                shape_x, shape_y = scene_rect.width() / 2, scene_rect.height() / 2
            
            # Draw everything
            self.scene.clear()
            
            # Add a subtle grid to the background
            self.draw_grid(scene_rect)
            
            if self.astro_object:
                self.astro_object.draw(self.scene, astro_x, astro_y, scale)
            self.current_shape.draw(self.scene, shape_x, shape_y, scale)
            
            # Add position markers and connection line
            if self.astro_object:
                # Draw center markers
                self.scene.addEllipse(astro_x-3, astro_y-3, 6, 6, QPen(Qt.green, 2))
                self.scene.addEllipse(shape_x-3, shape_y-3, 6, 6, QPen(Qt.red, 2))
                
                # Add labels
                astro_text = self.scene.addText("Center")
                astro_text.setDefaultTextColor(Qt.darkGreen)
                astro_text.setPos(astro_x + 10, astro_y - 15)
                
                shape_text = self.scene.addText("Shape")
                shape_text.setDefaultTextColor(Qt.darkRed)
                shape_text.setPos(shape_x + 10, shape_y - 15)
                
                # Draw line between centers
                self.scene.addLine(astro_x, astro_y, shape_x, shape_y, QPen(Qt.blue, 1, Qt.DashLine))
            
            # Calculate and display results
            self.display_results()
            
            # Add to history
            self.add_to_history()
            
            # Update info label
            alignment_name = alignment.value if self.astro_object else "Center"
            self.info_label.setText(
                f"• Shape: {shape_type.value}\n"
                f"• Celestial Body: {self.astro_menu.currentText() if self.astro_object else 'None'}\n"
                f"• Alignment: {alignment_name}\n"
                f"• Scale: {scale:.2f} px/unit"
            )
            
            self.status_label.setText("✅ Calculation completed successfully!")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))
            
    def draw_grid(self, scene_rect):
        """Draw a subtle grid in the background."""
        width = scene_rect.width()
        height = scene_rect.height()
        
        # Draw horizontal lines
        for y in range(0, int(height), 50):
            self.scene.addLine(0, y, width, y, QPen(QColor(220, 220, 220), 0.5))
            
        # Draw vertical lines
        for x in range(0, int(width), 50):
            self.scene.addLine(x, 0, x, height, QPen(QColor(220, 220, 220), 0.5))
            
        # Draw axes
        center_x = width / 2
        center_y = height / 2
        self.scene.addLine(0, center_y, width, center_y, QPen(Qt.gray, 1))
        self.scene.addLine(center_x, 0, center_x, height, QPen(Qt.gray, 1))
        
    def calculate_scale(self, scene_rect):
        """Calculate appropriate scale to fit both shape and astronomical object."""
        scene_w = scene_rect.width()
        scene_h = scene_rect.height()
        
        if scene_w == 0 or scene_h == 0:
            return 1.0
            
        # Get natural sizes
        shape_w, shape_h, _ = self.current_shape.natural_size()
        
        if self.astro_object:
            astro_w, astro_h, _ = self.astro_object.natural_size()
            
            # Handle extreme size differences
            size_ratio = max(astro_w / max(shape_w, 0.001), astro_h / max(shape_h, 0.001))
            
            if size_ratio > 100:  # Astronomical object is much larger
                # Scale based on astronomical object but ensure shape is visible
                scale_x = (scene_w * 0.4) / astro_w if astro_w > 0 else 1
                scale_y = (scene_h * 0.4) / astro_h if astro_h > 0 else 1
            else:
                # Scale based on largest object
                max_w = max(shape_w, astro_w)
                max_h = max(shape_h, astro_h)
                scale_x = (scene_w * 0.8) / max_w if max_w > 0 else 1
                scale_y = (scene_h * 0.8) / max_h if max_h > 0 else 1
        else:
            # Scale based on shape only
            scale_x = (scene_w * 0.8) / shape_w if shape_w > 0 else 1
            scale_y = (scene_h * 0.8) / shape_h if shape_h > 0 else 1
        
        return min(scale_x, scale_y)
        
    def display_results(self):
        """Display calculation results."""
        if not self.current_shape:
            return
            
        result_text = f"<h3>{self.current_shape.__class__.__name__} Properties</h3>"
        result_text += f"<b>Area:</b> {self.current_shape.area():.2f}<br>"
        result_text += f"<b>Perimeter:</b> {self.current_shape.perimeter():.2f}<br>"
        
        volume = self.current_shape.volume()
        if volume > 0:
            result_text += f"<b>Volume:</b> {volume:.2f}<br>"
            
        # Add dimensions
        w, h, d = self.current_shape.natural_size()
        if d > 0:
            result_text += f"<b>Dimensions:</b> {w:.1f} × {h:.1f} × {d:.1f}<br>"
        else:
            result_text += f"<b>Dimensions:</b> {w:.1f} × {h:.1f}<br>"
            
        if self.astro_object:
            # Check for overlap
            scene_rect = self.scene.sceneRect()
            scale = self.calculate_scale(scene_rect)
            
            astro_x, astro_y = scene_rect.width() / 2, scene_rect.height() / 2
            alignment = AlignmentType(self.align_menu.currentText())
            shape_x, shape_y = self.astro_object.calculate_alignment_position(
                self.current_shape, alignment, scene_rect, scale)
                
            astro_bb = self.astro_object.bounding_box(astro_x, astro_y, scale)
            shape_bb = self.current_shape.bounding_box(shape_x, shape_y, scale)
            
            overlap = self.check_overlap(astro_bb, shape_bb)
            result_text += f"<b>Overlap with {self.astro_menu.currentText()}:</b> {'Yes' if overlap else 'No'}<br>"
            
        self.result_label.setText(result_text)
        
    def add_to_history(self):
        """Add current calculation to history."""
        history_entry = {
            'shape': self.current_shape.__class__.__name__,
            'astro': self.astro_menu.currentText(),
            'result': self.result_label.text()
        }
        self.history.append(history_entry)
        # Keep only last 10 entries
        if len(self.history) > 10:
            self.history.pop(0)
            
    def save_results(self):
        """Save results to a text file."""
        try:
            filename = "geometry_results.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Geometry Calculation Results\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Shape: {self.current_shape.__class__.__name__ if self.current_shape else 'None'}\n")
                f.write(f"Astronomical Object: {self.astro_menu.currentText()}\n")
                f.write(f"Alignment: {self.align_menu.currentText()}\n\n")
                f.write("Results:\n")
                f.write(self.result_label.text().replace('<br>', '\n').replace('<b>', '').replace('</b>', '').replace('<h3>', '').replace('</h3>', ''))
                f.write("\n\nCalculation History:\n")
                for i, entry in enumerate(self.history, 1):
                    f.write(f"{i}. {entry['shape']} with {entry['astro']}\n")
            
            QMessageBox.information(self, "Saved", f"Results saved to {filename}")
            self.status_label.setText(f"💾 Results saved to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save results: {str(e)}")
        
    def clear_all(self):
        """Clear all inputs, results, and the visualization."""
        # Clear the graphics scene
        self.scene.clear()
    
    # Clear input fields
        for i in range(self.inputs_layout.count()):
            layout = self.inputs_layout.itemAt(i)
        if isinstance(layout, QHBoxLayout):
            # Get the input field (should be at position 1 in the layout)
            if layout.count() > 1:
                widget = layout.itemAt(1).widget()
                if isinstance(widget, QLineEdit):
                    widget.clear()
    
    # Clear astronomical object fields
        self.astro_radius_entry.clear()
    
    # Reset selections to defaults
        self.shape_menu.setCurrentIndex(0)
        self.astro_menu.setCurrentIndex(0)
        self.align_menu.setCurrentIndex(0)
    
    # Clear results
        self.result_label.setText("⏳ Results will be shown here.")

        # Reset info label
        self.info_label.setText("• Select a shape and astronomical object\n• Choose an alignment type\n• Click 'Draw & Calculate' to visualize")

        # Reset shape and astronomical object references
        self.current_shape = None
        self.astro_object = None

        # Update status
        self.status_label.setText("🔄 All inputs cleared. Ready for new calculation.")
        
    def check_overlap(self, rect1, rect2):
        """Check if two rectangles overlap."""
        x1_min, y1_min, x1_max, y1_max = rect1
        x2_min, y2_min, x2_max, y2_max = rect2
        
        return not (x1_max < x2_min or x2_max < x1_min or 
                   y1_max < y2_min or y2_max < y1_min)
        
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Update scene size when window is resized
        if hasattr(self, 'view'):
            size = self.view.size()
            self.scene.setSceneRect(0, 0, size.width(), size.height())
            # Redraw if we have content
            if self.current_shape:
                self.calculate()


# ----------------- Run -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeometryApp()
    window.show()
    sys.exit(app.exec_())

