import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QApplication, QSizePolicy, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt

__version__ = "2.0"

matplotlib.use("Qt5Agg")


class MatplotlibWidget(QWidget):
    """
    QWidget wrapping a matplotlib figure. Figure can only be set in constructor.
    Figure is exposed as self.fig.

    Parameters
    ----------
    parent : QWidget, default None
        Qt parent of this widget
    fig : Figure, default None
        Figure to show
    toolbar : None, "up" or "down"
    """

    def __init__(self,
                 fig,
                 toolbar=None,
                 parent=None):

        if not fig:
            raise ValueError("fig must be provided.")

        if toolbar not in [None, "up", "down"]:
            raise ValueError("toolbar must be None, 'up' or 'down'.")

        super().__init__()
        self.setParent(parent)

        self._fig = fig

        self._vbox = QVBoxLayout(self)
        self.setLayout(self._vbox)
        # self.setContentsMargins(0, 0, 0, 0)  # shouldn't be necessary
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)

        self._figure_canvas = FigureCanvas(self._fig)
        self._figure_canvas.setParent(self)
        self._figure_canvas.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Expanding)

        if toolbar == "up":
            self._vbox.addWidget(NavigationToolbar(self._figure_canvas, self))

        self._vbox.addWidget(self._figure_canvas)

        if toolbar == "down":
            self._vbox.addWidget(NavigationToolbar(self._figure_canvas, self))

    # properties ax, axs, fig are read only
    @property
    def ax(self):
        return self._ax

    @property
    def axs(self):
        return self._axs

    @property
    def fig(self):
        return self._fig
