from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidget
from PySide6.QtCore import Qt
import logging

from sensor_types.readings import Reading, RunwaySensorData
from .wind_cell import WindCell

class WindGrid(QWidget):
	data: Reading | None = None
	log = logging.getLogger(__name__)

	def __init__(self):
		super().__init__()

		self.outer_layout = QVBoxLayout()
		self.outer_layout.addWidget(QLabel("WIND"))

		self.table = QTableWidget()
		self.table.setColumnCount(4)
		self.table.setHorizontalHeaderLabels(["CROSS", "MAX", "TAIL", "MAX"])
		self.render_inner()

		self.outer_layout.addWidget(self.table)
		self.setLayout(self.outer_layout)

	def load_data(self, data: Reading | None) -> None:
		self.data = data
		self.render_inner()

	def render_inner(self) -> None:
		for i in range(self.table.rowCount()):
			self.table.removeRow(i)

		if not self.data:
			self.table.setRowCount(0)
			return

		keys = [key for key in self.data.wind_sensor_detail.keys() if "runway-" in key]
		self.table.setRowCount(len(keys))
		self.table.setVerticalHeaderLabels([key[len("runway-"):].upper() for key in keys])

		for (idx, key) in enumerate(keys):
			item = self.data.wind_sensor_detail[key]
			if not isinstance(item, RunwaySensorData):
				self.log.warning(f"Item for sensor {key} is not of runway type?")
				continue # Should never happen

			self.table.setItem(idx, 0, WindCell(item.sensor_wind.cross_wind, "RL"))
			self.table.setItem(idx, 2, WindCell(item.sensor_wind.tail_wind, "TH"))

		