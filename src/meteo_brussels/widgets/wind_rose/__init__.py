from math import floor
import math
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGridLayout, QSizePolicy, QPushButton, QLabel, QFrame, QGraphicsLineItem, QAbstractGraphicsShapeItem, QApplication
from PySide6.QtGui import QBrush, QColor, QPen, QResizeEvent, QShowEvent, QIcon, QTransform
from PySide6.QtCore import QEvent, Qt, QLineF, Signal
from widgets import DARK_GREEN, BLUE
from widgets.big_label import BigLabel
from .wind_reading import WindReading
from sensor_types import SensorReading
from .arc import QGraphicsArcItem


def normalise_heading(heading: int) -> int:
    """
    Takes a heading in degrees,
    and turns it into a standard angle.

    Qt angles follow these invariants:
    - angles are integers, in 16ths of a degree
    - 0° is at 3 o'clock
    - Positive angles go counter-clockwise

    Wind rose angles go differently,
    0 is at the top and positive angles go to the right.

    This method does not convert to 16ths of a degree
    """
    return (- heading + 90) % 360



# TODO verify its correct... I've seen some things going bad... VRB btn 300 and 000, heading 320 seems to give bad results
class WindRose(QFrame):
    pie_width = 10.0
    _sensor_reading: SensorReading
    """Width of the slice showing current wind direction"""
    _tick_items: list[QAbstractGraphicsShapeItem | QGraphicsLineItem] = []
    _radius: int = 50

    popped_out = Signal(str)


    def __init__(self, show_debug_lines: bool = False, can_pop_out: bool = True):
        super().__init__()

        self.show_debug_lines = show_debug_lines

        if can_pop_out:
            self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
            self.setLineWidth(2)

        self._scene = QGraphicsScene()
        self._scene.setBackgroundBrush(self.palette().base())

        self.central = QGraphicsEllipseItem(-self._radius, -self._radius, 2*self._radius, 2*self._radius)
        self.central.setBrush(QBrush(DARK_GREEN))
        self.central.setPen(Qt.PenStyle.NoPen)

        arc_pen = QPen(BLUE, 10.0, c=Qt.PenCapStyle.FlatCap)
        self.left_arc = QGraphicsArcItem(-self._radius, -self._radius, 2*self._radius, 2*self._radius)
        self.left_arc.setPen(arc_pen)
        self.left_arc.setBrush(Qt.BrushStyle.NoBrush)
        self.right_arc = QGraphicsArcItem(-self._radius, -self._radius, 2*self._radius, 2*self._radius)
        self.right_arc.setPen(arc_pen)
        self.right_arc.setBrush(Qt.BrushStyle.NoBrush)

        self._scene.addItem(self.central)
        self._scene.addItem(self.left_arc)
        self._scene.addItem(self.right_arc)

        self._draw_tick_marks()

        # Add placeholder orientation lines
        self.heading_line = self._scene.addLine(self._radius, self._radius, 0, 0, QPen(QColor.fromString("pink"), 0.0))

        debug_pen = QPen(QColor.fromString("cyan"), 0.0)
        self.wind_lower_line = self._scene.addLine(self._radius, self._radius, 0, 0, debug_pen)
        self.wind_upper_line = self._scene.addLine(self._radius, self._radius, 0, 0, debug_pen)

        self.heading_line.setVisible(self.show_debug_lines)
        self.wind_lower_line.setVisible(self.show_debug_lines)
        self.wind_upper_line.setVisible(self.show_debug_lines)

        self.view = QGraphicsView(self._scene)
        self._layout = QGridLayout()

        self.title = BigLabel(scaling=1.5)
        self._layout.addWidget(self.view, 0, 0, 1, 4)
        self._layout.addWidget(self.title, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        if can_pop_out:
            popout_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.WindowNew), "")
            popout_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            popout_button.pressed.connect(lambda: self.popped_out.emit("runway-" + self._sensor_reading.label))
            self._layout.addWidget(popout_button, 0, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self._reading_widget = WindReading()
        self._layout.addWidget(self._reading_widget, 1, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignHCenter)

        # variability
        self._layout.addWidget(QLabel("VRB BTN", alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter), 2, 0)
        self._variable_lower = BigLabel(scaling=1.5)
        self._layout.addWidget(self._variable_lower, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(QLabel("AND", alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter), 2, 2)
        self._variable_upper = BigLabel(scaling=1.5)
        self._layout.addWidget(self._variable_upper, 2, 3, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)
        self._layout.setColumnStretch(2, 1)
        self._layout.setColumnStretch(3, 2)
        self.setLayout(self._layout)

    def set_wind(self, reading: SensorReading) -> None:
        self._sensor_reading = reading

        self._render()

    def set_debug(self, val: bool) -> None:
        self.show_debug_lines = val
        self.heading_line.setVisible(self.show_debug_lines)
        self.wind_lower_line.setVisible(self.show_debug_lines)
        self.wind_upper_line.setVisible(self.show_debug_lines)

    def _render(self):
        self.title.setText(self._sensor_reading.label)
        self._reading_widget.set_data(self._sensor_reading)

        vrb_lower = (self._sensor_reading.wind_direction - self._sensor_reading.wind_direction_deviation_left) % 360
        vrb_upper = (self._sensor_reading.wind_direction + self._sensor_reading.wind_direction_deviation_right) % 360
        self._variable_lower.setText(f"{vrb_lower:03d}°")
        self._variable_upper.setText(f"{vrb_upper:03d}°")

        wind_angle = normalise_heading(self._sensor_reading.wind_direction)

        self.heading_line.setLine(self.line_for_wind_heading(self._sensor_reading.wind_direction))
        self.wind_lower_line.setLine(self.line_for_wind_heading(self._sensor_reading.wind_direction + self._sensor_reading.wind_direction_deviation_left))
        self.wind_upper_line.setLine(self.line_for_wind_heading(self._sensor_reading.wind_direction - self._sensor_reading.wind_direction_deviation_right))

        # Normalisation functions guarantee positive angles from any heading. This simplifies

        self.central.setStartAngle(floor((wind_angle + self.pie_width / 2) * 16.0))
        self.central.setSpanAngle(floor((360.0 - self.pie_width) * 16))

        self.left_arc.setStartAngle(floor(wind_angle + self.pie_width / 2) * 16)
        self.left_arc.setSpanAngle(self._sensor_reading.wind_direction_deviation_left * 16)

        self.right_arc.setStartAngle(floor(wind_angle - self.pie_width / 2) * 16)
        self.right_arc.setSpanAngle(-self._sensor_reading.wind_direction_deviation_right * 16)

        self._fit()


    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._fit()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._fit()


    def get_reading(self) -> SensorReading:
        return self._sensor_reading

    def _fit(self) -> None:
        content_rect = self._scene.sceneRect()
        self.view.fitInView(content_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def event(self, e: QEvent) -> bool:
        if e.type() == QEvent.Type.PaletteChange:
            self._scene.setBackgroundBrush(self.palette().base())
            pen = QPen(self.palette().windowText(), 0.0)
            for item in self._tick_items:
                item.setPen(pen)
        return super().event(e)

    def _draw_tick_marks(self) -> None:
        pen = QPen(self.palette().windowText(), 0.0)

        self._tick_items.append(self._scene.addEllipse(-self._radius, -self._radius, 2*self._radius, 2*self._radius, pen, Qt.BrushStyle.NoBrush))

        font = QApplication.font()
        font.setPixelSize(2)

        for heading in range(10, 360 + 1, 10):
            angle = normalise_heading(heading)
            y_heading = -math.sin(math.radians(angle))
            x_heading = math.cos(math.radians(angle))

            scale = 3 if angle % 30 == 0 else 1

            y_start = y_heading * self._radius
            y_end = y_heading * (self._radius + scale)
            x_start = x_heading * self._radius
            x_end = x_heading * (self._radius + scale)

            self._tick_items.append(self._scene.addLine(x_start, y_start, x_end, y_end, pen))

            if angle % 30 == 0:
                txt = self._scene.addText(f"{heading:03d}", font)
                txt.adjustSize()
                bound = txt.sceneTransform().mapRect(txt.boundingRect())
                txt_x = x_start
                txt_y = y_start

                if 0 <= angle < 180:
                    txt_y -= bound.height() / 2

                if heading == 360:
                    txt_y -= bound.height() / 4

                if 180 < heading < 360:
                    txt_x -= bound.width()

                txt.setPos(txt_x, txt_y)
                # TODO add to list


    def line_for_wind_heading(self, heading: int) -> QLineF:
        normalised_heading = normalise_heading(heading)
        y_heading = -math.sin(math.radians(normalised_heading)) * self._radius
        x_heading = math.cos(math.radians(normalised_heading)) * self._radius
        return QLineF(0, 0, x_heading, y_heading)
