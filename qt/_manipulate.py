from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QHBoxLayout, QLabel, QGridLayout, QLineEdit, QMenu, QAction
import inspect
import collections
import decimal
from time import time


# noinspection PyAttributeOutsideInit
class ManipulateRowWidget(QWidget):
    valueChanged = pyqtSignal(float)
    animationStarted = pyqtSignal()
    animationStopped = pyqtSignal()
    trackingAllowed = pyqtSignal()
    trackingDisallowed = pyqtSignal()

    SLIDER_STEPS = 100
    BACKWARD_PLAY_LABEL = '\u25c0'
    FORWARD_PLAY_LABEL = '\u25b6'
    STOP_ANIMATION_LABEL = '\u25a0'
    ANIM_BUTTONS_LABEL_FONT = QFont('Arial', 14)

    def __init__(self, low, high, initial, parent=None):
        super().__init__(parent=parent)

        self.low = low
        self.high = high
        self.initial = initial
        self._value = float(initial)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.valueChanged.emit(self._value)
        # TODO value has to be fixed as one of allowed values of the slider and set to slider and value_edit

    def build_main_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.build_anim_backward_button()
        self.build_slider_widget()
        self.build_value_widget()
        self.build_anim_options_widget()
        self.build_anim_forward_button()

        layout.addWidget(self.anim_backward_button)
        layout.addWidget(self.slider_widget)
        layout.addWidget(self.value_widget)
        layout.addWidget(self.anim_options_widget)
        layout.addWidget(self.anim_forward_button)

        self.show_slider_layout()

    def build_slider_widget(self):
        self.slider_widget = QWidget(self)
        layout = QHBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.slider_widget.setLayout(layout)

        self.build_low_edit()
        self.build_slider()
        self.build_high_edit()

        layout.addWidget(self.low_edit)
        layout.addWidget(self.slider)
        layout.addWidget(self.high_edit)

    def build_value_widget(self):
        # TODO
        pass

    def build_anim_options_widget(self):
        # TODO
        pass

    def build_anim_backward_button(self):
        self.anim_backward_button = QPushButton(self.BACKWARD_PLAY_LABEL, self)

        width = self.anim_backward_button.height()
        self.anim_backward_button.setFixedSize(width, width)
        self.anim_backward_button.clicked.connect(self.handler_anim_backward_button_clicked)
        self.anim_backward_button.setFont(self.ANIM_BUTTONS_LABEL_FONT)

    def build_anim_forward_button(self):
        self.anim_forward_button = QPushButton(self.FORWARD_PLAY_LABEL, self)

        width = self.anim_forward_button.height()
        self.anim_forward_button.setFixedSize(width, width)
        self.anim_forward_button.clicked.connect(self.handler_anim_forward_button_clicked)
        self.anim_forward_button.setFont(self.ANIM_BUTTONS_LABEL_FONT)

    def build_low_edit(self):
        self.low_edit = QLineEdit(self.slider_widget)

        self.low_edit.setMaximumWidth(40)
        self.low_edit.setCursorPosition(0)
        self.low_edit.setValidator(QDoubleValidator())
        self.low_edit.editingFinished.connect(self.handler_low_edit_finished)

    def build_slider(self):
        self.slider = QSlider(Qt.Horizontal, self.slider_widget)

        self.slider.setMaximum(self.SLIDER_STEPS)
        self.slider.setTracking(False)
        self.slider.valueChanged.connect(self.handler_slider_value_changed)

    def build_high_edit(self):
        self.high_edit = QLineEdit(self.slider_widget)

        self.high_edit.setMaximumWidth(40)
        self.high_edit.setCursorPosition(0)
        self.high_edit.setValidator(QDoubleValidator())
        self.high_edit.editingFinished.connect(self.handler_high_edit_finished)

    def show_slider_widget(self):
        self.hide_widgets()
        # TODO set other widgets

    def show_value_widget(self):
        # TODO
        pass

    def show_anim_options_widget(self):
        # TODO
        pass

    def hide_widgets(self):
        self.slider_widget.hide()
        self.value_widget.hide()
        self.anim_options_widget.hide()

    def handler_anim_backward_button_clicked(self, *args):
        # TODO
        pass

    def handler_anim_forward_button_clicked(self, *args):
        # TODO
        pass

    def handler_low_edit_finished(self, *args):
        # TODO
        pass

    def handler_slider_value_changed(self, *args):
        # TODO
        pass

    def handler_high_edit_finished(self, *args):
        # TODO
        pass

    def handler_animate_every_edit_finished(self, *args):
        # TODO
        pass

    def handler_animation_period_edit_finished(self, *args):
        # TODO
        pass

    def handler_animation_period_edit_return(self, *args):
        # TODO
        pass

    def handler_backward_timeout(self, *args):
        # TODO
        pass

    def handler_forward_timeout(self, *args):
        # TODO
        pass

    def handler_context_menu_requested(self, *args):
        # TODO
        pass

    def handler_switch_widgets_action_triggered(self, *args):
        # TODO
        pass

    def handler_tracking_action_requested(self, *args):
        # TODO
        pass

    def handler_anim_options_action_triggered(self, *args):
        # TODO
        pass


class ManipulateWidget(QWidget):

    def __init__(self, target, period=50, parent=None):
        super().__init__(parent=None)

        self.target = target
        self.period = period

        self.animation_counter = 0
        self.tracking_counter = 0

        self.last_call_time = time()

        self.grid = QGridLayout(self)
        self.setLayout(self.grid)

        self.rows, self.values = self._build_rows()

        print(self.values)

    def _build_rows(self):
        names, lows, highs, initials = self.parse_signature()

        rows = []
        for i, (name, low, high, initial) in enumerate(zip(names, lows, highs, initials)):
            def handler_value_changed(val, n=name):
                self.value_changed(n, val)
                self.call()

            name_label = QLabel(name, self)
            row = ManipulateRowWidget(low, high, initial, self)
            row.valueChanged.connect(handler_value_changed)
            row.animationStarted.connect(self.handler_animation_started)
            row.animationStopped.connect(self.handler_animation_stopped)
            row.trackingAllowed.connect(self.handler_tracking_allowed)
            row.trackingDisallowed.connect(self.handler_tracking_disallowed)
            self.grid.addWidget(name_label, i, 0, alignment=Qt.AlignRight)
            self.grid.addWidget(row, i, 1)
            rows.append(row)

        return rows, {n: i for n, i in zip(names, initials)}

    def value_changed(self, name, value):
        self.values[name] = value

    def parse_signature(self):
        signature = inspect.signature(self.target)
        params = signature.parameters
        names = list(params)
        lows = []
        highs = []
        initials = []

        for param in params.values():
            default = param.default

            if isinstance(default, collections.Sequence):

                if len(default) == 2 and default[0] < default[1]:
                    lows.append(default[0])
                    highs.append(default[1])
                    initials.append(default[0])
                elif len(default) == 3 and default[0] <= default[2] <= default[1]:
                    lows.append(default[0])
                    highs.append(default[1])
                    initials.append(default[2])
                else:
                    raise ValueError("Unable to parse such arguments")
            else:
                lows.append(0)
                highs.append(1)
                initials.append(0)

        return names, lows, highs, initials

    def call(self):
        if self.animation_counter or self.tracking_counter:
            if time() - self.last_call_time < self.period:
                print("animation running or tracking allowed, skipping")
                return

        self.target(**self.values)

    def handler_animation_started(self):
        self.animation_counter += 1

    def handler_animation_stopped(self):
        self.animation_counter -= 1

    def handler_tracking_allowed(self):
        self.tracking_counter += 1

    def handler_tracking_disallowed(self):
        self.tracking_counter -= 1
