from PySide6.QtWidgets import QLabel, QApplication, QFrame, QWidget, QHBoxLayout

class BigLabel(QLabel):
	def __init__(self, scaling: float = 2.0, text: str | None = None) -> None:
		super().__init__(text=text)
		self._scaling = scaling

		font = QApplication.font()
		font.setPointSizeF(font.pointSizeF() * self._scaling)
		self.setFont(font)
		
		self.setStyleSheet("padding: 2px;")

		self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
		self.setLineWidth(1)


class BigLabelMin(QWidget):
	def __init__(self, scaling: float = 2.0, text: str | None = None) -> None:
		super().__init__()

		self._label = BigLabel(scaling=scaling, text=text)
		self._layout = QHBoxLayout()
		self.setLayout(self._layout)
		self._layout.addWidget(self._label, stretch=0)
		self._layout.addStretch()

	def setText(self, text: str) -> None:
		self._label.setText(text)