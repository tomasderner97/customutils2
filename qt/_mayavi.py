import sys
import os
os.environ["ETS_TOOLKIT"] = "qt4"
os.environ["QT_API"] = "pyqt5"

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

from matplotlib import colors as mplcolors

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor


class MayaviWidget(QWidget):
    """
    Qt widget wrapping a mayavi (mlab) scene. It has a timer, controlled by self.start_timer() and
    self.stop_timer(). It calls the self.timeout(frame: int) function. When self.timeout(frame) 
    is called for the first time, frame has a value 1, frame 0 should be called manually from the
    constructor (see usage). 
    This widget also contains mayavi toolbar, the height of which is not counted in height param.
    mlab is exposed as self.mlab, but it is possible to use mlab imported straight from mayavi.

    self.timeout(frame: int) must be reimplemented in child class!

    Parameters
    ----------
    parent : QWidget, default None
        Qt parent of this widget
    width, height : int
        Width and height of the scene (excluding the toolbar). 

    Usage
    -----

    class MayaviVisualization(MayaviWidget):

        def __init__(self):

            super().__init__(width, height)

            # preparation of useful objects and mlab elements, actual drawing should be done in
            # self.timeout()

            self.timeout(0)  # draw initial frame

        def timeout(self, frame):

            # drawing

    # usage of inherited class:

    app = QApplication(sys.argv)

    mv = MayaviVisualization()
    mv.start_timer(period)  # optional for animations
    mv.show()

    sys.exit(app.exec())

    // alternative use for static figure:

    mw = MayaviWidget(params)
    mw.mlab.something() // drawing
    qt_app(mw)

    """

    def __init__(self, parent=None, width=500, height=500, bgcolor=None, fgcolor=None):

        super().__init__()

        self.scene = self._make_visualization(width, height)

        self._prepare_layout()

        self.mlab = self.scene.scene.mlab

        self.set_figure_colors(bgcolor, fgcolor)

        self.timer = QTimer(self)

    def _make_visualization(self, width, height):

        class Visualization(HasTraits):

            scene = Instance(MlabSceneModel, ())
            view = View(Item('scene',
                             width=width,
                             height=height,
                             show_label=False,
                             editor=SceneEditor(scene_class=MayaviScene)),
                        resizable=True)

        return Visualization()

    def _prepare_layout(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scene_widget = self.scene.edit_traits(parent=self,
                                                   kind="subpanel").control
        self.scene_widget.setParent(self)
        layout.addWidget(self.scene_widget)

    def set_figure_colors(self, bgcolor=None, fgcolor=None):

        bgcolor = self._str_color_to_tuple(bgcolor)
        fgcolor = self._str_color_to_tuple(fgcolor)

        self.mlab.figure(self.mlab.gcf(), bgcolor=bgcolor, fgcolor=fgcolor)

    def _str_color_to_tuple(self, color):

        if isinstance(color, str):
            if color in mplcolors.BASE_COLORS.keys():
                return mplcolors.BASE_COLORS[color]
            elif color in mplcolors.CSS4_COLORS.keys():
                return mplcolors.to_rgb(mplcolors.CSS4_COLORS[color])
            else:
                raise ValueError("Invalid color identifier.")
        else:
            return color

    def start_timer(self, period):

        self._frame_counter = 0

        def anim():

            self._frame_counter += 1
            self.timeout(self._frame_counter)

        self.timer.timeout.connect(anim)
        self.timer.start(period)

    def stop_timer(self):

        self.timer.stop()

    def reset_timer(self):
        """
        Sets frame counter to zero (-1, the variable is incremented once before next timeout).
        """

        self._frame_counter = -1

    def timeout(self, frame):

        raise NotImplementedError("You need to reimplement this method or connect another function")


def main():

    app = QApplication(sys.argv)
    w = MayaviWidget(width=500, height=500, bgcolor="w")

    w.mlab.test_contour3d()

    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
