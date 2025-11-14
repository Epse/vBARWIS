from typing import Any
from PySide6.QtCore import QObject, QPersistentModelIndex, Qt, QAbstractTableModel, QModelIndex

from sensor_types import Reading, RunwaySensorData

class SensorTableModel(QAbstractTableModel):
	sensor_data: Reading | None = None

	def __init__(self) -> None:
		super().__init__()

	def load_data(self, x: Reading | None) -> None:
		# It may be better to emit layoutChanged, because then the selection might remain active..
		self.beginResetModel()
		self.sensor_data = x
		self.endResetModel()

	def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
		if self.sensor_data:
			return len(self.sensor_data.wind_sensor_detail)
		return 0

	def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
		return 3

	def headerData(self, section: int, orientation: Qt.Orientation, /, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
		if role != Qt.ItemDataRole.DisplayRole:
			return None

		if orientation == Qt.Orientation.Horizontal:
			return ("Sensor", "Wind", "Tail/XWind")[section]
		else:
			return f"{section}"

	def data(self, index: QModelIndex | QPersistentModelIndex, /, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
		col = index.column()
		row = index.row()

		if role != Qt.ItemDataRole.DisplayRole:
			return None

		if not self.sensor_data:
			return None

		items = list(self.sensor_data.wind_sensor_detail.items())
		
		if col == 0:
			return items[row][0]
		elif col == 1:
			# Wind
			return items[row][1].sensor_reading.to_human()
		elif col == 2:
			item = items[row][1]
			if isinstance(item, RunwaySensorData):
				return str(item.sensor_wind)
			else:
				return None
		
		return None