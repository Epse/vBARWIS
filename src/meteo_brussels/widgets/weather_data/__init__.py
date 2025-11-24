from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from widgets.big_label import BigLabel


class WeatherData(QWidget):
	def __init__(self) -> None:
		super().__init__()

		self._layout = QVBoxLayout()
		self.setLayout(self._layout)
