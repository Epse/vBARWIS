import logging

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence

from sensor_types import Reading
from api_calls import BatcAPI
from widgets.wind_grid import WindGrid
from widgets.wind_rose import WindRose

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class MainWindow(QMainWindow):
    api = BatcAPI()
    data: Reading  | None = None

    refresh_interval = 2 * 60 * 1000 # 2 minutes
    auto_refresh = False
    show_debug = False

    def __init__(self):
        super().__init__()

        self.api.setup_cookies()

        self.setWindowTitle("vBARWIS")
        #self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        #self.setWindowFlag(Qt.WindowType.Tool) # Gives it a smaller titlebar, and no taskbar entry, but also makes it not fully quit when window is closed...

        self.menu = self.menuBar()
        self.barwisMenu = self.menu.addMenu("BARWIS")
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

        self.wind_grid = WindGrid()
        layout.addWidget(self.wind_grid)

        self.status = self.statusBar()
        self.status.showMessage("Done")

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        if self.auto_refresh:
            self.timer.start(self.refresh_interval)

        self.wind_rose = WindRose(show_debug_lines=self.show_debug)
        layout.addWidget(self.wind_rose)

        self.get_data()
    
    def get_data(self):
        self.status.showMessage("Refreshing...")
        data = self.api.fetch_doc()
        if data is None:
            self.status.showMessage("Got no data..")
            return

        current = data['data']['currentLabel']
        self.data = self.api.get_latest_reading(data)

        if self.data is None:
            self.status.showMessage("No data after parse...")
            return

        # Loading to children
        self.wind_grid.load_data(self.data)
        main_wind_key = "runway-25R" # TODO configurable
        main_wind_sensor = self.data.wind_sensor_detail[main_wind_key].sensor_reading
        self.wind_rose.set_wind(main_wind_sensor.wind_direction, main_wind_sensor.wind_direction_deviation_left, main_wind_sensor.wind_direction_deviation_right)

        log.info(f"Got {len(self.data.wind_sensor_detail)}")
        self.status.showMessage(f"Done, data from {current}")

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


def main():
    app = QApplication()
    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()
