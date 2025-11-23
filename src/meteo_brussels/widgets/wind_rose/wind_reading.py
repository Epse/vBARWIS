from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from sensor_types import InnerWind

class WindReading(QWidget):
	_data: InnerWind
	def __init__(self) -> None:
		super().__init__()

		self._layout = QHBoxLayout()
		self.setLayout(self._layout)

		self._heading = QLabel()
		self._speed = QLabel()
		self._layout.addWidget(self._heading)
		self._layout.addWidget(self._speed)

	def set_data(self, wind: InnerWind):
		self._data = wind
		self._heading.setText(f"{wind.wind_direction:03d}°")
		self._speed.setText(f"{wind.wind_speed:02d}kt")


