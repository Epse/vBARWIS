from PySide6.QtGui import QPainter, QRegion, QPainterPath
from PySide6.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRect

class QGraphicsArcItem(QGraphicsEllipseItem):
	def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None:
		path = QPainterPath()
		path.addEllipse(self.rect())
		painter.setClipPath(path)
		painter.setClipping(True)
		painter.setPen(self.pen())
		painter.setBrush(self.brush())
		painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())