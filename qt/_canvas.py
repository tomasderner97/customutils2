import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap, QColor

__version__ = "1.0"


class Canvas(QWidget):
    """
    Canvas class for PyQt5. Every time it is redrawn, it calls update_func.
    Every redraw is complete, pixel values are not remembered between redraws.
    """

    def __init__(self,
                 width=500,
                 height=500,
                 update_func=None,
                 anim_period=-1):
        """
        Parameters
        ----------
        width : int
            Width of canvas
        height : int
            Height of canvas
        update_func : callable(c: Canvas)
            Function called on redraw
        anim_period : int
            Animation period in ms, default is -1, meaning no automatic periodic redrawing
        """

        super().__init__()

        self.setFixedSize(width, height)

        self.update_func = update_func if update_func else lambda widget: None
        self.anim_period = anim_period
        self.p = QPainter()

        self.timer = None
        if anim_period >= 0:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.timeout)
            self.timer.start(anim_period)

    def timeout(self):

        self.update()

    def paintEvent(self, event):

        self.p.begin(self)
        self.update_func(self)
        self.p.end()


class PixmapCanvas(QWidget):
    """
    Canvas class for PyQt5. Everything is drawn on QPixmap, meaning the content is stable
    between updates.
    """

    def __init__(self,
                 width=500,
                 height=500,
                 init_func=None,
                 update_func=None,
                 anim_period=-1):
        """
        Parameters
        ----------
        width : int
            Width of the canvas
        height : int
            Height of the canvas
        init_func : callable(c: PixmapCanvas)
            Init function for the canvas, is called once, painter is available (c.p)
        update_func : callable(c: PixmapCanvas, *args, **kwargs)
            This is called every time the timeout() method is called. It is called by timer
            or manually. Painter is available (c.p)
        anim_period : int
            animation period in ms, if 0, timer is not initialized
        """
        super().__init__()

        self.pixmap = QPixmap(width, height)
        self.setFixedSize(width, height)

        self.init_func = init_func if init_func else lambda widget: None
        self.update_func = update_func if update_func else lambda widget: None
        self.anim_period = anim_period
        self.p = QPainter()

        self.timer = None
        if anim_period >= 0:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.timeout)
            self.timer.start(anim_period)

        self.p.begin(self.pixmap)
        self.init_func(self)
        self.p.end()

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
        Calls the update_func() and passes the args and kwargs.
        """
        activated_here = True

        if self.p.isActive():
            activated_here = False
        else:
            self.p.begin(self.pixmap)

        self.update_func(self, *args, **kwargs)
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


def init(c: PixmapCanvas):

    c.background_color("red")
    c.counter = 0


def update(c: PixmapCanvas):

    print(c.counter)
    if c.counter == 5:
        c.resize(600, 600)
        c.background_color("blue")

    c.counter += 1


def main():

    app = QApplication(sys.argv)
    canv = PixmapCanvas(init_func=init, update_func=update, anim_period=1000)
    canv.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
