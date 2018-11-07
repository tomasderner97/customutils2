import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap, QColor

__version__ = "2.1"
# 1.0 was moved to _deprecated
# change in 2.1, renamed update_func to redraw


class Canvas(QWidget):
    """
    Canvas class for PyQt5. Every time it is redrawn, it calls self.redraw.
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

    def redraw(self):

        raise NotImplementedError("This method is abstract, you need to implement it.")

    def paintEvent(self, event):

        self.p.begin(self)
        self.redraw()
        self.p.end()


class PixmapCanvas(QWidget):
    """
    Canvas class for PyQt5. Everything is drawn on QPixmap, meaning the content is stable
    between updates.
    """

    def __init__(self,
                 width=500,
                 height=500,
                 anim_period=-1):

        super().__init__()

        self.pixmap = QPixmap(width, height)
        self.setFixedSize(width, height)

        self.anim_period = anim_period
        self.p = QPainter()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)

        if anim_period >= 0:
            self.timer.start(anim_period)

        self.p.begin(self.pixmap)
        self.init()
        self.p.end()

    def init(self):

        pass

    def redraw(self):

        raise NotImplementedError("This method is abstract, you need to implement it.")

    def background_color(self, color_name):
        """
        Deletes content of the canvas and sets background color.
        """
        activated_here = True

        if self.p.isActive():
            activated_here = False
        else:
            self.p.begin(self.pixmap)

        self.p.fillRect(0, 0, self.width(), self.height(), QColor(color_name))

        if activated_here:
            self.p.end()

    def timeout(self, *args, **kwargs):
        """
        Calls the redraw() and passes the args and kwargs.
        """
        activated_here = True

        if self.p.isActive():
            activated_here = False
        else:
            self.p.begin(self.pixmap)

        self.redraw(*args, **kwargs)
        if activated_here:
            self.p.end()
        self.update()

    def paintEvent(self, event):

        self.p.begin(self)
        self.p.drawPixmap(0, 0, self.pixmap)
        self.p.end()

    def resize(self, *args):
        """ 
        Deletes everything on canvas and sets new size.
        """
        stopped_here = False

        if self.p.isActive():
            self.p.end()
            stopped_here = True

        self.setFixedSize(*args)
        self.pixmap = QPixmap(self.width(), self.height())

        if stopped_here:
            self.p.begin(self.pixmap)
