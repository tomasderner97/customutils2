import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap, QColor

__version__ = "2.0"


class Canvas(QWidget):
    """
    Canvas class for PyQt5. Every time it is redrawn, it calls update_func.
    Every redraw is complete, pixel values are not remembered between redraws.
    """

    def __init__(self,
                 width=500,
                 height=500,
                 anim_period=-1):

        super().__init__()

        self.setFixedSize(width, height)
        self.anim_period = anim_period
        self.p = QPainter()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)

        if anim_period >= 0:
            self.timer.start(anim_period)

    def timeout(self):

        self.update()

    def update_func(self):

        raise NotImplementedError("This method is abstract, you need to implement it.")

    def paintEvent(self, event):

        self.p.begin(self)
        self.update_func()
        self.p.end()


class MyCanvas(Canvas):

    def __init__(self):

        super().__init__(anim_period=5)

    def update_func(self):

        from random import random

        self.p.drawLine(int(random() * self.width()),
                        int(random() * self.height()),
                        int(random() * self.width()),
                        int(random() * self.height()),)


def main():

    app = QApplication(sys.argv)
    mc = MyCanvas()
    mc.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
