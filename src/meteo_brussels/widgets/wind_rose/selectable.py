from typing import cast
from PySide6.QtWidgets import QSizePolicy, QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout, QGraphicsEllipseItem, QLabel, QHBoxLayout, QButtonGroup, QAbstractButton, QRadioButton
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QPalette, QPen, QRegion, QResizeEvent
from PySide6.QtCore import QLocale, QPoint, QRect, QSize, Qt, QLineF, Signal
from . import WindRose
from sensor_types import Reading

class SelectableWindRose(QWidget):
	_reading: Reading
	_selected_key: str
	_keys: list[str] = []

	selected = Signal(str)
	popped_out = Signal(str)

	def __init__(self, show_debug_lines: bool = False):
		super().__init__()
		self.wind_rose = WindRose(show_debug_lines=show_debug_lines)
		self.wind_rose.popped_out.connect(self.popped_out)

		self.select_container = QWidget()
		self.select_layout = QHBoxLayout(self.select_container)
		self.button_group = QButtonGroup()
		self.button_group.setExclusive(True)
		self.button_group.buttonToggled.connect(self._button_toggled)

		outer_select_container = QWidget()
		outer_select_layout = QHBoxLayout(outer_select_container)
		outer_select_layout.addWidget(QLabel("WINDROSE:"))
		outer_select_layout.addWidget(self.select_container)

		outer_layout = QVBoxLayout()
		outer_layout.addWidget(self.wind_rose)
		outer_layout.addWidget(outer_select_container)

		self.setLayout(outer_layout)

	def set_data(self, reading: Reading) -> None:
		self._reading = reading

		keys = sorted([key for key in reading.wind_sensor_detail.keys() if "runway-" in key])
		titles = [key[len("runway-"):] for key in keys]

		if keys == sorted(self._keys):
			self._after_selection_changed()
			return

		self._keys = keys

		for button in self.button_group.buttons():
			self.button_group.removeButton(button)
			self.select_layout.removeWidget(button)
			button.deleteLater()

		self._selected_key = keys[0]

		for idx in range(len(keys)):
			button = QRadioButton(titles[idx])
			self.button_group.addButton(button)
			self.select_layout.addWidget(button)
			
			if idx == 0:
				button.setChecked(True)
		
	def _after_selection_changed(self) -> None:
		self.wind_rose.set_wind(self._reading.wind_sensor_detail[self._selected_key].sensor_reading)
		self.selected.emit(self._selected_key)

	def _button_toggled(self, button: QAbstractButton, checked: bool) -> None:
		if not checked:
			return
		
		id = button.text()
		self._selected_key = f"runway-{id}"
		self._after_selection_changed()
	
	def set_debug(self, debug: bool) -> None:
		self.wind_rose.set_debug(debug)

	def get_selected_key(self) -> str:
		return self._selected_key