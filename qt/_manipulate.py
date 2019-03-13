from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QHBoxLayout, QLabel, QGridLayout, QLineEdit, QMenu, QAction, \
    QVBoxLayout
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
    PLAY_BACKWARD_LABEL = '\u25c0'
    PLAY_FORWARD_LABEL = '\u25b6'
    STOP_ANIMATION_LABEL = '\u25a0'
    ANIM_BUTTONS_LABEL_FONT = QFont('Arial', 14)

    def __init__(self, low, high, initial, parent=None):
        super().__init__(parent=parent)

        self.low = low
        self.high = high
        self.initial = initial
        self._value = 0

        self.anim_step = 1
        self.anim_period = 100
        self.adjust_slider_step_size()

        self.timer_backward = QTimer(self)
        self.timer_backward.timeout.connect(self.handler_backward_timeout)
        self.timer_forward = QTimer(self)
        self.timer_forward.timeout.connect(self.handler_forward_timeout)

        self.build_main_layout()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.handler_context_menu_requested)

        self.set_value(float(initial))

    def get_value(self):
        return self._value

    def set_value(self, val):
        slider_steps_fraction = (val - self.low) / self.slider_step_size
        if slider_steps_fraction.is_integer():
            slider_steps = int(slider_steps_fraction)
        else:
            slider_steps = int(decimal.Decimal(slider_steps_fraction).quantize(1, rounding=decimal.ROUND_HALF_UP))

        if slider_steps < 0:
            slider_steps = 0
        elif slider_steps > self.SLIDER_STEPS:
            slider_steps = self.SLIDER_STEPS

        self.slider.setValue(slider_steps)

        self.set_value_from_slider_steps(slider_steps)

    def set_value_from_slider_steps(self, steps):
        val = self.low + self.slider_step_size * steps

        self.value_edit.setText(self.format_number(val))
        if self._value != val:
            self._value = val
            self.valueChanged.emit(self._value)

    def adjust_slider_step_size(self):
        self.slider_step_size = (self.high - self.low) / self.SLIDER_STEPS

    def format_number(self, val):
        if isinstance(val, int) or val.is_integer():
            return str(int(val))

        string = f"{val:.14f}".rstrip("0")
        if string[-1] == '.':
            string += "0"
        return string

    def move_slider_left(self, steps):
        current = self.slider.value()
        self.slider.setValue((current - steps) % self.SLIDER_STEPS)

    def move_slider_right(self, steps):
        current = self.slider.value()
        self.slider.setValue((current + steps) % self.SLIDER_STEPS)

    def start_backward_animation(self):
        if self.timer_forward.isActive() or self.timer_backward.isActive():
            return
        self.timer_backward.start(self.anim_period)
        self.animationStarted.emit()
        self.anim_backward_button.setText(self.STOP_ANIMATION_LABEL)
        self.anim_forward_button.setEnabled(False)

    def stop_backward_animation(self):
        if self.timer_backward.isActive():
            self.timer_backward.stop()
            self.animationStopped.emit()
            self.anim_backward_button.setText(self.PLAY_BACKWARD_LABEL)
            self.anim_forward_button.setEnabled(True)

    def start_forward_animation(self):
        if self.timer_backward.isActive() or self.timer_forward.isActive():
            return
        self.timer_forward.start(self.anim_period)
        self.animationStarted.emit()
        self.anim_forward_button.setText(self.STOP_ANIMATION_LABEL)
        self.anim_backward_button.setEnabled(False)

    def stop_forward_animation(self):
        if self.timer_forward.isActive():
            self.timer_forward.stop()
            self.animationStopped.emit()
            self.anim_forward_button.setText(self.PLAY_FORWARD_LABEL)
            self.anim_backward_button.setEnabled(True)

    def disable_animations(self):
        self.anim_backward_button.setEnabled(False)
        self.anim_forward_button.setEnabled(False)
        self.anim_backward_button.setText(self.PLAY_BACKWARD_LABEL)
        self.anim_forward_button.setText(self.PLAY_FORWARD_LABEL)
        self.timer_backward.stop()
        self.timer_forward.stop()

    def enable_animations(self):
        if self.timer_forward.isActive() or self.timer_backward.isActive():
            return
        self.anim_backward_button.setEnabled(True)
        self.anim_forward_button.setEnabled(True)

    def build_main_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.build_anim_backward_button()
        self.build_step_backward_button()
        self.build_slider_widget()
        self.build_value_widget()
        self.build_anim_options_widget()
        self.build_step_forward_button()
        self.build_anim_forward_button()

        layout.addWidget(self.anim_backward_button)
        layout.addWidget(self.step_backward_button)
        layout.addWidget(self.slider_widget)
        layout.addWidget(self.value_widget)
        layout.addWidget(self.anim_options_widget)
        layout.addWidget(self.step_forward_button)
        layout.addWidget(self.anim_forward_button)

        self.show_slider_widget()

    def build_slider_widget(self):
        self.slider_widget = QWidget(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.slider_widget.setLayout(layout)

        self.build_low_edit()
        self.build_slider()
        self.build_high_edit()

        layout.addWidget(self.low_edit)
        layout.addWidget(self.slider)
        layout.addWidget(self.high_edit)

    def build_value_widget(self):
        self.value_widget = self.value_edit = QLineEdit(self)

        self.value_edit.setValidator(QDoubleValidator())
        self.value_edit.editingFinished.connect(self.handler_value_edit_finished)

    def build_anim_options_widget(self):
        self.anim_options_widget = QWidget(self)
        layout = QHBoxLayout(self.anim_options_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.anim_options_widget.setLayout(layout)

        step_label = QLabel("Step:", self.anim_options_widget)
        period_label = QLabel("Period:", self.anim_options_widget)

        self.build_animation_step_edit()
        self.build_animation_period_edit()

        layout.addWidget(step_label)
        layout.addWidget(self.animation_step_edit)
        layout.addWidget(period_label)
        layout.addWidget(self.animation_period_edit)

    def build_anim_backward_button(self):
        self.anim_backward_button = QPushButton(self.PLAY_BACKWARD_LABEL, self)

        width = self.anim_backward_button.height()
        self.anim_backward_button.setFixedSize(width, width)
        self.anim_backward_button.clicked.connect(self.handler_anim_backward_button_clicked)
        self.anim_backward_button.setFont(self.ANIM_BUTTONS_LABEL_FONT)

    def build_step_backward_button(self):
        self.step_backward_button = QPushButton("<", self)

        width = self.step_backward_button.height()
        self.step_backward_button.setFixedSize(width, width)
        self.step_backward_button.clicked.connect(self.handler_step_backward_button_clicked)

    def build_step_forward_button(self):
        self.step_forward_button = QPushButton(">", self)

        width = self.step_forward_button.height()
        self.step_forward_button.setFixedSize(width, width)
        self.step_forward_button.clicked.connect(self.handler_step_forward_button_clicked)

    def build_anim_forward_button(self):
        self.anim_forward_button = QPushButton(self.PLAY_FORWARD_LABEL, self)

        width = self.anim_forward_button.height()
        self.anim_forward_button.setFixedSize(width, width)
        self.anim_forward_button.clicked.connect(self.handler_anim_forward_button_clicked)
        self.anim_forward_button.setFont(self.ANIM_BUTTONS_LABEL_FONT)

    def build_low_edit(self):
        self.low_edit = QLineEdit(self.format_number(self.low), self.slider_widget)

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
        self.high_edit = QLineEdit(self.format_number(self.high), self.slider_widget)

        self.high_edit.setMaximumWidth(40)
        self.high_edit.setCursorPosition(0)
        self.high_edit.setValidator(QDoubleValidator())
        self.high_edit.editingFinished.connect(self.handler_high_edit_finished)

    def build_animation_step_edit(self):
        self.animation_step_edit = QLineEdit(str(self.anim_step), self.anim_options_widget)

        self.animation_step_edit.setMaximumWidth(30)
        self.animation_step_edit.editingFinished.connect(self.handler_animation_step_edit_finished)
        self.animation_step_edit.setValidator(QIntValidator())

    def build_animation_period_edit(self):
        self.animation_period_edit = QLineEdit(str(self.anim_period), self.anim_options_widget)

        self.animation_period_edit.setMinimumWidth(20)
        self.animation_period_edit.editingFinished.connect(self.handler_animation_period_edit_finished)
        self.animation_period_edit.returnPressed.connect(self.handler_animation_period_edit_return)
        self.animation_period_edit.setValidator(QIntValidator())

    def show_slider_widget(self):
        self.hide_widgets()
        self.slider_widget.show()
        self.enable_animations()

    def show_value_widget(self):
        self.hide_widgets()
        self.value_widget.show()
        self.enable_animations()
        self.window().setFocus()

    def show_anim_options_widget(self):
        self.hide_widgets()
        self.anim_options_widget.show()
        self.disable_animations()
        self.animation_step_edit.setFocus()

    def hide_widgets(self):
        self.slider_widget.hide()
        self.value_widget.hide()
        self.anim_options_widget.hide()

    def handler_anim_backward_button_clicked(self, *args):
        if self.timer_backward.isActive():
            self.stop_backward_animation()
        else:
            self.start_backward_animation()

    def handler_anim_forward_button_clicked(self, *args):
        if self.timer_forward.isActive():
            self.stop_forward_animation()
        else:
            self.start_forward_animation()

    def handler_step_backward_button_clicked(self, *args):
        self.move_slider_left(1)

    def handler_step_forward_button_clicked(self, *args):
        self.move_slider_right(1)

    def handler_low_edit_finished(self, *args):
        current = float(self.low_edit.text())
        if current < self.high:
            self.low = current
            self.adjust_slider_step_size()
            self.set_value(self.get_value())

        self.low_edit.setText(self.format_number(self.low))
        self.window().setFocus()

    def handler_slider_value_changed(self, *args):
        print("slider")
        steps = self.slider.value()
        self.set_value_from_slider_steps(steps)

    def handler_high_edit_finished(self, *args):
        current = float(self.high_edit.text())
        if current > self.low:
            self.high = current
            self.adjust_slider_step_size()
            self.set_value(self.get_value())

        self.high_edit.setText(self.format_number(self.high))
        self.window().setFocus()

    def handler_value_edit_finished(self, *args):
        print("value_edit")
        self.set_value(float(self.value_edit.text()))
        self.window().setFocus()

    def handler_animation_step_edit_finished(self, *args):
        current = int(self.animation_step_edit.text())
        if current < self.SLIDER_STEPS // 2:
            self.anim_step = current
        self.animation_step_edit.setText(str(self.anim_step))
        self.animation_period_edit.setFocus()

    def handler_animation_period_edit_finished(self, *args):
        current = int(self.animation_period_edit.text())
        if current < 0:
            self.animation_period_edit.setText(str(self.animation_period))
        else:
            self.anim_period = current

    def handler_animation_period_edit_return(self, *args):
        self.show_slider_widget()

    def handler_backward_timeout(self, *args):
        self.move_slider_left(self.anim_step)

    def handler_forward_timeout(self, *args):
        self.move_slider_right(self.anim_step)

    def handler_context_menu_requested(self, pos):
        menu = QMenu(self)

        switch_widgets_action = QAction(self)
        if self.slider_widget.isHidden():
            switch_widgets_action.setText("Show slider")
        else:
            switch_widgets_action.setText("Show value")
        switch_widgets_action.triggered.connect(self.handler_switch_widgets_action_triggered)

        anim_options_action = QAction("Animation options", self)
        anim_options_action.triggered.connect(self.handler_anim_options_action_triggered)

        tracking_action = QAction(self)
        if self.slider.hasTracking():
            tracking_action.setText("Turn tracking off")
        else:
            tracking_action.setText("Turn tracking on")
        tracking_action.triggered.connect(self.handler_tracking_action_triggered)

        menu.addActions([switch_widgets_action, anim_options_action, tracking_action])
        menu.exec(self.mapToGlobal(pos))

    def handler_switch_widgets_action_triggered(self, *args):
        if self.slider_widget.isHidden():
            self.show_slider_widget()
        else:
            self.show_value_widget()

    def handler_tracking_action_triggered(self, *args):
        if self.slider.hasTracking():
            self.slider.setTracking(False)
            self.trackingDisallowed.emit()
        else:
            self.slider.setTracking(True)
            self.trackingAllowed.emit()

    def handler_anim_options_action_triggered(self, *args):
        self.show_anim_options_widget()


class ManipulateWidget(QWidget):

    def __init__(self, target, period=50, parent=None):
        super().__init__(parent=None)

        self.target = target
        self.period = period

        self.animation_counter = 0
        self.tracking_counter = 0

        self.last_call_time = time()

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
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
            t = time()
            if t - self.last_call_time < self.period / 1000:
                print("animation running or tracking allowed, skipping")
                return
            self.last_call_time = t

        self.target(**self.values)

    def handler_animation_started(self):
        self.animation_counter += 1

    def handler_animation_stopped(self):
        self.animation_counter -= 1

    def handler_tracking_allowed(self):
        self.tracking_counter += 1

    def handler_tracking_disallowed(self):
        self.tracking_counter -= 1


def manipulate(widget, target, period=50, tight=True):
    """
    Helper function meant to construct a window with a manipulate widget quickly.
    Intended usage:
    qt_app(manipulate(target, widget))

    :param widget: The interesting widget to be controlled by the manipulate widget
    :param target: Target function called by ManipulateWidget
    :param period: Minimum waiting time before sequential calls of target when animation or tracking is active
    :param tight: if true, context margins of the window are set to zero
    :return: constructed wrapping qwidget
    """
    window = QWidget()
    layout = QVBoxLayout(window)
    window.setLayout(layout)
    layout.addWidget(widget)

    manip = ManipulateWidget(target, period=period, parent=window)
    layout.addWidget(manip)

    if tight:
        manip.setContentsMargins(10, 0, 10, 10)
        layout.setContentsMargins(0, 0, 0, 0)

    def key_pressed(e):
        widget.keyPressEvent(e)

    window.keyPressEvent = key_pressed
    manip.call()
    window.setFocus()

    return window
