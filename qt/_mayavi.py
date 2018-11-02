import sys
import os
os.environ["ETS_TOOLKIT"] = "qt4"
os.environ["QT_API"] = "pyqt5"

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor


class MayaviWidget(QWidget):

    def __init__(self, parent=None, width=500, height=500):

        super().__init__()

        self.scene = self._make_visualization(width, height)

        self._prepare_layout()

        self.mlab = self.scene.scene.mlab

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

    def start_timer(self, period):

        self._frame_counter = 0

        def anim():

            self._frame_counter += 1
            self.timeout(self._frame_counter)

        self.timer.timeout.connect(anim)
        self.timer.start(period)

    def stop_timer(self):

        self.timer.stop()

    def timeout(self, frame):

        raise NotImplementedError("You need to reimplement this method or connect another function")


def main():

    app = QApplication(sys.argv)
    w = MayaviWidget(width=500, height=500)

    w.mlab.test_contour3d()

    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
