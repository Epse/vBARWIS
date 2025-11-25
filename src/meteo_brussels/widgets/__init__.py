from typing import Callable
from PySide6.QtWidgets import QWidget, QMenuBar, QMenu, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QColor, QStyleHints, QGuiApplication
from PySide6.QtCore import Qt

from widgets.big_label import BigLabel

BLUE = QColor(26, 60, 206)
DARK_GREEN = QColor(48,103,29)

def make_color_scheme_menu(bar: QMenu, on_toggle: Callable[[Qt.ColorScheme], None]):
	menu = bar.addMenu("Dark theme")
	scheme = QGuiApplication.styleHints().colorScheme()
	follow_system = menu.addAction("Follow system", lambda: on_toggle(Qt.ColorScheme.Unknown))
	follow_system.setCheckable(True)
	follow_system.setChecked(scheme == Qt.ColorScheme.Unknown)
	dark = menu.addAction("Dark", lambda: on_toggle(Qt.ColorScheme.Dark))
	dark.setCheckable(True)
	dark.setChecked(scheme == Qt.ColorScheme.Dark)
	light = menu.addAction("Light", lambda: on_toggle(Qt.ColorScheme.Light))
	dark.setCheckable(True)
	light.setChecked(scheme == Qt.ColorScheme.Light)

class TitledBigLabel(QWidget):
	def __init__(self, scaling: float = 1.5, label: str | None = None, content: str | None = None, stretchable: bool = False) -> None:
		super().__init__()

		self._layout = QVBoxLayout()
		self._label = QLabel(text=label)
		self._big = BigLabel(scaling=scaling, text=content, stretchable=stretchable)

		self._layout.addWidget(self._label)
		self._layout.addWidget(self._big)

		self.setLayout(self._layout)

	def set_content(self, content: str) -> None:
		self._big.setText(content)

class VContainer(QWidget):
	def __init__(self, *args: QWidget) -> None:
		super().__init__()

		self._layout = QVBoxLayout()
		for w in args:
			self._layout.addWidget(w)

		self.setLayout(self._layout)

class HContainer(QWidget):
	def __init__(self, *args: QWidget) -> None:
		super().__init__()

		self._layout = QHBoxLayout()
		for (idx, w) in enumerate(args):
			if idx != len(args) - 1:
				self._layout.addWidget(w, stretch=0)
			else:
				self._layout.addWidget(w, stretch=1)

		self.setLayout(self._layout)