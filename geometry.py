# Geometry
import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView,
    QSizePolicy
)
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor
from PyQt5.QtCore import QPointF


# ----------------- OOP Classes -----------------
class Shape:
    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def draw(self, scene):
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

    def draw(self, scene):
        scene.clear()
        diameter = min(2 * self.radius, 180)
        x = (300 - diameter) / 2
        y = (200 - diameter) / 2
        ellipse = scene.addEllipse(x, y, diameter, diameter)
        ellipse.setBrush(QBrush(QColor("lightblue")))
        ellipse.setPen(QPen(QColor("blue"), 3))


class Rectangle(Shape):
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def draw(self, scene):
        scene.clear()
        w = min(self.width, 280)
        h = min(self.height, 180)
        x = (300 - w) / 2
        y = (200 - h) / 2
        rect = scene.addRect(x, y, w, h)
        rect.setBrush(QBrush(QColor("lightgreen")))
        rect.setPen(QPen(QColor("green"), 3))


class Triangle(Shape):
    def __init__(self, base, height):
        if base <= 0 or height <= 0:
            raise ValueError("Base and height must be positive")
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

    def perimeter(self):
        hypotenuse = math.sqrt(self.base ** 2 + self.height ** 2)
        return self.base + self.height + hypotenuse

    def draw(self, scene):
        scene.clear()
        base = min(self.base, 280)
        height = min(self.height, 180)
        x_center = 150
        y_top = 10
        points = [
            QPointF(x_center, y_top),
            QPointF(x_center - base / 2, y_top + height),
            QPointF(x_center + base / 2, y_top + height)
        ]
        polygon = QPolygonF(points)
        poly_item = scene.addPolygon(polygon)
        poly_item.setBrush(QBrush(QColor("yellow")))
        poly_item.setPen(QPen(QColor("orange"), 3))


class Square(Shape):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self.side = side

    def area(self):
        return self.side ** 2

    def perimeter(self):
        return 4 * self.side

    def draw(self, scene):
        scene.clear()
        s = min(self.side, 180)
        x = (300 - s) / 2
        y = (200 - s) / 2
        rect = scene.addRect(x, y, s, s)
        rect.setBrush(QBrush(QColor("pink")))
        rect.setPen(QPen(QColor("red"), 3))


class Ellipse(Shape):
    def __init__(self, a, b):
        if a <= 0 or b <= 0:
            raise ValueError("Axes must be positive")
        self.a = a
        self.b = b

    def area(self):
        return math.pi * self.a * self.b

    def perimeter(self):
        # Ramanujan approximation
        h = ((self.a - self.b) ** 2) / ((self.a + self.b) ** 2)
        return math.pi * (self.a + self.b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

    def draw(self, scene):
        scene.clear()
        w = min(2 * self.a, 280)
        h = min(2 * self.b, 180)
        x = (300 - w) / 2
        y = (200 - h) / 2
        ellipse = scene.addEllipse(x, y, w, h)
        ellipse.setBrush(QBrush(QColor("lightyellow")))
        ellipse.setPen(QPen(QColor("brown"), 3))


class Parallelogram(Shape):
    def __init__(self, base, side, height):
        if base <= 0 or side <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")
        self.base = base
        self.side = side
        self.height = height

    def area(self):
        return self.base * self.height

    def perimeter(self):
        return 2 * (self.base + self.side)

    def draw(self, scene):
        scene.clear()
        base = min(self.base, 200)
        height = min(self.height, 150)
        points = [
            QPointF(50, 50),
            QPointF(50 + base, 50),
            QPointF(50 + base + 30, 50 + height),
            QPointF(50 + 30, 50 + height)
        ]
        polygon = QPolygonF(points)
        poly_item = scene.addPolygon(polygon)
        poly_item.setBrush(QBrush(QColor("cyan")))
        poly_item.setPen(QPen(QColor("darkblue"), 3))


class Rhombus(Shape):
    def __init__(self, d1, d2):
        if d1 <= 0 or d2 <= 0:
            raise ValueError("Diagonals must be positive")
        self.d1 = d1
        self.d2 = d2

    def area(self):
        return (self.d1 * self.d2) / 2

    def perimeter(self):
        side = math.sqrt((self.d1 / 2) ** 2 + (self.d2 / 2) ** 2)
        return 4 * side

    def draw(self, scene):
        scene.clear()
        d1 = min(self.d1, 200)
        d2 = min(self.d2, 150)
        x_center, y_center = 150, 100
        points = [
            QPointF(x_center, y_center - d2 / 2),
            QPointF(x_center + d1 / 2, y_center),
            QPointF(x_center, y_center + d2 / 2),
            QPointF(x_center - d1 / 2, y_center)
        ]
        polygon = QPolygonF(points)
        poly_item = scene.addPolygon(polygon)
        poly_item.setBrush(QBrush(QColor("violet")))
        poly_item.setPen(QPen(QColor("purple"), 3))


class Pentagon(Shape):
    def __init__(self, side):
        if side <= 0:
            raise ValueError("Side must be positive")
        self.side = side

    def area(self):
        return (5 * self.side ** 2) / (4 * math.tan(math.pi / 5))

    def perimeter(self):
        return 5 * self.side

    def draw(self, scene):
        scene.clear()
        r = min(self.side * 1.5, 80)
        cx, cy = 150, 100
        points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5 - math.pi / 2
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append(QPointF(x, y))
        polygon = QPolygonF(points)
        poly_item = scene.addPolygon(polygon)
        poly_item.setBrush(QBrush(QColor("orange")))
        poly_item.setPen(QPen(QColor("darkred"), 3))


# ----------------- GUI Application -----------------
class GeometryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geometry OOP Project")
        self.setGeometry(200, 200, 400, 500)

        layout = QVBoxLayout()

        # Shape selection
        self.shape_menu = QComboBox()
        self.shape_menu.addItems([
            "Circle", "Rectangle", "Triangle",
            "Square", "Ellipse", "Parallelogram",
            "Rhombus", "Pentagon"
        ])
        self.shape_menu.currentIndexChanged.connect(self.update_labels)
        layout.addWidget(QLabel("Select Shape:"))
        layout.addWidget(self.shape_menu)

        # Dimension inputs
        self.label1 = QLabel("Dimension 1:")
        self.entry1 = QLineEdit()
        self.label2 = QLabel("Dimension 2:")
        self.entry2 = QLineEdit()
        self.label3 = QLabel("Dimension 3:")
        self.entry3 = QLineEdit()

        layout.addWidget(self.label1)
        layout.addWidget(self.entry1)
        layout.addWidget(self.label2)
        layout.addWidget(self.entry2)
        layout.addWidget(self.label3)
        layout.addWidget(self.entry3)

        # Buttons
        self.calc_btn = QPushButton("Draw & Calculate")
        self.calc_btn.clicked.connect(self.calculate)
        layout.addWidget(self.calc_btn)

        # Graphics area
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(300, 200)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scene.setSceneRect(0, 0, 300, 200)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.update_labels()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = self.view.size()
        self.scene.setSceneRect(0, 0, size.width(), size.height())

    def update_labels(self):
        shape = self.shape_menu.currentText()

        # 🔥 Reset all fields
        self.entry1.clear()
        self.entry2.clear()
        self.entry3.clear()

        # Enable all by default
        self.entry1.setDisabled(False)
        self.entry2.setDisabled(False)
        self.entry3.setDisabled(False)

        self.label1.show()
        self.entry1.show()
        self.label2.show()
        self.entry2.show()
        self.label3.hide()
        self.entry3.hide()

        if shape == "Circle":
            self.label1.setText("Radius:")
            self.label2.hide()
            self.entry2.hide()

        elif shape == "Rectangle":
            self.label1.setText("Width:")
            self.label2.setText("Height:")

        elif shape == "Triangle":
            self.label1.setText("Base:")
            self.label2.setText("Height:")

        elif shape == "Square":
            self.label1.setText("Side:")
            self.label2.hide()
            self.entry2.hide()

        elif shape == "Ellipse":
            self.label1.setText("Semi-major axis (a):")
            self.label2.setText("Semi-minor axis (b):")

        elif shape == "Parallelogram":
            self.label1.setText("Base:")
            self.label2.setText("Side:")
            self.label3.show()
            self.entry3.show()
            self.label3.setText("Height:")

        elif shape == "Rhombus":
            self.label1.setText("Diagonal 1:")
            self.label2.setText("Diagonal 2:")

        elif shape == "Pentagon":
            self.label1.setText("Side:")
            self.label2.hide()
            self.entry2.hide()

    def calculate(self):
        shape = self.shape_menu.currentText()
        try:
            val1 = float(self.entry1.text()) if self.entry1.isVisible() and self.entry1.text() else None
            val2 = float(self.entry2.text()) if self.entry2.isVisible() and self.entry2.text() else None
            val3 = float(self.entry3.text()) if self.entry3.isVisible() and self.entry3.text() else None

            if shape == "Circle":
                obj = Circle(val1)
            elif shape == "Rectangle":
                obj = Rectangle(val1, val2)
            elif shape == "Triangle":
                obj = Triangle(val1, val2)
            elif shape == "Square":
                obj = Square(val1)
            elif shape == "Ellipse":
                obj = Ellipse(val1, val2)
            elif shape == "Parallelogram":
                obj = Parallelogram(val1, val2, val3)
            elif shape == "Rhombus":
                obj = Rhombus(val1, val2)
            elif shape == "Pentagon":
                obj = Pentagon(val1)
            else:
                raise ValueError("Select a shape")

            obj.draw(self.scene)
            QMessageBox.information(self, "Results",
                                    f"Area = {obj.area():.2f}\nPerimeter = {obj.perimeter():.2f}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ----------------- Run -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeometryApp()
    window.show()
    sys.exit(app.exec_())

