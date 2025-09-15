# geometry_oop_with_astronomy.py
import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView,
    QSizePolicy, QCheckBox
)
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor
from PyQt5.QtCore import QPointF, QRectF


# ----------------- Base / Abstract-like classes -----------------
class BaseShape2D:
    """Abstract-ish 2D shape interface for area/perimeter/draw/natural_size."""
    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def natural_size(self):
        """Return (width, height) in the shape's own units (unscaled)."""
        raise NotImplementedError

    def draw(self, scene: QGraphicsScene, cx: float, cy: float, scale: float):
        """Draw shape centered at (cx, cy) with a scale factor (units -> pixels)."""
        raise NotImplementedError

    def bounding_box(self, cx: float, cy: float, scale: float):
        """Return (x_min, y_min, x_max, y_max) in pixels for overlap detection."""
        # Default: use natural_size centered box
        w, h = self.natural_size()
        w_px = w * scale
        h_px = h * scale
        return (cx - w_px/2, cy - h_px/2, cx + w_px/2, cy + h_px/2)


# ----------------- 2D Shapes (implementing interface) -----------------
class Circle(BaseShape2D):
    def __init__(self, radius):
        if radius is None or radius <= 0:
            raise ValueError("Radius must be positive")
        self._radius = radius  # encapsulated attribute

    def area(self):
        return math.pi * self._radius ** 2

    def perimeter(self):
        return 2 * math.pi * self._radius

    def natural_size(self):
        d = 2 * self._radius
        return (d, d)

    def draw(self, scene, cx, cy, scale):
        scene.clear() if False else None  # no-op here; caller handles clearing or ordering
        diameter_px = 2 * self._radius * scale
        x = cx - diameter_px/2
        y = cy - diameter_px/2
        ellipse = scene.addEllipse(x, y, diameter_px, diameter_px)
        if ellipse is not None:
            ellipse.setBrush(QBrush(QColor("lightblue")))
            ellipse.setPen(QPen(QColor("blue"), 3))
            ellipse.setZValue(1)

    def bounding_box(self, cx, cy, scale):
        return super().bounding_box(cx, cy, scale)


class Rectangle(BaseShape2D):
    def __init__(self, width, height):
        if width is None or height is None or width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self._width = width
        self._height = height

    def area(self):
        return self._width * self._height

    def perimeter(self):
        return 2 * (self._width + self._height)

    def natural_size(self):
        return (self._width, self._height)

    def draw(self, scene, cx, cy, scale):
        w_px = self._width * scale
        h_px = self._height * scale
        x = cx - w_px/2
        y = cy - h_px/2
        rect = scene.addRect(x, y, w_px, h_px)
        if rect is not None:
            rect.setBrush(QBrush(QColor("lightgreen")))
            rect.setPen(QPen(QColor("green"), 3))
            rect.setZValue(1)


class Triangle(BaseShape2D):
    def __init__(self, base, height):
        if base is None or height is None or base <= 0 or height <= 0:
            raise ValueError("Base and height must be positive")
        self._base = base
        self._height = height

    def area(self):
        return 0.5 * self._base * self._height

    def perimeter(self):
        hyp = math.sqrt(self._base**2 + self._height**2)
        return self._base + self._height + hyp

    def natural_size(self):
        return (self._base, self._height)

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
        if item is not None:
            item.setBrush(QBrush(QColor("yellow")))
            item.setPen(QPen(QColor("orange"), 3))
            item.setZValue(1)


class Square(BaseShape2D):
    def __init__(self, side):
        if side is None or side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return self._side ** 2

    def perimeter(self):
        return 4 * self._side

    def natural_size(self):
        return (self._side, self._side)

    def draw(self, scene, cx, cy, scale):
        s_px = self._side * scale
        x = cx - s_px/2
        y = cy - s_px/2
        rect = scene.addRect(x, y, s_px, s_px)
        if rect is not None:
            rect.setBrush(QBrush(QColor("pink")))
            rect.setPen(QPen(QColor("red"), 3))
            rect.setZValue(1)


class Ellipse(BaseShape2D):
    def __init__(self, a, b):
        if a is None or b is None or a <= 0 or b <= 0:
            raise ValueError("Axes must be positive")
        self._a = a  # semi-major
        self._b = b  # semi-minor

    def area(self):
        return math.pi * self._a * self._b

    def perimeter(self):
        h = ((self._a - self._b) ** 2) / ((self._a + self._b) ** 2)
        return math.pi * (self._a + self._b) * (1 + (3*h) / (10 + math.sqrt(4 - 3*h)))

    def natural_size(self):
        return (2 * self._a, 2 * self._b)

    def draw(self, scene, cx, cy, scale):
        w_px = 2 * self._a * scale
        h_px = 2 * self._b * scale
        x = cx - w_px/2
        y = cy - h_px/2
        ellipse = scene.addEllipse(x, y, w_px, h_px)
        if ellipse is not None:
            ellipse.setBrush(QBrush(QColor("lightyellow")))
            ellipse.setPen(QPen(QColor("brown"), 3))
            ellipse.setZValue(1)


class Parallelogram(BaseShape2D):
    def __init__(self, base, side, height):
        if base is None or side is None or height is None or base <= 0 or side <= 0 or height <= 0:
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
        return (self._base + self._base * 0.2, self._height)

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
        if item is not None:
            item.setBrush(QBrush(QColor("cyan")))
            item.setPen(QPen(QColor("darkblue"), 3))
            item.setZValue(1)


class Rhombus(BaseShape2D):
    def __init__(self, d1, d2):
        if d1 is None or d2 is None or d1 <= 0 or d2 <= 0:
            raise ValueError("Diagonals must be positive")
        self._d1 = d1
        self._d2 = d2

    def area(self):
        return (self._d1 * self._d2) / 2

    def perimeter(self):
        side = math.sqrt((self._d1/2)**2 + (self._d2/2)**2)
        return 4 * side

    def natural_size(self):
        return (self._d1, self._d2)

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
        if item is not None:
            item.setBrush(QBrush(QColor("violet")))
            item.setPen(QPen(QColor("purple"), 3))
            item.setZValue(1)


class Pentagon(BaseShape2D):
    def __init__(self, side):
        if side is None or side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def area(self):
        return (5 * self._side**2) / (4 * math.tan(math.pi/5))

    def perimeter(self):
        return 5 * self._side

    def natural_size(self):
        # approximate bounding box using circumradius ≈ 1.539 * side
        r = 1.539 * self._side
        return (2*r, 2*r)

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
        if item is not None:
            item.setBrush(QBrush(QColor("orange")))
            item.setPen(QPen(QColor("darkred"), 3))
            item.setZValue(1)


# ----------------- Astronomical Object -----------------
class AstronomicalObject:
    """Simple circle-astronomical object used for alignment/overlap demonstration."""
    def __init__(self, radius, color="lightgray"):
        if radius is None or radius <= 0:
            raise ValueError("Astronomical radius must be positive")
        self._radius = radius
        self._color = color

    def natural_size(self):
        return (2 * self._radius, 2 * self._radius)

    def draw(self, scene, cx, cy, scale):
        diameter_px = 2 * self._radius * scale
        x = cx - diameter_px/2
        y = cy - diameter_px/2
        item = scene.addEllipse(x, y, diameter_px, diameter_px)
        item.setBrush(QBrush(QColor(self._color)))
        item.setPen(QPen(QColor("black"), 2))
        item.setZValue(0)  # behind shapes

    def bounding_box(self, cx, cy, scale):
        d = 2 * self._radius * scale
        return (cx - d/2, cy - d/2, cx + d/2, cy + d/2)


# ----------------- GUI Application -----------------
class GeometryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geometry OOP Project (2D + Astronomy Alignment)")
        self.setGeometry(200, 200, 600, 600)

        main_layout = QVBoxLayout()

        # --- Control row 1: Shape type and astro show ---
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Select Shape:"))
        self.shape_menu = QComboBox()
        self.shape_menu.addItems([
            "Circle", "Rectangle", "Triangle", "Square",
            "Ellipse", "Parallelogram", "Rhombus", "Pentagon"
        ])
        self.shape_menu.currentIndexChanged.connect(self.update_labels)
        row1.addWidget(self.shape_menu)

        row1.addWidget(QLabel("Astronomy:"))
        self.astro_menu = QComboBox()
        self.astro_menu.addItems(["None", "Planet/Star"])
        self.astro_menu.currentIndexChanged.connect(self.update_labels)
        row1.addWidget(self.astro_menu)

        main_layout.addLayout(row1)

        # --- Inputs area ---
        self.inputs_layout = QVBoxLayout()

        self.label1 = QLabel("Dimension 1:")
        self.entry1 = QLineEdit()
        self.label2 = QLabel("Dimension 2:")
        self.entry2 = QLineEdit()
        self.label3 = QLabel("Dimension 3:")
        self.entry3 = QLineEdit()

        self.inputs_layout.addWidget(self.label1)
        self.inputs_layout.addWidget(self.entry1)
        self.inputs_layout.addWidget(self.label2)
        self.inputs_layout.addWidget(self.entry2)
        self.inputs_layout.addWidget(self.label3)
        self.inputs_layout.addWidget(self.entry3)

        # Astronomical object inputs
        astro_row = QHBoxLayout()
        self.astro_radius_label = QLabel("Astro Radius:")
        self.astro_radius_entry = QLineEdit()
        self.align_label = QLabel("Alignment:")
        self.align_menu = QComboBox()
        self.align_menu.addItems(["Center", "Top", "Bottom", "Left", "Right", "Overlap"])
        astro_row.addWidget(self.astro_radius_label)
        astro_row.addWidget(self.astro_radius_entry)
        astro_row.addWidget(self.align_label)
        astro_row.addWidget(self.align_menu)
        self.inputs_layout.addLayout(astro_row)

        main_layout.addLayout(self.inputs_layout)

        # --- Buttons & result label ---
        btn_row = QHBoxLayout()
        self.calc_btn = QPushButton("Draw & Calculate")
        self.calc_btn.clicked.connect(self.calculate)
        btn_row.addWidget(self.calc_btn)

        self.result_label = QLabel("")
        btn_row.addWidget(self.result_label)
        main_layout.addLayout(btn_row)

        # --- Graphics area ---
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(480, 360)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scene.setSceneRect(0, 0, 480, 360)
        main_layout.addWidget(self.view)

        self.setLayout(main_layout)

        # initialize labels / visibility
        self.update_labels()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        size = self.view.size()
        self.scene.setSceneRect(0, 0, size.width(), size.height())

    def update_labels(self):
        # Reset inputs every time the selection changes
        self.entry1.clear(); self.entry2.clear(); self.entry3.clear()
        self.astro_radius_entry.clear()
        # Enable all by default
        self.entry1.setDisabled(False)
        self.entry2.setDisabled(False)
        self.entry3.setDisabled(False)
        self.astro_radius_entry.setDisabled(False)
        self.align_menu.setDisabled(False)
        self.astro_radius_label.show(); self.astro_radius_entry.show(); self.align_label.show(); self.align_menu.show()

        shape = self.shape_menu.currentText()
        astro_choice = self.astro_menu.currentText()

        # default visibility
        self.label1.show(); self.entry1.show()
        self.label2.show(); self.entry2.show()
        self.label3.hide(); self.entry3.hide()

        if shape == "Circle":
            self.label1.setText("Radius:")
            self.label2.hide(); self.entry2.hide()
        elif shape == "Rectangle":
            self.label1.setText("Width:")
            self.label2.setText("Height:")
        elif shape == "Triangle":
            self.label1.setText("Base:")
            self.label2.setText("Height:")
        elif shape == "Square":
            self.label1.setText("Side:")
            self.label2.hide(); self.entry2.hide()
        elif shape == "Ellipse":
            self.label1.setText("Semi-major axis (a):")
            self.label2.setText("Semi-minor axis (b):")
        elif shape == "Parallelogram":
            self.label1.setText("Base:")
            self.label2.setText("Side:")
            self.label3.show(); self.entry3.show()
            self.label3.setText("Height:")
        elif shape == "Rhombus":
            self.label1.setText("Diagonal 1:")
            self.label2.setText("Diagonal 2:")
        elif shape == "Pentagon":
            self.label1.setText("Side:")
            self.label2.hide(); self.entry2.hide()

        # Astro UI show/hide
        if astro_choice == "None":
            self.astro_radius_label.hide()
            self.astro_radius_entry.hide()
            self.align_label.hide()
            self.align_menu.hide()
        else:
            # visible
            self.astro_radius_label.show(); self.astro_radius_entry.show()
            self.align_label.show(); self.align_menu.show()

    def _create_shape_instance(self, shape_name, v1, v2, v3):
        """Factory returning a BaseShape2D instance (or raise)."""
        if shape_name == "Circle":
            return Circle(v1)
        elif shape_name == "Rectangle":
            return Rectangle(v1, v2)
        elif shape_name == "Triangle":
            return Triangle(v1, v2)
        elif shape_name == "Square":
            return Square(v1)
        elif shape_name == "Ellipse":
            return Ellipse(v1, v2)
        elif shape_name == "Parallelogram":
            return Parallelogram(v1, v2, v3)
        elif shape_name == "Rhombus":
            return Rhombus(v1, v2)
        elif shape_name == "Pentagon":
            return Pentagon(v1)
        else:
            raise ValueError("Unknown shape")

    @staticmethod
    def _rects_intersect(a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)

    def calculate(self):
        shape_name = self.shape_menu.currentText()
        astro_choice = self.astro_menu.currentText()
        alignment = self.align_menu.currentText()

        # parse inputs
        try:
            v1 = float(self.entry1.text()) if self.entry1.isVisible() and self.entry1.text() else None
            v2 = float(self.entry2.text()) if self.entry2.isVisible() and self.entry2.text() else None
            v3 = float(self.entry3.text()) if self.entry3.isVisible() and self.entry3.text() else None

            shape_obj = self._create_shape_instance(shape_name, v1, v2, v3)

            astro_obj = None
            if astro_choice != "None":
                ar = float(self.astro_radius_entry.text()) if self.astro_radius_entry.text() else None
                if ar is None:
                    raise ValueError("Enter astronomical radius")
                astro_obj = AstronomicalObject(ar)

            # Prepare scene sizing and scaling
            scene_rect: QRectF = self.scene.sceneRect()
            scene_w = scene_rect.width()
            scene_h = scene_rect.height()
            # natural sizes
            s_w, s_h = shape_obj.natural_size()
            a_w = a_h = 0
            if astro_obj:
                a_w, a_h = astro_obj.natural_size()

            max_w = max(s_w, a_w) if (s_w and a_w) else (s_w or a_w)
            max_h = max(s_h, a_h) if (s_h and a_h) else (s_h or a_h)
            # avoid zero
            max_w = max(max_w, 1)
            max_h = max(max_h, 1)

            # scale to fit both (85% of scene)
            scale_x = (scene_w * 0.85) / max_w
            scale_y = (scene_h * 0.85) / max_h
            scale = min(scale_x, scale_y, 1.0)

            # compute centers (in pixels)
            astro_cx = scene_w / 2
            astro_cy = scene_h / 2

            # compute shape center based on alignment
            # if no astro, just center shape
            if not astro_obj:
                shape_cx, shape_cy = scene_w / 2, scene_h / 2
            else:
                # in pixel units we will use scaled sizes
                astro_radius_px = astro_obj.natural_size()[0] / 2 * scale
                shape_w_px = s_w * scale
                shape_h_px = s_h * scale
                margin = 6
                if alignment == "Center":
                    shape_cx, shape_cy = astro_cx, astro_cy
                elif alignment == "Top":
                    shape_cx = astro_cx
                    shape_cy = astro_cy - (astro_radius_px + shape_h_px/2 + margin)
                elif alignment == "Bottom":
                    shape_cx = astro_cx
                    shape_cy = astro_cy + (astro_radius_px + shape_h_px/2 + margin)
                elif alignment == "Left":
                    shape_cx = astro_cx - (astro_radius_px + shape_w_px/2 + margin)
                    shape_cy = astro_cy
                elif alignment == "Right":
                    shape_cx = astro_cx + (astro_radius_px + shape_w_px/2 + margin)
                    shape_cy = astro_cy
                else:  # Overlap - slight offset
                    shape_cx = astro_cx + 0.15 * astro_radius_px
                    shape_cy = astro_cy + 0.10 * astro_radius_px

            # Draw both objects: draw astro first (if any), then shape (shape above)
            self.scene.clear()
            if astro_obj:
                astro_obj.draw(self.scene, astro_cx, astro_cy, scale)
            shape_obj.draw(self.scene, shape_cx, shape_cy, scale)

            # overlap detection (bounding-box approximation)
            overlap_text = "N/A"
            if astro_obj:
                astro_bb = astro_obj.bounding_box(astro_cx, astro_cy, scale)
                shape_bb = shape_obj.bounding_box(shape_cx, shape_cy, scale)
                overlap = self._rects_intersect(astro_bb, shape_bb)
                overlap_text = "Yes" if overlap else "No"

            # Prepare result text (use original units for area/perimeter)
            res = f"Area = {shape_obj.area():.3f} | Perimeter = {shape_obj.perimeter():.3f}"
            if astro_obj:
                res += f"    | Overlap with astro: {overlap_text}"

            # show in label and popup
            self.result_label.setText(res)
            QMessageBox.information(self, "Results", res)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ----------------- Run -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeometryApp()
    window.show()
    sys.exit(app.exec_())
