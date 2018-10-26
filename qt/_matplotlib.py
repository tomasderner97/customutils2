import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QApplication, QSizePolicy

matplotlib.use("Qt5Agg")


class MatplotlibWidget(FigureCanvas):

    def __init__(self,
                 parent=None,
                 fig=None,
                 ax=None,
                 width=0,
                 height=0,
                 dpi=0,
                 tight_layout=False):

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

        FigureCanvas.__init__(self, self._fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    @property
    def ax(self):

        return self._ax

    @property
    def axs(self):

        return self._axs

    @property
    def fig(self):

        return self._fig


def main():

    fig, axs = plt.subplots(2, 1)
    axs[0].plot([1, 3, 2])
    axs[1].plot([2, 1, 3])

    app = QApplication(sys.argv)
    mw = MatplotlibWidget(fig=fig, ax=axs, tight_layout=True)
    mw.ax.plot([3, 2, 1])
    mw.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
