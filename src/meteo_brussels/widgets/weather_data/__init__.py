from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from datetime import datetime
from zoneinfo import ZoneInfo

from widgets.big_label import BigLabel


class WeatherData(QWidget):
	def __init__(self) -> None:
		super().__init__()

		self._layout = QVBoxLayout()
		self.setLayout(self._layout)

		self._layout.addWidget(Header(), stretch=0)
		self._layout.addWidget(QWidget(), stretch=1)


class Header(QWidget):
	def __init__(self) -> None:
		super().__init__()

		self._layout = QGridLayout()
		self.setLayout(self._layout)

		self._layout.addWidget(QLabel("EBBR"), 0, 0, 2, 1)
		self._layout.addWidget(QLabel("Date"), 0, 1)
		self._layout.addWidget(QLabel("Issue Time"), 0, 2)
		self._layout.addWidget(QLabel("Time"), 0, 3)

		self._date = BigLabel(scaling=1.5)
		self._layout.addWidget(self._date, 1, 1)

		self._issue_time = BigLabel(scaling=1.5)
		self._layout.addWidget(self._issue_time, 1, 2)

		self._time = BigLabel(scaling=1.5)
		self._layout.addWidget(self._time, 1, 3)

		self._timer = QTimer()
		self._timer.start(1000) # Once a second
		self._timer.timeout.connect(self._on_timer)

		self._on_timer()

	def _on_timer(self) -> None:
		now = datetime.now().astimezone(ZoneInfo("UTC"))

		self._date.setText(now.strftime("%d%m%y"))

		self._issue_time.setText("Unknown") # TODO update to actual issue time
		self._time.setText(now.strftime("%H%MUTC"))