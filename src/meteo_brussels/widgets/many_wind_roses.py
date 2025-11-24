from typing import cast
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from sensor_types import Reading, SensorReading, RunwaySensorData
from widgets.wind_rose import WindRose


# TODO popout buttons?
class ManyWindRoses(QWidget):
	_reading: Reading
	_show_keys: list[str] = []
	_roses: dict[str, WindRose] = {}

	popped_out = Signal(str)

	def __init__(self) -> None:
		super().__init__()
		self._layout = QVBoxLayout(self)
		self.setLayout(self._layout)

	def _render(self) -> None:
		keys_to_delete = [(key, val) for (key, val) in self._roses.items() if key not in self._show_keys]

		for (key, rose) in keys_to_delete:
			if key in self._show_keys:
				continue

			self._layout.removeWidget(rose)
			rose.deleteLater()
			self._roses.pop(key, None)
		
		for (key, reading) in self._reading.wind_sensor_detail.items():
			if "runway-" not in key:
				continue

			if key not in self._show_keys:
				continue

			if key not in self._roses.keys():
				self._roses[key] = WindRose()
				self._roses[key].popped_out.connect(self.popped_out)
				self._layout.addWidget(self._roses[key])

			self._roses[key].set_wind(cast(RunwaySensorData, reading).sensor_reading)

	def set_reading(self, reading: Reading) -> None:
		self._reading = reading
		self._render()

	def set_show_keys(self, show_keys: list[str]) -> None:
		self._show_keys = show_keys

		self._render()

	def set_show_debug(self, show_debug: bool) -> None:
		for (_key, rose) in self._roses.items():
			rose.set_debug(show_debug)