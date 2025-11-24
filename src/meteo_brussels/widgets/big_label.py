from PySide6.QtWidgets import QLabel, QApplication, QFrame, QWidget, QHBoxLayout, QSizePolicy

class BigLabel(QLabel):
	_scaling: float = 2.0
	def __init__(self, scaling: float = 2.0, text: str | None = None) -> None:
		super().__init__(text=text)
		self._scaling = scaling

		font = QApplication.font()
		font.setPointSizeF(font.pointSizeF() * self._scaling)
		self.setFont(font)

		self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
		self.setLineWidth(1)

		self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
	