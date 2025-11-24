from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from . import WindRose
from sensor_types import SensorReading, Reading

class PopOutRose(QWidget):
	_rose: WindRose
	_key: str

	about_to_close = Signal()

	def __init__(self, key: str, reading: SensorReading):
		super().__init__()

		self._key = key

		# Window setp
		self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
		self.setWindowFlag(Qt.WindowType.Tool) # Gives it a smaller titlebar, and no taskbar entry, but also makes it not fully quit when window is closed...
		self.setWindowTitle(self._key)

		self._rose = WindRose(can_pop_out=False)
		
		self._layout = QVBoxLayout()
		self.setLayout(self._layout)
		self._layout.addWidget(self._rose)

		self.set_data(reading)

	def set_data(self, reading: SensorReading) -> None:
		self._rose.set_wind(reading)
		self._rose.setWindowTitle(reading.label)

	def set_data_from(self, reading: Reading) -> None:
		self.set_data(reading.wind_sensor_detail[self._key].sensor_reading)

	def get_key(self) -> str:
		return self._key

	def closeEvent(self, event: QCloseEvent) -> None:
		self.about_to_close.emit()
		return super().closeEvent(event)