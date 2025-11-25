import logging

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QIcon

from sensor_types import Reading
from api_calls import BatcAPI
from widgets import make_color_scheme_menu
from widgets.wind_grid import WindGrid
from widgets.wind_rose.selectable import SelectableWindRose
from widgets.many_wind_roses import ManyWindRoses
from widgets.wind_rose.popout import PopOutRose
from widgets.weather_data import WeatherData

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class MainWindow(QMainWindow):
    api = BatcAPI()
    data: Reading  | None = None

    refresh_interval = 2 * 60 * 1000 # 2 minutes
    auto_refresh = False
    show_debug = False

    _popped_out: dict[str, PopOutRose] = {}

    def __init__(self):
        super().__init__()

        self.api.setup_cookies()

        self.setWindowTitle("vBARWIS")

        self.menu = self.menuBar()
        self.barwisMenu = self.menu.addMenu("BARWIS")
        make_color_scheme_menu(self.barwisMenu, self._switch_color_scheme)

        self.debug_toggle = self.barwisMenu.addAction("Show Debug", self.toggle_debug)
        self.debug_toggle.setCheckable(True)
        self.debug_toggle.setChecked(self.show_debug)
        self.barwisMenu.addAction("Quit", self.close, QKeySequence("Ctrl+Q"))
        
        self.refreshMenu = self.menu.addMenu("Refresh")
        self.auto_refresh_action = self.refreshMenu.addAction("Automatic", self.toggle_autorefresh)
        self.auto_refresh_action.setCheckable(True)
        self.auto_refresh_action.setChecked(self.auto_refresh)
        self.refreshMenu.addAction("Refresh now", self.get_data, QKeySequence("Ctrl+R"))

        # We are going for the OG BARWIS look
        # It has 3 columns, 2 big and 1 small. Left has textual info, main wnds in text and METAR info, as well as time and date
        # Middle has a grid of wind data and below a main wind rose with large readouts. Radio buttons let you pick which one.
        # Right then has smaller wind roses for the remaining runways.
        # Ideally we tuck a feature somewhere to show forecasts, and a minimode popout with just a small wind rose for one runway

        container = QWidget()
        self.setCentralWidget(container)

        layout = QHBoxLayout(container)

        self._weather_data = WeatherData()
        layout.addWidget(self._weather_data, stretch=1)

        central_container = QWidget()
        central_layout = QVBoxLayout(central_container)
        layout.addWidget(central_container, stretch=1)

        self.wind_grid = WindGrid()
        central_layout.addWidget(self.wind_grid)

        self.status = self.statusBar()
        self.status.showMessage("Done")

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        if self.auto_refresh:
            self.timer.start(self.refresh_interval)

        self.wind_rose = SelectableWindRose(show_debug_lines=self.show_debug)
        self.wind_rose.popped_out.connect(self.pop_out)
        central_layout.addWidget(self.wind_rose)

        self.many_wind_roses = ManyWindRoses()
        self.many_wind_roses.popped_out.connect(self.pop_out)
        layout.addWidget(self.many_wind_roses, stretch=0)

        self.get_data(initial=True)
    
    def get_data(self, initial: bool = False):
        self.status.showMessage("Refreshing...")
        data = self.api.fetch_doc()
        if data is None:
            self.status.showMessage("Got no data..")
            return

        current = data.currentLabel
        self.data = self.api.get_latest_reading(data)

        if self.data is None:
            self.status.showMessage("No data after parse...")
            return

        # Loading to children
        self.wind_grid.load_data(self.data)
        self.wind_rose.set_data(self.data)
        self.many_wind_roses.set_reading(self.data)
        
        if initial:
            self.wind_rose.selected.connect(self.update_many_keys)
            keys = [key for key in self.data.wind_sensor_detail.keys() if "runway-" in key]
            keys.pop(0)
            self.many_wind_roses.set_show_keys(keys)

        for (_key, popout) in self._popped_out.items():
            popout.set_data_from(self.data)

        log.info(f"Got {len(self.data.wind_sensor_detail)}")
        self.status.showMessage(f"Done, data from {current}")

    def update_many_keys(self, selected_key: str) -> None:
        if self.data is None:
            return

        keys = [key for key in self.data.wind_sensor_detail.keys() if "runway-" in key]
        keys.remove(selected_key)
        self.many_wind_roses.set_show_keys(keys)

    def on_timer(self):
        self.get_data()

    def toggle_autorefresh(self):
        if self.auto_refresh:
            self.timer.stop()
        else:
            self.timer.start(self.refresh_interval)

        self.auto_refresh = not self.auto_refresh
        self.auto_refresh_action.setChecked(self.auto_refresh)
    
    def toggle_debug(self):
        self.show_debug = not self.show_debug
        self.debug_toggle.setChecked(self.show_debug)

        self.wind_rose.set_debug(self.show_debug)

    def pop_out(self, key: str) -> None:
        if self.data is None:
            print("Bailing popout, no data")
            return

        if key in self._popped_out.keys():
            self.status.showMessage("Already popped out")
            return

        print(f"Popping out {key}")
        popout = PopOutRose(key, self.data.wind_sensor_detail[key].sensor_reading)
        self._popped_out[key] = popout
        popout.about_to_close.connect(lambda: self._popped_out.pop(key, None))
        popout.show()

    def _switch_color_scheme(self, scheme: Qt.ColorScheme) -> None:
        print(f"Changing color to {repr(scheme)}")
        QApplication.styleHints().setColorScheme(scheme)


def main():
    app = QApplication()
    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()
