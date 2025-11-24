from math import floor
import math
from PySide6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout, QGraphicsEllipseItem, QGridLayout, QSizePolicy, QPushButton
from PySide6.QtGui import QBrush, QColor, QPen, QResizeEvent, QShowEvent, QIcon
from PySide6.QtCore import Qt, QLineF, Signal
from widgets import DARK_GREEN, BLUE
from widgets.big_label import BigLabel
from .wind_reading import WindReading
from sensor_types import SensorReading
from .arc import QGraphicsArcItem


def transform_angle(angle: float) -> int:
	"""
	Takes a float angle in degrees,
	and turns it into a Qt angle.

	Qt angles follow these invariants:
	- angles are integers, in 16ths of a degree
	- 0° is at 3 o'clock
	- Positive angles go counter-clockwise

	Wind rose angles go differently,
	0 is at the top and positive angles go to the right
	"""
	angle = -angle + 90.0
	angle = angle % 360.0

	return floor(angle * 16) # Integer representation

def normalise_heading(heading: int) -> int:
	"""same as above, but only corrects the transform"""
	return (- heading + 90) % 360


def line_for_wind_heading(heading: int) -> QLineF:
	normalised_heading = normalise_heading(heading)
	y_heading = -math.sin(math.radians(normalised_heading)) * 5 + 5
	x_heading = math.cos(math.radians(normalised_heading)) * 5 + 5
	return QLineF(5, 5, x_heading, y_heading)


class WindRose(QWidget):
	pie_width = 10.0
	_sensor_reading: SensorReading
	"""Width of the slice showing current wind direction"""

	popped_out = Signal(str)


	def __init__(self, show_debug_lines: bool = False, show_pop_out_button: bool = True):
		super().__init__()

		self.show_debug_lines = show_debug_lines

		self.scene = QGraphicsScene()

		self.central = QGraphicsEllipseItem(0, 0, 10, 10)
		self.central.setBrush(QBrush(DARK_GREEN))
		self.central.setPen(Qt.PenStyle.NoPen)

		arc_pen = QPen(BLUE, 1.0, c=Qt.PenCapStyle.FlatCap)
		self.left_arc = QGraphicsArcItem(0, 0, 10, 10)
		self.left_arc.setPen(arc_pen)
		self.left_arc.setBrush(Qt.BrushStyle.NoBrush)
		self.right_arc = QGraphicsArcItem(0, 0, 10, 10)
		self.right_arc.setPen(arc_pen)
		self.right_arc.setBrush(Qt.BrushStyle.NoBrush)

		self.scene.addItem(self.central)
		self.scene.addItem(self.left_arc)
		self.scene.addItem(self.right_arc)

		# Temporary, until I figure out tickmarks
		pen = QPen(self.palette().windowText(), 0.0)
		self.scene.addLine(0, 0, 10, 10, pen)
		self.scene.addLine(0, 10, 10, 0, pen)
		self.scene.addLine(0, 5, 10, 5, pen)
		self.scene.addLine(5, 0, 5, 10, pen)

		# Add placeholder orientation lines
		self.heading_line = self.scene.addLine(5, 5, 0, 0, QPen(QColor.fromString("pink"), 0.0))

		debug_pen = QPen(QColor.fromString("cyan"), 0.0)
		self.wind_lower_line = self.scene.addLine(5, 5, 0, 0, debug_pen)
		self.wind_upper_line = self.scene.addLine(5, 5, 0, 0, debug_pen)

		self.heading_line.setVisible(self.show_debug_lines)
		self.wind_lower_line.setVisible(self.show_debug_lines)
		self.wind_upper_line.setVisible(self.show_debug_lines)

		self.view = QGraphicsView(self.scene)
		self._layout = QGridLayout()

		self.title = BigLabel(scaling=1.5)
		self._layout.addWidget(self.view, 0, 0)
		self._layout.addWidget(self.title, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
		
		if show_pop_out_button:
			popout_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.WindowNew), "")
			popout_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
			popout_button.pressed.connect(lambda: self.popped_out.emit("runway-" + self._sensor_reading.label))
			self._layout.addWidget(popout_button, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

		self._reading_widget = WindReading()
		self._layout.addWidget(self._reading_widget, 1, 0)

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

		wind_angle = normalise_heading(self._sensor_reading.wind_direction)

		self.heading_line.setLine(line_for_wind_heading(self._sensor_reading.wind_direction))
		self.wind_lower_line.setLine(line_for_wind_heading(self._sensor_reading.wind_direction + self._sensor_reading.wind_direction_deviation_left))
		self.wind_upper_line.setLine(line_for_wind_heading(self._sensor_reading.wind_direction - self._sensor_reading.wind_direction_deviation_right))

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
		self.view.fitInView(0, 0, 12, 12, Qt.AspectRatioMode.KeepAspectRatio)