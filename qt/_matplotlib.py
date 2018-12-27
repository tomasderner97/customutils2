import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QApplication, QSizePolicy, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt

matplotlib.use("Qt5Agg")


class MatplotlibWidget(QWidget):

    """
    QWidget wrapping a matplotlib figure. It has a timer, controlled by self.start_timer() and
    self.stop_timer(). It calls the self.timeout(frame: int) function. When self.timeout(frame) 
    is called for the first time, frame has a value 1, frame 0 should be called manually from the
    constructor (see usage). 

    Figure is exposed as self.fig, self.ax. Main Axes is in self.ax, all axes are in self.axs.

    Parameters
    ----------
    parent : QWidget, default None
        Qt parent of this widget
    fig : Figure, default None
        Figure to show
    ax : Axes, default None
        Axes belonging to fig
    width, height : int, default is figsize in rcParams or size of fig
        Width and height of the widget (in pixels)
    dpi : int, default is value in rcParams
        Dots per inch of the figure
    tight_layout : bool, default False
        if true, call self.fig.tight_layout()
    toolbar : bool, default False
        if true, show matplotlib toolbar

    Usage
    -----

    # TODO
    """

    def __init__(self,
                 parent=None,
                 fig=None,
                 ax=None,
                 width=0,
                 height=0,
                 dpi=0,
                 tight_layout=False,
                 toolbar=False):

        super().__init__()
        self.setParent(parent)

        self._prepare_matplotlib_stuff(fig, ax, width, height, dpi, tight_layout)
        self._prepare_layout(toolbar)

        self.timer = QTimer(self)

    def _prepare_matplotlib_stuff(self, fig, ax, width, height, dpi, tight_layout):

        if not dpi:
            dpi = matplotlib.rcParams["figure.dpi"]

        if fig:
            self._fig = fig

            if ax is None:
                raise AttributeError("You can not pass figure without axes.")

            # _ax contains main axes (placed first in ax list), _axs has all axes
            try:
                self._ax = ax[0]
                self._axs = ax
            except TypeError:
                self._ax = ax
                self._axs = [ax]

        else:
            self._fig = Figure(figsize=matplotlib.rcParams["figure.figsize"], dpi=dpi)
            self._ax = self._fig.add_subplot(111)
            self._axs = [self._ax]

        if not width:
            width = matplotlib.rcParams["figure.figsize"][0] * dpi
        if not height:
            height = matplotlib.rcParams["figure.figsize"][1] * dpi

        if width or height:
            self._fig.set_size_inches(width / dpi, height / dpi)

        if tight_layout:
            self._fig.tight_layout()

    def _prepare_layout(self, toolbar):

        self._vbox = QVBoxLayout(self)
        self.setLayout(self._vbox)
        self.setContentsMargins(0, 0, 0, 0)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)

        self._figure_canvas = FigureCanvas(self._fig)
        self._figure_canvas.setParent(self)
        self._figure_canvas.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Expanding)

        if toolbar:
            self._vbox.addWidget(NavigationToolbar(self._figure_canvas, self))

        self._vbox.addWidget(self._figure_canvas)

    @property
    def ax(self):

        return self._ax

    @property
    def axs(self):

        return self._axs

    @property
    def fig(self):

        return self._fig

    def start_timer(self, period):
        """
        Starts self.timer with given period. It calls self.timeout, which must be defined.
        It passes frame count to timeout. The count can be reset with self.reset_timer.
        """

        self._frame_counter = 0

        def anim():

            self._frame_counter += 1
            self.timeout(self._frame_counter)

        self.timer.timeout.connect(anim)
        self.timer.start(period)

    def stop_timer(self):
        """
        Stops the timer.
        """

        self.timer.stop()

    def reset_timer(self):
        """
        Sets frame counter to zero (-1, the variable is incremented once before next timeout).
        """

        self._frame_counter = -1

    def timeout(self, frame):
        """
        Callback method for self.timer. Is abstract, gets frame count.
        """

        raise NotImplementedError("You need to reimplement this method or connect another function")
