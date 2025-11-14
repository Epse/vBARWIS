from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget)

from .model import SensorTableModel
from sensor_types import Reading

class SensorTable(QWidget):
	def __init__(self, data: Reading | None = None):
		super().__init__()

		self.model = SensorTableModel()
		if data:
			self.model.load_data(data)

		self.table_view = QTableView()
		self.table_view.setModel(self.model)

		self.horizontal_header = self.table_view.horizontalHeader()
		self.table_view.verticalHeader().hide()
		self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
		self.horizontal_header.setStretchLastSection(True)

		self.main_layout = QHBoxLayout()
		size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

		self.table_view.setSizePolicy(size)
		self.main_layout.addWidget(self.table_view, stretch=1)

		self.setLayout(self.main_layout)

	def load_data(self, data: Reading | None) -> None:
		self.model.load_data(data)