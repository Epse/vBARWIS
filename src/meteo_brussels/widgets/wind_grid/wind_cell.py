from PySide6.QtWidgets import QWidget, QLabel, QTableWidgetItem
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
from typing import Literal

class WindCell(QTableWidgetItem):
	def __init__(self, value: float, suffix_kind: Literal["RL", "TH", ""] = ""):
		self.suffix_kind = suffix_kind
		super().__init__(self._format_float(value))

		#self.setAutoFillBackground(True)

		self.setBackground(QColor.fromRgb(114, 188, 47))

		if suffix_kind == "TH" and value <= -3.0:
			self.setBackground(QColor.fromRgb(206, 189, 84))

		self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
		font = self.font()
		font.setBold(True)
		self.setFont(font)

	def _format_float(self, value: float) -> str:
		if self.suffix_kind == "":
			return f"{abs(value):.1f}"

		suffix = self.suffix_kind[0] if value < 0 else self.suffix_kind[1]

		return f"{abs(value):.1f}{suffix}"

		
