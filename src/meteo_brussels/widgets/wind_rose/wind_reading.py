from PySide6.QtWidgets import QHBoxLayout, QWidget
from sensor_types import InnerWind
from widgets.big_label import BigLabel

class WindReading(QWidget):
	_data: InnerWind
	def __init__(self) -> None:
		super().__init__()

		self._layout = QHBoxLayout()
		self.setLayout(self._layout)

		self._heading = BigLabel()
		self._speed = BigLabel()
		self._layout.addStretch()
		self._layout.addWidget(self._heading, stretch=0)
		self._layout.addSpacing(5)
		self._layout.addWidget(self._speed, stretch=0)
		self._layout.addStretch()

	def set_data(self, wind: InnerWind):
		self._data = wind
		self._heading.setText(f"{wind.wind_direction:03d}°")
		self._speed.setText(f"{wind.wind_speed:02d}kt")


