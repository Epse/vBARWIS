from typing import cast
from PySide6.QtWidgets import QSizePolicy, QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout, QGraphicsEllipseItem, QLabel, QHBoxLayout, QButtonGroup, QAbstractButton, QRadioButton
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QPalette, QPen, QRegion, QResizeEvent
from PySide6.QtCore import QLocale, QPoint, QRect, QSize, Qt, QLineF
from . import WindRose
from sensor_types import Reading

class SelectableWindRose(QWidget):
	reading: Reading
	selected_key: str

	def __init__(self, show_debug_lines: bool = False):
		super().__init__()
		self.wind_rose = WindRose(show_debug_lines=show_debug_lines)

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
		self.reading = reading

		for button in self.button_group.buttons():
			self.button_group.removeButton(button)
			self.select_layout.removeWidget(button)
			button.deleteLater()

		keys = [key for key in reading.wind_sensor_detail.keys() if "runway-" in key]
		titles = [key[len("runway-"):] for key in keys]

		self.selected_key = keys[0]

		for idx in range(len(keys)):
			button = QRadioButton(titles[idx])
			self.button_group.addButton(button)
			self.select_layout.addWidget(button)
			
			if idx == 0:
				button.setChecked(True)

		self._after_selection_changed()
		
	def _after_selection_changed(self) -> None:
		self.wind_rose.set_wind(self.reading.wind_sensor_detail[self.selected_key].sensor_reading)

	def _button_toggled(self, button: QAbstractButton, checked: bool) -> None:
		if not checked:
			return
		
		id = button.text()
		self.selected_key = f"runway-{id}"
		self._after_selection_changed()
	
	def set_debug(self, debug: bool) -> None:
		self.wind_rose.set_debug(debug)