# geometry_oop_with_astronomy_enhanced.py
# Improved UI: added toolbar (zoom/reset/snapshot), keyboard shortcuts, grid toggle,
# accessibility names/tooltips, better color dialog usage, improved animation timing,
# and various UX refinements (validation messages, helpful defaults).
# Add this import near your other PyQt imports at the top of the file:
from PyQt5.QtWidgets import QColorDialog, QAction
import sys
import math
import json
from datetime import datetime
from PyQt5.QtGui import (
    QPolygonF, QBrush, QPen, QColor, QFont, QPainter, QPixmap, QIcon, QImage
)
from abc import ABC, abstractmethod
from enum import Enum
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView,
    QSizePolicy, QCheckBox, QGroupBox, QTextEdit, QTabWidget, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QFileDialog, QSlider, QDoubleSpinBox,
    QColorDialog, QToolBar, QAction, QShortcut
)
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QPixmap, QIcon, QKeySequence
from PyQt5.QtCore import QPointF, QRectF, Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve

# ----------------- Enums for better code readability -----------------
class ShapeType(Enum):
    # 2D Shapes
    CIRCLE = "Circle"
    RECTANGLE = "Rectangle"
    TRIANGLE = "Triangle"
    SQUARE = "Square"
    ELLIPSE = "Ellipse"
    PARALLELOGRAM = "Parallelogram"
    RHOMBUS = "Rhombus"
    PENTAGON = "Pentagon"
    HEXAGON = "Hexagon"
    OCTAGON = "Octagon"
    STAR = "Star"
    # 3D Shapes
    SPHERE = "Sphere"
    CUBE = "Cube"
    CYLINDER = "Cylinder"
    CONE = "Cone"
    PYRAMID = "Pyramid"


class AlignmentType(Enum):
    CENTER = "Center"
    TOP = "Top"
    BOTTOM = "Bottom"
    LEFT = "Left"
    RIGHT = "Right"
    OVERLAP = "Overlap"
    ORBIT = "Orbit"
    RANDOM = "Random"


class ThemeType(Enum):
    LIGHT = "Light"
    DARK = "Dark"
    BLUE = "Blue"
    GREEN = "Green"
    COSMIC = "Cosmic"


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
    def draw(self, scene: QGraphicsScene, cx: float, cy: float, scale: float, color: QColor = None):
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
        try:
            return f"{self.__class__.__name__}: Area={self.area():.2f}, Perimeter={self.perimeter():.2f}"
        except Exception:
            return f"{self.__class__.__name__}"


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

    def draw(self, scene, cx, cy, scale, color=None):
        diameter_px = 2 * self._radius * scale
        x = cx - diameter_px/2
        y = cy - diameter_px/2

        fill_color = color if color else QColor("#4FC3F7")
        border_color = fill_color.darker(150)

        ellipse = scene.addEllipse(x, y, diameter_px, diameter_px)
        ellipse.setBrush(QBrush(fill_color))
        ellipse.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        w_px = self._width * scale
        h_px = self._height * scale
        x = cx - w_px/2
        y = cy - h_px/2

        fill_color = color if color else QColor("#81C784")
        border_color = fill_color.darker(150)

        rect = scene.addRect(x, y, w_px, h_px)
        rect.setBrush(QBrush(fill_color))
        rect.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        base_px = self._base * scale
        height_px = self._height * scale

        fill_color = color if color else QColor("#FFF176")
        border_color = fill_color.darker(150)

        # center the triangle vertically at cy (apex up)
        points = [
            QPointF(cx, cy - height_px/2),
            QPointF(cx - base_px/2, cy + height_px/2),
            QPointF(cx + base_px/2, cy + height_px/2)
        ]
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        s_px = self._side * scale
        x = cx - s_px/2
        y = cy - s_px/2

        fill_color = color if color else QColor("#FF8A65")
        border_color = fill_color.darker(150)

        rect = scene.addRect(x, y, s_px, s_px)
        rect.setBrush(QBrush(fill_color))
        rect.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        w_px = 2 * self._a * scale
        h_px = 2 * self._b * scale
        x = cx - w_px/2
        y = cy - h_px/2

        fill_color = color if color else QColor("#DCE775")
        border_color = fill_color.darker(150)

        ellipse = scene.addEllipse(x, y, w_px, h_px)
        ellipse.setBrush(QBrush(fill_color))
        ellipse.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        base_px = self._base * scale
        height_px = self._height * scale
        shear = base_px * 0.2
        x0 = cx - base_px/2
        y0 = cy - height_px/2

        fill_color = color if color else QColor("#4DD0E1")
        border_color = fill_color.darker(150)

        points = [
            QPointF(x0, y0),
            QPointF(x0 + base_px, y0),
            QPointF(x0 + base_px + shear, y0 + height_px),
            QPointF(x0 + shear, y0 + height_px)
        ]
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        d1_px = self._d1 * scale
        d2_px = self._d2 * scale

        fill_color = color if color else QColor("#BA68C8")
        border_color = fill_color.darker(150)

        points = [
            QPointF(cx, cy - d2_px / 2),
            QPointF(cx + d1_px / 2, cy),
            QPointF(cx, cy + d2_px / 2),
            QPointF(cx - d1_px / 2, cy)
        ]
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        r_px = 1.539 * self._side * scale

        fill_color = color if color else QColor("#FFB74D")
        border_color = fill_color.darker(150)

        points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5 - math.pi/2
            x = cx + r_px * math.cos(angle)
            y = cy + r_px * math.sin(angle)
            points.append(QPointF(x, y))
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
        item.setZValue(1)


class Hexagon(Shape2D):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return (3 * math.sqrt(3) * self._side**2) / 2

    def perimeter(self):
        return 6 * self._side

    def natural_size(self):
        # Bounding box: width = 2 * side, height = √3 * side
        width = 2 * self._side
        height = math.sqrt(3) * self._side
        return (width, height, 0)

    def draw(self, scene, cx, cy, scale, color=None):
        side_px = self._side * scale

        fill_color = color if color else QColor("#4DB6AC")
        border_color = fill_color.darker(150)

        points = []
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = cx + side_px * math.cos(angle)
            y = cy + side_px * math.sin(angle)
            points.append(QPointF(x, y))
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
        item.setZValue(1)


class Octagon(Shape2D):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return 2 * (1 + math.sqrt(2)) * self._side**2

    def perimeter(self):
        return 8 * self._side

    def natural_size(self):
        # Bounding box: width = height = (1 + √2) * side
        size = (1 + math.sqrt(2)) * self._side
        return (size, size, 0)

    def draw(self, scene, cx, cy, scale, color=None):
        r_px = self._side / math.cos(math.pi/8) * scale

        fill_color = color if color else QColor("#7986CB")
        border_color = fill_color.darker(150)

        points = []
        for i in range(8):
            angle = 2 * math.pi * i / 8 - math.pi/8
            x = cx + r_px * math.cos(angle)
            y = cy + r_px * math.sin(angle)
            points.append(QPointF(x, y))
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
        item.setZValue(1)


class Star(Shape2D):
    def __init__(self, outer_radius, inner_radius):
        if outer_radius <= 0 or inner_radius <= 0:
            raise ValueError("Radii must be positive")
        self._outer_radius = outer_radius
        self._inner_radius = inner_radius

    def area(self):
        # Approximation for a 5-pointed star
        return (5 * self._outer_radius * self._inner_radius *
                math.sin(math.pi/5) * math.sin(3*math.pi/10) /
                math.sin(7*math.pi/10))

    def perimeter(self):
        # Approximation: 10 * average of radii
        return 10 * (self._outer_radius + self._inner_radius) / 2

    def natural_size(self):
        return (2 * self._outer_radius, 2 * self._outer_radius, 0)

    def draw(self, scene, cx, cy, scale, color=None):
        outer_r_px = self._outer_radius * scale
        inner_r_px = self._inner_radius * scale

        fill_color = color if color else QColor("#FFD54F")
        border_color = fill_color.darker(150)

        points = []
        for i in range(10):
            angle = math.pi/2 + 2 * math.pi * i / 10
            r = outer_r_px if i % 2 == 0 else inner_r_px
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append(QPointF(x, y))
        polygon = QPolygonF(points)
        item = scene.addPolygon(polygon)
        item.setBrush(QBrush(fill_color))
        item.setPen(QPen(border_color, 2))
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

    def draw(self, scene, cx, cy, scale, color=None):
        # Represent 3D sphere as a circle with shading
        diameter_px = 2 * self._radius * scale

        fill_color = color if color else QColor("#64B5F6")
        border_color = fill_color.darker(150)
        highlight_color = fill_color.lighter(150)

        # Draw main circle
        x = cx - diameter_px/2
        y = cy - diameter_px/2
        ellipse = scene.addEllipse(x, y, diameter_px, diameter_px)
        ellipse.setBrush(QBrush(fill_color))
        ellipse.setPen(QPen(border_color, 2))
        ellipse.setZValue(1)

        # Draw highlight to give 3D effect
        highlight_diameter = diameter_px * 0.6
        highlight_x = x + diameter_px * 0.2
        highlight_y = y + diameter_px * 0.2
        highlight = scene.addEllipse(highlight_x, highlight_y,
                                     highlight_diameter, highlight_diameter)
        highlight.setBrush(QBrush(highlight_color))
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

    def draw(self, scene, cx, cy, scale, color=None):
        side_px = self._side * scale

        fill_color = color if color else QColor("#E57373")
        border_color = fill_color.darker(150)
        side_color = fill_color.darker(120)
        top_color = fill_color.lighter(120)

        x = cx - side_px/2
        y = cy - side_px/2

        # Draw front face
        front = scene.addRect(x, y, side_px, side_px)
        front.setBrush(QBrush(fill_color))
        front.setPen(QPen(border_color, 2))
        front.setZValue(1)

        # Draw top face (perspective)
        top_points = [
            QPointF(x, y),
            QPointF(x + side_px, y),
            QPointF(x + side_px * 0.8, y - side_px * 0.2),
            QPointF(x - side_px * 0.2, y - side_px * 0.2)
        ]
        top = scene.addPolygon(QPolygonF(top_points))
        top.setBrush(QBrush(top_color))
        top.setPen(QPen(border_color, 2))
        top.setZValue(0)

        # Draw side face (perspective)
        side_points = [
            QPointF(x + side_px, y),
            QPointF(x + side_px, y + side_px),
            QPointF(x + side_px * 0.8, y + side_px * 0.8),
            QPointF(x + side_px * 0.8, y - side_px * 0.2)
        ]
        side = scene.addPolygon(QPolygonF(side_points))
        side.setBrush(QBrush(side_color))
        side.setPen(QPen(border_color, 2))
        side.setZValue(0)


class Cylinder(Shape3D):
    def __init__(self, radius, height):
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and height must be positive")
        self._radius = radius
        self._height = height

    def area(self):
        return 2 * math.pi * self._radius * (self._radius + self._height)

    def volume(self):
        return math.pi * self._radius ** 2 * self._height

    def natural_size(self):
        return (2 * self._radius, self._height, 2 * self._radius)

    def draw(self, scene, cx, cy, scale, color=None):
        radius_px = self._radius * scale
        height_px = self._height * scale

        fill_color = color if color else QColor("#AED581")
        border_color = fill_color.darker(150)
        top_color = fill_color.lighter(120)

        # Draw main body (rectangle)
        x = cx - radius_px
        y = cy - height_px/2
        body = scene.addRect(x, y, 2 * radius_px, height_px)
        body.setBrush(QBrush(fill_color))
        body.setPen(QPen(border_color, 2))
        body.setZValue(1)

        # Draw top ellipse
        top_ellipse = scene.addEllipse(x, y - radius_px/2, 2 * radius_px, radius_px)
        top_ellipse.setBrush(QBrush(top_color))
        top_ellipse.setPen(QPen(border_color, 2))
        top_ellipse.setZValue(2)

        # Draw bottom ellipse
        bottom_ellipse = scene.addEllipse(x, y + height_px - radius_px/2, 2 * radius_px, radius_px)
        bottom_ellipse.setBrush(QBrush(fill_color.darker(120)))
        bottom_ellipse.setPen(QPen(border_color, 2))
        bottom_ellipse.setZValue(0)


class Cone(Shape3D):
    def __init__(self, radius, height):
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and height must be positive")
        self._radius = radius
        self._height = height

    def area(self):
        slant_height = math.sqrt(self._radius**2 + self._height**2)
        return math.pi * self._radius * (self._radius + slant_height)

    def volume(self):
        return (math.pi * self._radius ** 2 * self._height) / 3

    def natural_size(self):
        return (2 * self._radius, self._height, 2 * self._radius)

    def draw(self, scene, cx, cy, scale, color=None):
        radius_px = self._radius * scale
        height_px = self._height * scale

        fill_color = color if color else QColor("#FFB74D")
        border_color = fill_color.darker(150)

        # Draw base ellipse
        x = cx - radius_px
        y = cy + height_px/2 - radius_px/2
        base = scene.addEllipse(x, y, 2 * radius_px, radius_px)
        base.setBrush(QBrush(fill_color.darker(120)))
        base.setPen(QPen(border_color, 2))
        base.setZValue(0)

        # Draw cone body (triangle)
        points = [
            QPointF(cx, cy - height_px/2),  # Apex
            QPointF(cx - radius_px, cy + height_px/2),  # Base left
            QPointF(cx + radius_px, cy + height_px/2)   # Base right
        ]
        cone = scene.addPolygon(QPolygonF(points))
        cone.setBrush(QBrush(fill_color))
        cone.setPen(QPen(border_color, 2))
        cone.setZValue(1)


class Pyramid(Shape3D):
    def __init__(self, base, height):
        if base <= 0 or height <= 0:
            raise ValueError("Base and height must be positive")
        self._base = base
        self._height = height

    def area(self):
        slant_height = math.sqrt((self._base/2)**2 + self._height**2)
        return self._base**2 + 2 * self._base * slant_height

    def volume(self):
        return (self._base ** 2 * self._height) / 3

    def natural_size(self):
        return (self._base, self._height, self._base)

    def draw(self, scene, cx, cy, scale, color=None):
        base_px = self._base * scale
        height_px = self._height * scale

        fill_color = color if color else QColor("#9575CD")
        border_color = fill_color.darker(150)
        side_color = fill_color.darker(120)

        # Draw base (square)
        x = cx - base_px/2
        y = cy + height_px/2 - base_px/2
        base = scene.addRect(x, y, base_px, base_px)
        base.setBrush(QBrush(fill_color.darker(120)))
        base.setPen(QPen(border_color, 2))
        base.setZValue(0)

        # Draw front face (triangle)
        front_points = [
            QPointF(cx, cy - height_px/2),  # Apex
            QPointF(cx - base_px/2, cy + height_px/2),  # Base left
            QPointF(cx + base_px/2, cy + height_px/2)   # Base right
        ]
        front = scene.addPolygon(QPolygonF(front_points))
        front.setBrush(QBrush(fill_color))
        front.setPen(QPen(border_color, 2))
        front.setZValue(1)

        # Draw side face (triangle with perspective)
        side_points = [
            QPointF(cx, cy - height_px/2),  # Apex
            QPointF(cx + base_px/2, cy + height_px/2),  # Base front right
            QPointF(cx + base_px/2, cy + height_px/2 - base_px/2)  # Base back right
        ]
        side = scene.addPolygon(QPolygonF(side_points))
        side.setBrush(QBrush(side_color))
        side.setPen(QPen(border_color, 2))
        side.setZValue(0.5)


# ----------------- Astronomical Object -----------------
class AstronomicalObject:
    """Represents astronomical objects for alignment demonstration."""

    def __init__(self, radius, color="#888888", name="Planet", has_rings=False):
        if radius <= 0:
            raise ValueError("Astronomical radius must be positive")
        self._radius = radius
        self._color = color
        self._name = name
        self._has_rings = has_rings

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

        # Draw rings if applicable
        if self._has_rings:
            ring_width = diameter_px * 0.2
            ring_height = diameter_px * 0.05
            ring_x = cx - (diameter_px + ring_width)/2
            ring_y = cy - ring_height/2
            ring = scene.addEllipse(ring_x, ring_y, diameter_px + ring_width, ring_height)
            ring.setBrush(QBrush(QColor(210, 180, 140, 180)))  # Tan color with transparency
            ring.setPen(QPen(QColor(139, 69, 19), 1))  # Brown border
            ring.setZValue(0.5)
            ring.setRotation(30)  # Tilt the rings

        # Add a label (white for dark backgrounds; keep readable)
        text = scene.addText(self._name)
        # Choose label color based on object brightness
        try:
            col = QColor(self._color)
            brightness = (col.red() * 0.299 + col.green() * 0.587 + col.blue() * 0.114) / 255
            text_color = QColor("black") if brightness > 0.6 else QColor("white")
        except Exception:
            text_color = QColor("white")
        text.setDefaultTextColor(text_color)
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
        elif alignment == AlignmentType.RANDOM:
            # Random position within the scene
            min_x = shape_w_px/2 + margin
            max_x = scene_w - shape_w_px/2 - margin
            min_y = shape_h_px/2 + margin
            max_y = scene_h - shape_h_px/2 - margin

            import random
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
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
        elif shape_type == ShapeType.HEXAGON:
            return Hexagon(params[0])
        elif shape_type == ShapeType.OCTAGON:
            return Octagon(params[0])
        elif shape_type == ShapeType.STAR:
            return Star(params[0], params[1])
        elif shape_type == ShapeType.SPHERE:
            return Sphere(params[0])
        elif shape_type == ShapeType.CUBE:
            return Cube(params[0])
        elif shape_type == ShapeType.CYLINDER:
            return Cylinder(params[0], params[1])
        elif shape_type == ShapeType.CONE:
            return Cone(params[0], params[1])
        elif shape_type == ShapeType.PYRAMID:
            return Pyramid(params[0], params[1])
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")


# ----------------- Theme Manager -----------------
class ThemeManager:
    """Manages application themes."""

    THEMES = {
        ThemeType.LIGHT: {
            "background": "#ffffff",
            "text": "#000000",
            "panel": "#f8f8f8",
            "border": "#cccccc",
            "button": "#4a86e8",
            "button_hover": "#3a76d8",
            "button_pressed": "#2a66c8",
            "accent": "#6a11cb",
            "grid": "#e0e0e0",
            "combo_background": "#ffffff",
            "combo_text": "#000000",
            "spinbox_background": "#ffffff",
            "spinbox_text": "#000000",
            "viz_background": "#f0f0f0"  # Added - light gray for visualization
        },
        ThemeType.DARK: {
            "background": "#2d2d2d",
            "text": "#ffffff",
            "panel": "#3d3d3d",
            "border": "#555555",
            "button": "#5a96f8",
            "button_hover": "#4a86e8",
            "button_pressed": "#3a76d8",
            "accent": "#8a31eb",
            "grid": "#444444",
            "combo_background": "#ffffff",
            "combo_text": "#000000",
            "spinbox_background": "#ffffff",
            "spinbox_text": "#000000",
            "viz_background": "#1a1a1a"  # Added - very dark gray
        },
        ThemeType.BLUE: {
            "background": "#e8f4f8",
            "text": "#003366",
            "panel": "#d0e8f0",
            "border": "#a0c0d0",
            "button": "#3a76d8",
            "button_hover": "#2a66c8",
            "button_pressed": "#1a56b8",
            "accent": "#0066cc",
            "grid": "#c0d8e0",
            "combo_background": "#ffffff",
            "combo_text": "#000000",
            "spinbox_background": "#ffffff",
            "spinbox_text": "#000000",
            "viz_background": "#d8e8f0"  # Added - light blue
        },
        ThemeType.GREEN: {
            "background": "#f0f8f0",
            "text": "#004400",
            "panel": "#e0f0e0",
            "border": "#a0c0a0",
            "button": "#4caf50",
            "button_hover": "#3d9f40",
            "button_pressed": "#2e8f30",
            "accent": "#008800",
            "grid": "#d0e8d0",
            "combo_background": "#ffffff",
            "combo_text": "#000000",
            "spinbox_background": "#ffffff",
            "spinbox_text": "#000000",
            "viz_background": "#e0f0e0"  # Added - light green
        },
        ThemeType.COSMIC: {
            "background": "#0a0a2a",
            "text": "#ffffff",
            "panel": "#1a1a3a",
            "border": "#444466",
            "button": "#6a11cb",
            "button_hover": "#5a01bb",
            "button_pressed": "#4a01ab",
            "accent": "#2575fc",
            "grid": "#2a2a4a",
            "combo_background": "#ffffff",
            "combo_text": "#000000",
            "spinbox_background": "#ffffff",
            "spinbox_text": "#000000",
            "viz_background": "#0f0f2a"  # Added - cosmic dark blue
        }
    }

    @staticmethod
    def get_theme(theme_type):
        return ThemeManager.THEMES.get(theme_type, ThemeManager.THEMES[ThemeType.LIGHT])

    @staticmethod
    def get_theme(theme_type):
        return ThemeManager.THEMES.get(theme_type, ThemeManager.THEMES[ThemeType.LIGHT])


# ----------------- GUI Application -----------------
class GeometryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌌 Geometric Universe Explorer")
        self.setGeometry(100, 100, 1400, 900)  # Larger window for better layout

        # Initialize attributes
        self.current_shape = None
        self.astro_object = None
        self.history = []  # Store calculation history
        self.current_theme = ThemeType.COSMIC
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_angle = 0.0
        self.animation_speed = 1.0
        self.current_shape_tab = 0  # Track which shape tab is active (0=2D, 1=3D)

        # Visualization state
        self.grid_visible = True
        self.view_scale = 1.0

        # Initialize UI
        self.setup_ui()
        self.apply_theme(self.current_theme)

    def show_about(self):
        """Show a brief About dialog explaining the app's purpose."""
        about_text = (
            "<h3>Geometric Universe Explorer</h3>"
            "<p>This educational sandbox lets you create geometric shapes, "
            "compute area/perimeter/volume, and visualize the shape relative to "
            "a central celestial object with optional orbit animation.</p>"
            "<ul>"
            "<li>Enter numeric parameters for a shape (units are selectable in Settings).</li>"
            "<li>Choose a celestial body and alignment mode (Center, Overlap, Orbit, etc.).</li>"
            "<li>Use animation to simulate a simple orbit, and save snapshots or results.</li>"
            "</ul>"
            "<p>Tip: enable logarithmic scale when you compare objects with very different sizes.</p>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("About Geometric Universe Explorer")
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_about(self):
        """Show a brief About dialog explaining the app's purpose (helpful for first-run)."""
        about_text = (
            "<h3>Geometric Universe Explorer</h3>"
            "<p>This educational sandbox lets you create geometric shapes, "
            "compute area/perimeter/volume, and visualize the shape relative to "
            "a central celestial object with optional orbit animation.</p>"
            "<ul>"
            "<li>Enter numeric parameters for a shape (units are selectable in Settings).</li>"
            "<li>Choose a celestial body and alignment mode (Center, Overlap, Orbit, etc.).</li>"
            "<li>Use animation to simulate a simple orbit, and save snapshots or results.</li>"
            "</ul>"
            "<p>Tip: enable logarithmic scale when you compare objects with very different sizes.</p>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("About Geometric Universe Explorer")
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(480)
        left_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # Title
        title = QLabel("🌌 Geometric Universe Explorer")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setMinimumHeight(60)
        title.setAccessibleName("App Title")
        left_layout.addWidget(title)

        # Create tabs for better organization
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # Shape tab with sub-tabs for 2D and 3D
        shape_tab = QWidget()
        shape_layout = QVBoxLayout(shape_tab)
        shape_layout.setSpacing(10)

        # Create sub-tabs for 2D and 3D shapes
        self.shape_sub_tabs = QTabWidget()
        self.shape_sub_tabs.setDocumentMode(True)

        # 2D Shapes Tab
        shapes_2d_tab = QWidget()
        shapes_2d_layout = QVBoxLayout(shapes_2d_tab)
        shapes_2d_layout.setSpacing(10)

        shape_2d_group = QGroupBox("🟦 2D Shapes")
        shape_2d_layout_group = QVBoxLayout()
        shape_2d_layout_group.setSpacing(8)

        shape_2d_type_row = QHBoxLayout()
        shape_2d_type_row.addWidget(QLabel("2D Shape Type:"))
        self.shape_2d_menu = QComboBox()
        # Add only 2D shapes
        self.shape_2d_menu.addItems([
            ShapeType.CIRCLE.value, ShapeType.RECTANGLE.value, ShapeType.TRIANGLE.value,
            ShapeType.SQUARE.value, ShapeType.ELLIPSE.value, ShapeType.PARALLELOGRAM.value,
            ShapeType.RHOMBUS.value, ShapeType.PENTAGON.value, ShapeType.HEXAGON.value,
            ShapeType.OCTAGON.value, ShapeType.STAR.value
        ])
        self.shape_2d_menu.currentIndexChanged.connect(self.update_input_fields)
        shape_2d_menu_tip = "Choose which 2D shape to create. Parameters will update below."
        self.shape_2d_menu.setToolTip(shape_2d_menu_tip)
        shape_2d_type_row.addWidget(self.shape_2d_menu)
        shape_2d_layout_group.addLayout(shape_2d_type_row)

        shape_2d_group.setLayout(shape_2d_layout_group)
        shapes_2d_layout.addWidget(shape_2d_group)
        self.shape_sub_tabs.addTab(shapes_2d_tab, "🟦 2D Shapes")

        # 3D Shapes Tab
        shapes_3d_tab = QWidget()
        shapes_3d_layout = QVBoxLayout(shapes_3d_tab)
        shapes_3d_layout.setSpacing(10)

        shape_3d_group = QGroupBox("🧊 3D Shapes")
        shape_3d_layout_group = QVBoxLayout()
        shape_3d_layout_group.setSpacing(8)

        shape_3d_type_row = QHBoxLayout()
        shape_3d_type_row.addWidget(QLabel("3D Shape Type:"))
        self.shape_3d_menu = QComboBox()
        # Add only 3D shapes
        self.shape_3d_menu.addItems([
            ShapeType.SPHERE.value, ShapeType.CUBE.value, ShapeType.CYLINDER.value,
            ShapeType.CONE.value, ShapeType.PYRAMID.value
        ])
        self.shape_3d_menu.currentIndexChanged.connect(self.update_input_fields)
        self.shape_3d_menu.setToolTip("Choose a 3D shape for volume/surface calculations.")
        shape_3d_type_row.addWidget(self.shape_3d_menu)
        shape_3d_layout_group.addLayout(shape_3d_type_row)

        shape_3d_group.setLayout(shape_3d_layout_group)
        shapes_3d_layout.addWidget(shape_3d_group)
        self.shape_sub_tabs.addTab(shapes_3d_tab, "🧊 3D Shapes")

        # Connect tab change to update shape menu
        self.shape_sub_tabs.currentChanged.connect(self.on_shape_tab_changed)

        shape_layout.addWidget(self.shape_sub_tabs)

        # Input fields for shape parameters
        self.inputs_group = QGroupBox("📐 Shape Parameters")
        self.inputs_layout = QVBoxLayout()
        self.inputs_layout.setSpacing(5)
        self.setup_input_fields()
        self.inputs_group.setLayout(self.inputs_layout)
        shape_layout.addWidget(self.inputs_group)

        # Color selection
        color_group = QGroupBox("🎨 Shape Appearance")
        color_layout = QVBoxLayout()
        color_layout.setSpacing(8)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Shape Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Default", "Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Custom..."])
        self.color_combo.setToolTip("Pick a color for the shape. 'Custom...' opens a color picker.")
        color_row.addWidget(self.color_combo)
        color_layout.addLayout(color_row)

        # Opacity slider for shape
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(20)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setToolTip("Adjust shape opacity for better visualization when overlapping.")
        opacity_row.addWidget(self.opacity_slider)
        color_layout.addLayout(opacity_row)

        color_group.setLayout(color_layout)
        shape_layout.addWidget(color_group)

        tabs.addTab(shape_tab, "🔷 Shapes")

        # Astronomy tab
        astro_tab = QWidget()
        astro_layout = QVBoxLayout(astro_tab)
        astro_layout.setSpacing(10)

        astro_group = QGroupBox("🌠 Astronomy Settings")
        astro_group_layout = QVBoxLayout()
        astro_group_layout.setSpacing(8)

        astro_type_row = QHBoxLayout()
        astro_type_row.addWidget(QLabel("Celestial Body:"))
        self.astro_menu = QComboBox()
        self.astro_menu.addItems(["None", "Planet", "Star", "Moon", "Gas Giant", "Black Hole"])
        self.astro_menu.currentIndexChanged.connect(self.update_astro_fields)
        astro_type_row.addWidget(self.astro_menu)
        astro_group_layout.addLayout(astro_type_row)

        astro_params_row = QHBoxLayout()
        astro_params_row.addWidget(QLabel("Radius:"))
        self.astro_radius_entry = QLineEdit()
        self.astro_radius_entry.setPlaceholderText("50-200")
        astro_params_row.addWidget(self.astro_radius_entry)
        astro_group_layout.addLayout(astro_params_row)

        rings_row = QHBoxLayout()
        rings_row.addWidget(QLabel("Has Rings:"))
        self.rings_checkbox = QCheckBox()
        rings_row.addWidget(self.rings_checkbox)
        rings_row.addStretch()
        astro_group_layout.addLayout(rings_row)

        alignment_row = QHBoxLayout()
        alignment_row.addWidget(QLabel("Alignment:"))
        self.align_menu = QComboBox()
        self.align_menu.addItems([align.value for align in AlignmentType])
        alignment_row.addWidget(self.align_menu)
        astro_group_layout.addLayout(alignment_row)

        astro_group.setLayout(astro_group_layout)
        astro_layout.addWidget(astro_group)

        # Animation settings
        anim_group = QGroupBox("🌀 Animation")
        anim_layout = QVBoxLayout()
        anim_layout.setSpacing(8)

        anim_enable_row = QHBoxLayout()
        anim_enable_row.addWidget(QLabel("Enable Animation:"))
        self.anim_checkbox = QCheckBox()
        self.anim_checkbox.stateChanged.connect(self.toggle_animation)
        anim_enable_row.addWidget(self.anim_checkbox)
        anim_enable_row.addStretch()
        anim_layout.addLayout(anim_enable_row)

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.update_animation_speed)
        speed_row.addWidget(self.speed_slider)
        anim_layout.addLayout(speed_row)
        self.speed_label = QLabel("Medium") 
        speed_row.addWidget(self.speed_label)  
        anim_group.setLayout(anim_layout)
        astro_layout.addWidget(anim_group)

        tabs.addTab(astro_tab, "🌌 Astronomy")

        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setSpacing(10)

        theme_group = QGroupBox("🎨 Theme Settings")
        theme_layout = QVBoxLayout()
        theme_layout.setSpacing(8)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([theme.value for theme in ThemeType])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_row.addWidget(self.theme_combo)
        theme_layout.addLayout(theme_row)

        # Replace existing scale_row block with this
        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Scale Factor:"))
        self.scale_spinbox = QDoubleSpinBox()
        self.scale_spinbox.setMinimum(0.001)
        self.scale_spinbox.setMaximum(100.0)
        self.scale_spinbox.setValue(1.0)
        self.scale_spinbox.setSingleStep(0.01)
        scale_row.addWidget(self.scale_spinbox)

        # Units selector
        scale_row.addSpacing(6)
        scale_row.addWidget(QLabel("Units:"))
        self.units_combo = QComboBox()
        self.units_combo.addItems(["units (arb)", "px", "m", "km", "AU"])
        self.units_combo.setToolTip("Choose the interpretation of numeric inputs (affects labels in results).")
        scale_row.addWidget(self.units_combo)

        theme_layout.addLayout(scale_row)

        # Add logarithmic scale option
        log_scale_row = QHBoxLayout()
        log_scale_row.addWidget(QLabel("Use Logarithmic Scale:"))
        self.log_scale_checkbox = QCheckBox()
        self.log_scale_checkbox.setToolTip("Use logarithmic scaling for better visualization of very large values")
        log_scale_row.addWidget(self.log_scale_checkbox)
        log_scale_row.addStretch()
        theme_layout.addLayout(log_scale_row)

        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)

        # History section
        history_group = QGroupBox("📜 History")
        history_layout = QVBoxLayout()
        self.history_list = QComboBox()
        self.history_list.currentIndexChanged.connect(self.load_from_history)
        history_layout.addWidget(self.history_list)

        history_btn_row = QHBoxLayout()
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        history_btn_row.addWidget(self.clear_history_btn)

        self.save_history_btn = QPushButton("Save to File")
        self.save_history_btn.clicked.connect(self.save_history_to_file)
        history_btn_row.addWidget(self.save_history_btn)
        history_layout.addLayout(history_btn_row)

        history_group.setLayout(history_layout)
        settings_layout.addWidget(history_group)

        tabs.addTab(settings_tab, "⚙️ Settings")

        left_layout.addWidget(tabs)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.calc_btn = QPushButton("🖌️ Draw & Calculate")
        self.calc_btn.clicked.connect(self.calculate)
        self.calc_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        self.calc_btn.setToolTip("Draw the selected shape and calculate properties (Ctrl+D)")
        button_row.addWidget(self.calc_btn)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setObjectName("special")
        self.clear_btn.setToolTip("Clear inputs and visualization (Ctrl+C)")
        button_row.addWidget(self.clear_btn)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setObjectName("save")
        self.save_btn.setToolTip("Save results and history to a text file (Ctrl+S)")
        button_row.addWidget(self.save_btn)

        left_layout.addLayout(button_row)

        # Results display
        results_group = QGroupBox("📊 Results")
        results_layout = QVBoxLayout()
        self.result_label = QLabel("⏳ Results will be shown here.")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(120)
        results_layout.addWidget(self.result_label)
        results_group.setLayout(results_layout)
        left_layout.addWidget(results_group)

        # Status bar
        self.status_label = QLabel("🚀 Ready to explore the geometric universe!")
        self.status_label.setMinimumHeight(30)
        self.status_label.setAccessibleName("Status")
        left_layout.addWidget(self.status_label)

        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)

        # Right panel for visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)

        # Toolbar (zoom, reset, snapshot, grid toggle)
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(18, 18))

        zoom_in_action = QAction(QIcon(), "Zoom In", self)
        zoom_in_action.triggered.connect(lambda: self.zoom_view(1.2))
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_action.setToolTip("Zoom in the canvas (Ctrl++)")
        self.toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction(QIcon(), "Zoom Out", self)
        zoom_out_action.triggered.connect(lambda: self.zoom_view(1/1.2))
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.setToolTip("Zoom out the canvas (Ctrl+-)")
        self.toolbar.addAction(zoom_out_action)

        reset_view_action = QAction(QIcon(), "Reset View", self)
        reset_view_action.triggered.connect(self.reset_view)
        reset_view_action.setToolTip("Reset view and zoom")
        self.toolbar.addAction(reset_view_action)

        snapshot_action = QAction(QIcon(), "Snapshot", self)
        snapshot_action.triggered.connect(self.snapshot_canvas)
        snapshot_action.setToolTip("Save a snapshot of the canvas to an image file")
        self.toolbar.addAction(snapshot_action)

        # Grid toggle
        self.grid_toggle_action = QAction("Grid", self, checkable=True)
        self.grid_toggle_action.setChecked(self.grid_visible)
        self.grid_toggle_action.triggered.connect(self.toggle_grid)
        self.grid_toggle_action.setToolTip("Toggle background grid")
        self.toolbar.addAction(self.grid_toggle_action)

        right_layout.addWidget(self.toolbar)

        # Visualization title
        viz_title = QLabel("🔭 Visualization Canvas")
        viz_title.setObjectName("viz_title")
        viz_title.setAlignment(Qt.AlignCenter)
        viz_title.setMinimumHeight(30)
        right_layout.addWidget(viz_title)

        # Graphics area
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(800, 600)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        right_layout.addWidget(self.view)

        # Zoom/lens info
        zoom_info_row = QHBoxLayout()
        self.zoom_label = QLabel("Zoom: 100%")
        zoom_info_row.addWidget(self.zoom_label)
        zoom_info_row.addStretch()
        right_layout.addLayout(zoom_info_row)

        # Info panel below visualization
        info_group = QGroupBox("ℹ️ Visualization Info")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("• Select a shape and astronomical object\n• Choose an alignment type\n• Click 'Draw & Calculate' to visualize")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)

        self.setLayout(main_layout)

        # Accessibility names & shortcuts
        self.calc_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.calc_shortcut.activated.connect(self.calculate)
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.clear_shortcut.activated.connect(self.clear_all)
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_results)

        # Initialize UI state
        self.update_input_fields()
        self.update_astro_fields()

        # Initialize scene rect
        self.scene.setSceneRect(0, 0, 800, 600)

    def on_shape_tab_changed(self, index):
        """Handle shape tab change between 2D and 3D."""
        self.current_shape_tab = index
        self.update_input_fields()

    def get_current_shape_menu(self):
        """Get the current shape menu based on selected tab."""
        if self.current_shape_tab == 0:  # 2D tab
            return self.shape_2d_menu
        else:  # 3D tab
            return self.shape_3d_menu

    def get_current_shape_type(self):
        """Get the current shape type from the appropriate menu."""
        current_menu = self.get_current_shape_menu()
        return ShapeType(current_menu.currentText())

    def apply_theme(self, theme_type):
        """Apply the selected theme to the application."""
        theme = ThemeManager.get_theme(theme_type)
        self.current_theme = theme_type

        style = f"""
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                color: {theme['text']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme['border']};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {theme['panel']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme['text']};
            }}

            /* Buttons */
            QPushButton {{
                background-color: {theme['button']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
            QPushButton#special {{
                background-color: #e67c73;
            }}
            QPushButton#special:hover {{
                background-color: #d66c63;
            }}
            QPushButton#save {{
                background-color: #0f9d58;
            }}
            QPushButton#save:hover {{
                background-color: #0e8d48;
            }}

            /* Inputs: use theme values instead of hard-coded white/black */
            QLineEdit, QPlainTextEdit, QTextEdit {{
                padding: 6px;
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['spinbox_background']};
                color: {theme['spinbox_text']};
            }}
            QComboBox {{
                padding: 6px;
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['combo_background']};
                color: {theme['combo_text']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['combo_background']};
                color: {theme['combo_text']};
                selection-background-color: {theme['button']};
                selection-color: white;
            }}
            QDoubleSpinBox {{
                padding: 6px;
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['spinbox_background']};
                color: {theme['spinbox_text']};
            }}

            /* Titles */
            QLabel#title {{
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['accent']}, stop: 1 {theme['button']});
                border-radius: 8px;
                color: white;
            }}
            QLabel#viz_title {{
                font-weight: bold; 
                font-size: 16px; 
                padding: 5px;
                color: {theme['text']};
                background-color: {theme['panel']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
            }}

            /* Graphics view / text areas */
            QTextEdit, QGraphicsView {{
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['background']};
            }}

            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                background: {theme['panel']};
            }}
            QTabBar::tab {{
                background: {theme['panel']};
                border: 1px solid {theme['border']};
                padding: 8px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: {theme['text']};
            }}
            QTabBar::tab:selected {{
                background: {theme['background']};
                border-bottom-color: {theme['background']};
                color: {theme['text']};
            }}

            /* Sliders and checkboxes */
            QSlider::groove:horizontal {{
                border: 1px solid {theme['border']};
                height: 8px;
                background: {theme['panel']};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {theme['button']};
                border: 1px solid {theme['border']};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {theme['accent']};
                border-radius: 4px;
            }}
            QCheckBox {{
                spacing: 5px;
                color: {theme['text']};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme['border']};
                border-radius: 3px;
                background: {theme['spinbox_background']};
            }}
            QCheckBox::indicator:checked {{
                background: {theme['button']};
                border: 1px solid {theme['button']};
            }}

            /* ToolBar & ToolButtons: explicit styling fixes the disappearing labels */
            QToolBar {{
                background: {theme['panel']};
                border: 1px solid {theme['border']};
                spacing: 4px;
                padding: 2px;
            }}
            QToolButton {{
                color: {theme['text']};
                background: transparent;
                border: none;
                padding: 6px 8px;
                margin: 0 2px;
            }}
            QToolButton:hover {{
                background: rgba(255,255,255,0.03);
                border-radius: 4px;
            }}
            QToolButton:pressed {{
                background: rgba(255,255,255,0.06);
                border-radius: 4px;
            }}
            QToolButton:disabled {{
                color: {theme['border']};
            }}

            /* Ensure message boxes are readable in all themes */
            QMessageBox {{
                background-color: white;
                color: black;
            }}
            QMessageBox QLabel {{
                color: black;
            }}
            QMessageBox QPushButton {{
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #3a76d8;
            }}
           
            QGraphicsView {{
                border: 3px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['viz_background']};  
            }}
        """

        self.setStyleSheet(style)
        self.update()

    def change_theme(self, theme_name):
        """Change the application theme."""
        try:
            theme_type = ThemeType(theme_name)
            self.apply_theme(theme_type)
        except ValueError:
            pass

    def setup_input_fields(self):
        """Setup the input fields based on current shape selection."""
        # Clear existing fields
        for i in reversed(range(self.inputs_layout.count())):
            item = self.inputs_layout.itemAt(i)
            if item.layout():
                # Clear layout and its widgets
                child_layout = item.layout()
                for j in reversed(range(child_layout.count())):
                    w_item = child_layout.itemAt(j)
                    if w_item.widget():
                        w_item.widget().deleteLater()
                self.inputs_layout.removeItem(item)
            elif item.widget():
                # Remove widget directly
                item.widget().deleteLater()

        shape_type = self.get_current_shape_type()

        # Add appropriate input fields based on shape type
        if shape_type in [ShapeType.CIRCLE, ShapeType.SPHERE]:
            # One parameter needed - radius
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel("Radius:"))
            entry = QLineEdit()
            entry.setPlaceholderText("Enter radius (0-1,000,000)")
            entry.setToolTip("Positive numeric value required.")
            field_layout.addWidget(entry)
            self.inputs_layout.addLayout(field_layout)

        elif shape_type in [ShapeType.SQUARE, ShapeType.CUBE, ShapeType.PENTAGON,
                           ShapeType.HEXAGON, ShapeType.OCTAGON]:
            # One parameter needed - side
            param_name = "Side"
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(f"{param_name}:"))
            entry = QLineEdit()
            entry.setPlaceholderText(f"Enter {param_name.lower()} (0-1,000,000)")
            entry.setToolTip("Positive numeric value required.")
            field_layout.addWidget(entry)
            self.inputs_layout.addLayout(field_layout)

        elif shape_type == ShapeType.STAR:
            # Two parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Outer Radius:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter outer radius (0-1,000,000)")
            entry1.setToolTip("Outer radius (positive number)")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)

            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Inner Radius:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter inner radius (0-1,000,000)")
            entry2.setToolTip("Inner radius (positive number)")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)

        elif shape_type in [ShapeType.RECTANGLE, ShapeType.TRIANGLE, ShapeType.ELLIPSE,
                           ShapeType.RHOMBUS, ShapeType.CYLINDER, ShapeType.CONE,
                           ShapeType.PYRAMID]:
            # Two parameters needed
            if shape_type == ShapeType.RECTANGLE:
                param1, param2 = "Width", "Height"
            elif shape_type == ShapeType.TRIANGLE:
                param1, param2 = "Base", "Height"
            elif shape_type == ShapeType.ELLIPSE:
                param1, param2 = "Major axis", "Minor axis"
            elif shape_type == ShapeType.RHOMBUS:
                param1, param2 = "Diagonal 1", "Diagonal 2"
            elif shape_type == ShapeType.CYLINDER:
                param1, param2 = "Radius", "Height"
            elif shape_type == ShapeType.CONE:
                param1, param2 = "Radius", "Height"
            elif shape_type == ShapeType.PYRAMID:
                param1, param2 = "Base", "Height"

            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel(f"{param1}:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText(f"Enter {param1.lower()} (0-1,000,000)")
            entry1.setToolTip(f"{param1} (positive number)")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)

            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel(f"{param2}:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText(f"Enter {param2.lower()} (0-1,000,000)")
            entry2.setToolTip(f"{param2} (positive number)")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)

        elif shape_type == ShapeType.PARALLELOGRAM:
            # Three parameters needed
            field_layout1 = QHBoxLayout()
            field_layout1.addWidget(QLabel("Base:"))
            entry1 = QLineEdit()
            entry1.setPlaceholderText("Enter base (0-1,000,000)")
            entry1.setToolTip("Base (positive number)")
            field_layout1.addWidget(entry1)
            self.inputs_layout.addLayout(field_layout1)

            field_layout2 = QHBoxLayout()
            field_layout2.addWidget(QLabel("Side:"))
            entry2 = QLineEdit()
            entry2.setPlaceholderText("Enter side (0-1,000,000)")
            entry2.setToolTip("Side (positive number)")
            field_layout2.addWidget(entry2)
            self.inputs_layout.addLayout(field_layout2)

            field_layout3 = QHBoxLayout()
            field_layout3.addWidget(QLabel("Height:"))
            entry3 = QLineEdit()
            entry3.setPlaceholderText("Enter height (0-1,000,000)")
            entry3.setToolTip("Height (positive number)")
            field_layout3.addWidget(entry3)
            self.inputs_layout.addLayout(field_layout3)

    def update_input_fields(self):
        """Update the input fields when shape selection changes."""
        self.setup_input_fields()

    def update_astro_fields(self):
        """Show/hide astronomical object fields based on selection."""
        show_astro = self.astro_menu.currentText() != "None"
        self.astro_radius_entry.setVisible(show_astro)
        self.rings_checkbox.setVisible(show_astro)
        self.align_menu.setVisible(show_astro)

        # Set default radius based on selection
        if show_astro:
            astro_type = self.astro_menu.currentText()
            if astro_type == "Planet":
                self.astro_radius_entry.setText("80")
            elif astro_type == "Star":
                self.astro_radius_entry.setText("120")
                self.rings_checkbox.setChecked(False)
            elif astro_type == "Moon":
                self.astro_radius_entry.setText("40")
            elif astro_type == "Gas Giant":
                self.astro_radius_entry.setText("100")
                self.rings_checkbox.setChecked(True)
            elif astro_type == "Black Hole":
                self.astro_radius_entry.setText("60")
                self.rings_checkbox.setChecked(False)

    def get_shape_parameters(self):
        """Get parameters from input fields based on current shape selection."""
        shape_type = self.get_current_shape_type()
        params = []

        # Collect all numeric values from input fields
        for i in range(self.inputs_layout.count()):
            layout = self.inputs_layout.itemAt(i)
            # The stored items are QHBoxLayout typically
            try:
                if isinstance(layout, QHBoxLayout) or layout is None:
                    # In some PyQt versions, itemAt returns a QLayoutItem; handle generically
                    # Extract widget at position 1 if present
                    row = self.inputs_layout.itemAt(i)
                    inner = row.layout() if row.layout() else None
                    target_layout = inner if inner else row
                    if target_layout:
                        # Look for QLineEdit child
                        for j in range(target_layout.count()):
                            w = target_layout.itemAt(j).widget()
                            if isinstance(w, QLineEdit) and w.text():
                                try:
                                    param_value = float(w.text())
                                    if param_value <= 0:
                                        raise ValueError("All values must be positive")
                                    if param_value > 1000000:
                                        # Show warning but allow the value
                                        reply = QMessageBox.question(self, "Very Large Value",
                                                                     f"Value {param_value:,.0f} is very large. This may cause visualization issues. Continue?",
                                                                     QMessageBox.Yes | QMessageBox.No)
                                        if reply == QMessageBox.No:
                                            return []
                                    params.append(param_value)
                                except ValueError:
                                    raise ValueError(f"Invalid number: {w.text()}")
                                break
            except Exception:
                # Fallback: ignore layout parsing errors
                continue

        # Validate parameter count
        required_params = 1
        if shape_type in [ShapeType.RECTANGLE, ShapeType.TRIANGLE, ShapeType.ELLIPSE,
                          ShapeType.RHOMBUS, ShapeType.STAR, ShapeType.CYLINDER,
                          ShapeType.CONE, ShapeType.PYRAMID]:
            required_params = 2
        elif shape_type == ShapeType.PARALLELOGRAM:
            required_params = 3

        if len(params) != required_params:
            raise ValueError(f"This shape requires {required_params} parameters")

        return params

    def get_shape_color(self):
        """Get the selected shape color."""
        color_name = self.color_combo.currentText()

        if color_name == "Default":
            return None
        elif color_name == "Red":
            return QColor("#F44336")
        elif color_name == "Green":
            return QColor("#4CAF50")
        elif color_name == "Blue":
            return QColor("#2196F3")
        elif color_name == "Yellow":
            return QColor("#FFEB3B")
        elif color_name == "Purple":
            return QColor("#9C27B0")
        elif color_name == "Orange":
            return QColor("#FF9800")
        elif color_name == "Custom...":
            # Open color dialog for custom color selection
            color = QColorDialog.getColor()
            return color if color.isValid() else None

        return None

    def get_astro_color(self):
        """Get color for astronomical object based on selection."""
        astro_type = self.astro_menu.currentText()

        if astro_type == "Planet":
            return "#4CAF50"  # Green
        elif astro_type == "Star":
            return "#FFC107"  # Amber
        elif astro_type == "Moon":
            return "#E0E0E0"  # Light gray
        elif astro_type == "Gas Giant":
            return "#FF9800"  # Orange
        elif astro_type == "Black Hole":
            return "#212121"  # Very dark gray
        else:
            return "#888888"  # Default gray

    def calculate(self):
        """Main calculation and drawing method."""
        try:
            # Get shape parameters and create shape
            shape_type = self.get_current_shape_type()
            params = self.get_shape_parameters()
            if params is None or not params:  # User cancelled due to large values or error
                return

            shape_color = self.get_shape_color()
            # If opacity adjusted, incorporate into color's alpha
            base_color = shape_color if shape_color else QColor("#4FC3F7")
            alpha = int(self.opacity_slider.value() * 2.55)  # map 0-100 to 0-255
            base_color.setAlpha(alpha)

            self.current_shape = ShapeFactory.create_shape(shape_type, params)

            # Create astronomical object if selected
            self.astro_object = None
            if self.astro_menu.currentText() != "None":
                if not self.astro_radius_entry.text():
                    raise ValueError("Please enter astronomical object radius")
                astro_radius = float(self.astro_radius_entry.text())
                if astro_radius <= 0:
                    raise ValueError("Astronomical radius must be positive")

                astro_color = self.get_astro_color()
                has_rings = self.rings_checkbox.isChecked()
                self.astro_object = AstronomicalObject(astro_radius, color=astro_color,
                                                      name=self.astro_menu.currentText(),
                                                      has_rings=has_rings)

            # Calculate scale and positions
            scene_rect = self.scene.sceneRect()
            if scene_rect.width() == 0 or scene_rect.height() == 0:
                scene_rect = QRectF(0, 0, self.view.width(), self.view.height())
                self.scene.setSceneRect(scene_rect)

            scale = self.calculate_scale(scene_rect) * self.scale_spinbox.value()
            alignment = AlignmentType(self.align_menu.currentText()) if self.astro_object else AlignmentType.CENTER

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

            # Add a subtle grid to the background (if enabled)
            if self.grid_visible:
                self.draw_grid(scene_rect)

            if self.astro_object:
                self.astro_object.draw(self.scene, astro_x, astro_y, scale)
            self.current_shape.draw(self.scene, shape_x, shape_y, scale, base_color)

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
            scale_info = f"{scale:.6f}" if scale < 0.001 else f"{scale:.4f}"
            self.info_label.setText(
                f"• Shape: {shape_type.value}\n"
                f"• Celestial Body: {self.astro_menu.currentText() if self.astro_object else 'None'}\n"
                f"• Alignment: {alignment_name}\n"
                f"• Scale: {scale_info} px/unit\n"
                f"• Logarithmic Scale: {'Yes' if self.log_scale_checkbox.isChecked() else 'No'}"
            )

            self.status_label.setText("✅ Calculation completed successfully!")

            # Update view zoom label
            self.zoom_label.setText(f"Zoom: {int(self.view_scale * 100)}%")

            # Start animation if enabled
            if self.anim_checkbox.isChecked():
                # Timer interval adjusted by speed for smoother control
                interval = max(16, int(200 / max(1, self.animation_speed * 2)))
                self.animation_timer.start(interval)

        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.show_error_message(str(e))

    def show_error_message(self, message):
        """Show an error message with proper styling that works in all themes."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)

        # Apply a style that ensures readability in all themes
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3a76d8;
            }
        """)

        msg_box.exec_()

    def draw_grid(self, scene_rect):
        """Draw a subtle grid in the background."""
        theme = ThemeManager.get_theme(self.current_theme)
        grid_color = QColor(theme['grid'])
        grid_color.setAlpha(100)  # Semi-transparent

        width = int(scene_rect.width())
        height = int(scene_rect.height())

        # Draw horizontal lines
        step = 50
        for y in range(0, height, step):
            self.scene.addLine(0, y, width, y, QPen(grid_color, 0.5))

        # Draw vertical lines
        for x in range(0, width, step):
            self.scene.addLine(x, 0, x, height, QPen(grid_color, 0.5))

        # Draw axes
        center_x = width / 2
        center_y = height / 2
        axis_color = QColor(150, 150, 150, 160)
        self.scene.addLine(0, center_y, width, center_y, QPen(axis_color, 1))
        self.scene.addLine(center_x, 0, center_x, height, QPen(axis_color, 1))

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

        # Auto-adjust scale for very large values
        calculated_scale = min(scale_x, scale_y)

        # Apply logarithmic scaling if enabled for very large values
        if self.log_scale_checkbox.isChecked() and calculated_scale < 0.01:
            # Use logarithmic scaling: log10(value) then normalize
            max_dimension = max(shape_w, shape_h)
            if max_dimension > 1000:
                log_scale = math.log10(max_dimension)
                calculated_scale = (scene_w * 0.8) / (log_scale * 100)

        # If the calculated scale is too small (large values), use a minimum scale
        if calculated_scale < 0.0001:
            return 0.0001
        elif calculated_scale > 10000:
            return 10000
        else:
            return calculated_scale

    def display_results(self):
        """Display calculation results."""
        if not self.current_shape:
            return

        result_text = f"<h3>{self.current_shape.__class__.__name__} Properties</h3>"

        # Format large numbers with commas for readability
        area = self.current_shape.area()
        perimeter = self.current_shape.perimeter()

        result_text += f"<b>Area:</b> {area:,.2f}<br>"
        result_text += f"<b>Perimeter:</b> {perimeter:,.2f}<br>"

        volume = self.current_shape.volume()
        if volume > 0:
            result_text += f"<b>Volume:</b> {volume:,.2f}<br>"

        # Add dimensions
        w, h, d = self.current_shape.natural_size()
        if d > 0:
            result_text += f"<b>Dimensions:</b> {w:,.1f} × {h:,.1f} × {d:,.1f}<br>"
        else:
            result_text += f"<b>Dimensions:</b> {w:,.1f} × {h:,.1f}<br>"

        if self.astro_object:
            # Check for overlap
            scene_rect = self.scene.sceneRect()
            scale = self.calculate_scale(scene_rect) * self.scale_spinbox.value()

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
        timestamp = datetime.now().strftime("%H:%M:%S")
        shape_name = self.current_shape.__class__.__name__
        astro_name = self.astro_menu.currentText() if self.astro_object else "None"

        history_entry = {
            'timestamp': timestamp,
            'shape': shape_name,
            'astro': astro_name,
            'result': self.result_label.text(),
            'shape_type': self.get_current_shape_type().value,
            'shape_params': self.get_shape_parameters(),
            'astro_radius': self.astro_radius_entry.text() if self.astro_object else "",
            'alignment': self.align_menu.currentText()
        }

        self.history.append(history_entry)
        # Keep only last 20 entries
        if len(self.history) > 20:
            self.history.pop(0)

        # Update history list
        self.history_list.clear()
        for i, entry in enumerate(reversed(self.history)):
            self.history_list.addItem(f"{entry['timestamp']} - {entry['shape']} with {entry['astro']}")

    def load_from_history(self, index):
        """Load a calculation from history."""
        if index < 0 or index >= len(self.history):
            return

        # Get the history entry (history is displayed in reverse order)
        entry = self.history[len(self.history) - 1 - index]

        # Set shape type in appropriate menu based on shape type
        shape_type = entry['shape_type']
        if shape_type in [shape.value for shape in [
            ShapeType.CIRCLE, ShapeType.RECTANGLE, ShapeType.TRIANGLE, ShapeType.SQUARE,
            ShapeType.ELLIPSE, ShapeType.PARALLELOGRAM, ShapeType.RHOMBUS, ShapeType.PENTAGON,
            ShapeType.HEXAGON, ShapeType.OCTAGON, ShapeType.STAR
        ]]:
            # It's a 2D shape, switch to 2D tab and select the shape
            self.shape_sub_tabs.setCurrentIndex(0)
            shape_index = self.shape_2d_menu.findText(shape_type)
            if shape_index >= 0:
                self.shape_2d_menu.setCurrentIndex(shape_index)
        else:
            # It's a 3D shape, switch to 3D tab and select the shape
            self.shape_sub_tabs.setCurrentIndex(1)
            shape_index = self.shape_3d_menu.findText(shape_type)
            if shape_index >= 0:
                self.shape_3d_menu.setCurrentIndex(shape_index)

        # Set shape parameters
        self.set_shape_parameters(entry['shape_params'])

        # Set astronomical object
        if entry['astro'] != "None":
            astro_index = self.astro_menu.findText(entry['astro'])
            if astro_index >= 0:
                self.astro_menu.setCurrentIndex(astro_index)
            self.astro_radius_entry.setText(entry['astro_radius'])
        else:
            self.astro_menu.setCurrentIndex(0)

        # Set alignment
        align_index = self.align_menu.findText(entry['alignment'])
        if align_index >= 0:
            self.align_menu.setCurrentIndex(align_index)

        # Update results
        self.result_label.setText(entry['result'])

    def set_shape_parameters(self, params):
        """Set the shape parameters in the input fields."""
        # Clear existing fields first
        self.setup_input_fields()

        # Set the parameter values
        param_index = 0
        for i in range(self.inputs_layout.count()):
            layout = self.inputs_layout.itemAt(i)
            if layout and isinstance(layout.layout(), QHBoxLayout):
                target_layout = layout.layout()
            else:
                target_layout = layout.layout() if hasattr(layout, 'layout') and layout.layout() else layout
            if target_layout and param_index < len(params):
                # Find first QLineEdit in target_layout
                for j in range(target_layout.count()):
                    widget = target_layout.itemAt(j).widget()
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(params[param_index]))
                        param_index += 1
                        break

    def clear_history(self):
        """Clear the calculation history."""
        self.history = []
        self.history_list.clear()
        self.status_label.setText("🗑️ History cleared")

    def save_history_to_file(self):
        """Save the calculation history to a file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save History", "", "JSON Files (*.json);;Text Files (*.txt)"
            )

            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.history, f, indent=2)

                self.status_label.setText(f"💾 History saved to {filename}")

        except Exception as e:
            self.show_error_message(f"Could not save history: {str(e)}")

    def save_results(self):
        """Save results to a text file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Results", "", "Text Files (*.txt)"
            )

            if not filename:
                return

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
                    f.write(f"{i}. {entry['timestamp']} - {entry['shape']} with {entry['astro']}\n")

            self.status_label.setText(f"💾 Results saved to {filename}")

        except Exception as e:
            self.show_error_message(f"Could not save results: {str(e)}")

    def clear_all(self):
        """Clear all inputs, results, and the visualization."""
        # Stop animation
        self.animation_timer.stop()

        # Clear the graphics scene
        self.scene.clear()

        # Clear input fields
        for i in range(self.inputs_layout.count()):
            layout = self.inputs_layout.itemAt(i)
            try:
                inner = layout.layout() if layout.layout() else layout
                for j in range(inner.count()):
                    widget = inner.itemAt(j).widget()
                    if isinstance(widget, QLineEdit):
                        widget.clear()
            except Exception:
                continue

        # Clear astronomical object fields
        self.astro_radius_entry.clear()
        self.rings_checkbox.setChecked(False)

        # Reset selections to defaults
        self.shape_2d_menu.setCurrentIndex(0)
        self.shape_3d_menu.setCurrentIndex(0)
        self.astro_menu.setCurrentIndex(0)
        self.align_menu.setCurrentIndex(0)
        self.color_combo.setCurrentIndex(0)
        self.anim_checkbox.setChecked(False)
        self.log_scale_checkbox.setChecked(False)
        self.opacity_slider.setValue(100)

        # Reset zoom/view
        self.reset_view()

        # Clear results
        self.result_label.setText("⏳ Results will be shown here.")

        # Reset info label
        self.info_label.setText("• Select a shape and astronomical object\n• Choose an alignment type\n• Click 'Draw & Calculate' to visualize")

        # Reset shape and astronomical object references
        self.current_shape = None
        self.astro_object = None

        # Update status
        self.status_label.setText("🔄 All inputs cleared. Ready for new calculation.")

    def toggle_animation(self, state):
        """Toggle animation on or off."""
        if state == Qt.Checked and self.current_shape and self.astro_object:
            interval = max(16, int(200 / max(1, self.animation_speed * 2)))
            self.animation_timer.start(interval)
            self.animation_angle = 0.0
        else:
            self.animation_timer.stop()

    def update_animation_speed(self, speed):
        """Update the animation speed."""
        self.animation_speed = speed / 5.0  # Normalize to 0.2-2.0 range
        if self.animation_timer.isActive():
            interval = max(16, int(200 / max(1, self.animation_speed * 2)))
            self.animation_timer.start(interval)

    def animate(self):
        """Animate the shape in orbit around the astronomical object."""
        if not self.astro_object or not self.current_shape:
            self.animation_timer.stop()
            return

        # Increment angle based on speed
        self.animation_angle += 0.05 * self.animation_speed
        # Keep angle in radians for cos/sin
        # convert to radians (wrap if large)
        self.animation_angle = self.animation_angle % (2 * math.pi)

        # Redraw the scene with new position
        scene_rect = self.scene.sceneRect()
        scale = self.calculate_scale(scene_rect) * self.scale_spinbox.value()

        astro_x, astro_y = scene_rect.width() / 2, scene_rect.height() / 2

        # Calculate orbit position
        shape_w, shape_h, _ = self.current_shape.natural_size()
        shape_w_px = shape_w * scale
        astro_radius_px = self.astro_object._radius * scale

        orbit_radius = astro_radius_px + shape_w_px/2 + 10  # 10px margin
        shape_x = astro_x + orbit_radius * math.cos(self.animation_angle)
        shape_y = astro_y + orbit_radius * math.sin(self.animation_angle)

        # Redraw everything
        self.scene.clear()
        if self.grid_visible:
            self.draw_grid(scene_rect)
        self.astro_object.draw(self.scene, astro_x, astro_y, scale)

        shape_color = self.get_shape_color()
        base_color = shape_color if shape_color else QColor("#4FC3F7")
        alpha = int(self.opacity_slider.value() * 2.55)
        base_color.setAlpha(alpha)
        self.current_shape.draw(self.scene, shape_x, shape_y, scale, base_color)

        # Draw orbit path (faint)
        orbit = self.scene.addEllipse(
            astro_x - orbit_radius,
            astro_y - orbit_radius,
            orbit_radius * 2,
            orbit_radius * 2,
            QPen(QColor(255, 255, 255, 100), 1, Qt.DashLine)
        )
        orbit.setZValue(-1)

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
                # Recalculate to adapt to new scene size without losing zoom transform
                self.calculate()

    # ----------------- New UX helpers -----------------
    def zoom_view(self, factor):
        """Zoom the QGraphicsView by factor while updating zoom label."""
        self.view_scale *= factor
        # Limit zoom level
        self.view_scale = max(0.1, min(self.view_scale, 10.0))
        self.view.resetTransform()
        self.view.scale(self.view_scale, self.view_scale)
        self.zoom_label.setText(f"Zoom: {int(self.view_scale * 100)}%")

    def reset_view(self):
        """Reset zoom and pan to defaults."""
        self.view_scale = 1.0
        self.view.resetTransform()
        self.zoom_label.setText(f"Zoom: {int(self.view_scale * 100)}%")
        # Reset pan by centering the scene
        self.view.ensureVisible(self.scene.sceneRect())

    def snapshot_canvas(self):
        """Save current canvas to an image file (PNG)."""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Snapshot", "", "PNG Images (*.png);;JPEG Images (*.jpg)")
            if not filename:
                return
            # Render scene to image
            rect = self.scene.sceneRect()
            img = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
            img.fill(Qt.transparent)
            painter = QPainter(img)
            self.scene.render(painter)
            painter.end()
            img.save(filename)
            self.status_label.setText(f"🖼️ Snapshot saved to {filename}")
        except Exception as e:
            self.show_error_message(f"Could not save snapshot: {str(e)}")

    def toggle_grid(self):
        """Toggle background grid on/off."""
        self.grid_visible = not self.grid_visible
        # Redraw current scene (preserve shapes)
        if self.current_shape:
            self.calculate()

# ----------------- Run -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeometryApp()
    window.show()
    sys.exit(app.exec_())