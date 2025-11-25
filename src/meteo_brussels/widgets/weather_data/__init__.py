import math
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout
from datetime import datetime
from zoneinfo import ZoneInfo
from metar import Metar

from widgets import HContainer, TitledBigLabel
from widgets.big_label import BigLabel
from sensor_types import MeteoDocument
from api_calls import MetarAPI


class WeatherData(QWidget):
	_data: MeteoDocument
	_metar: Metar.Metar | None = None
	_api = MetarAPI()

	def __init__(self) -> None:
		super().__init__()

		self._layout = QVBoxLayout()
		self.setLayout(self._layout)

		# Needs Header, Wind, RVR, rest of the METAR, supplementary
		self._header = Header()
		self._layout.addWidget(self._header, stretch=0)

		self._visibility = TitledBigLabel(label="Vis")
		self._weather = TitledBigLabel(label="Weather", stretchable=True)
		self._layout.addWidget(HContainer(self._visibility, self._weather))
		self._clouds = TitledBigLabel(label="Clouds", stretchable=True)
		self._layout.addWidget(self._clouds)

		self._numbers = MetarNumbers()
		self._layout.addWidget(self._numbers)

		self._layout.addWidget(QWidget(), stretch=1)

		self._timer = QTimer()
		self._timer.timeout.connect(self._refresh_metar)
		self._timer.start(60 * 1000)

		self._refresh_metar()

	def _refresh_metar(self) -> None:
		metar_text = self._api.get("EBBR")
		if not metar_text:
			return

		self._metar = Metar.Metar(metar_text)
		self._header.set_issue_time(self._metar.time)

		if self._metar.vis:
			self._visibility.set_content(f"{self._metar.vis.value('km')}KM")
		else:
			self._visibility.set_content("???")

		self._weather.set_content(self._metar.present_weather())
		self._clouds.set_content(self._metar.sky_conditions())
		self._numbers.set_metar(self._metar)


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

		self._issue_time = BigLabel(scaling=1.5, text="Unknown")
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

		self._time.setText(now.strftime("%H%MUTC"))

	def set_issue_time(self, time: datetime | None) -> None:
		if not time:
			self._issue_time.setText("Unknown")
			return

		# TODO make it orange when its more than 20min ago or so
		self._issue_time.setText(time.strftime("%H%MUTC"))

class MetarNumbers(QWidget):
	def __init__(self) -> None:
		super().__init__()

		self._layout = QHBoxLayout()

		self._temp = TitledBigLabel(label="T")
		self._layout.addWidget(self._temp)
		self._dew = TitledBigLabel(label="DP")
		self._layout.addWidget(self._dew)
		self._hum = TitledBigLabel(label="RH")
		self._layout.addWidget(self._hum)
		self._tb = TitledBigLabel(label="TB")
		self._layout.addWidget(self._tb)
		self._qnh = TitledBigLabel(label="QNH", scaling=2.0, stretchable=True)
		self._layout.addWidget(self._qnh)

		self.setLayout(self._layout)

	def set_metar(self, metar: Metar.Metar) -> None:
		if t := metar.temp:
			self._temp.set_content(t.string("C") or "")
		else:
			self._temp.set_content("")

		if metar.dewpt:
			self._dew.set_content(metar.dewpt.string("C") or "")
		else:
			self._dew.set_content("")

		if metar.dewpt and metar.temp:
			d = metar.dewpt.value("c")
			t = metar.temp.value("c")
			rh = math.nan

			if d and t:
				rh = _relative_humidity(t, d)

				self._hum.set_content(f"{rh:.0f}%")
			else:
				self._hum.set_content("??")
		else:
			self._hum.set_content("??")

		if metar.press:
			if p := metar.press.string("hPa"):
				self._qnh.set_content(p)
			else:
				self._qnh.set_content("????")
		else:
			self._qnh.set_content("????")

def _relative_humidity(temp: float, dewp: float) -> float:
	top = 17.625 * (dewp - temp)
	bottom = 243.04 + temp - dewp
	return 100.0 * math.exp(top / bottom)