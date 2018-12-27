from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QHBoxLayout, QLabel, QGridLayout, QLineEdit, QMenu, QAction
from qt import qt_app
import inspect
import collections
import decimal
from time import time


# noinspection PyAttributeOutsideInit
class ManipulateRowWidget(QWidget):
    """
    Qt widget, row of ManipulateWidget. Contains 4 buttons (play/step backward/forward) and two exchangable
    widgets: slider_widget contains lineedits for lowest and highest values and slider, value_widget contains lineedit
    to set 'exact' value. The value set is changed to the nearest allowed value of the slider. If higher value is
    passed, highest allowed value is set, lower analogicaly.
    The two widgets are changeable by right clicking and selecting option in context menu.

    Init sets object variables, creates layouts, sets context menu, focuses window (to remove focus from lineedits),
    initializes timers for animations.
    """
    valueChanged = pyqtSignal(float)
    SLIDER_STEPS = 100
    BACKWARD_PLAY_LABEL = '\u25c0'
    FORWARD_PLAY_LABEL = '\u25b6'
    STOP_ANIMATION_LABEL = '\u25a0'

    # TODO pass self in valueChanged signal, check for animation or tracking down in something_changed
    def __init__(self, low, high, default, parent=None):
        super().__init__(parent)

        self.animation_period = 100
        self.animate_every = 1

        self.low = low
        self.high = high
        self.value = float(default)
        self.animation_period = 100

        self.create_main_layout()
        self.create_slider_layout()
        self.create_value_layout()
        self.create_anim_settings_layout()

        self.value_widget.hide()
        self.anim_settings_widget.hide()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu_requested)

        self.timer_backward = QTimer()
        self.timer_backward.timeout.connect(self.backward_timeout)
        self.timer_forward = QTimer()
        self.timer_forward.timeout.connect(self.forward_timeout)

        self.slider_value_changed(self.slider.value())

        self.window().setFocus()

    # started
    def low_edit_finished(self, *_):
        if float(self.low_edit.text()) >= self.high:
            self.low_edit.setText(str(self.low))
        self.low = float(self.low_edit.text())
        if self.low.is_integer():
            self.low = int(self.low)
        new_slider_val = self._get_closest_slider_value(self.value)
        self.slider.setValue(new_slider_val)

    # started
    def high_edit_finished(self, *_):
        if float(self.high_edit.text()) <= self.low:
            self.high_edit.setText(str(self.high))
        self.high = float(self.high_edit.text())
        if self.high.is_integer():
            self.high = int(self.high)
        new_slider_val = self._get_closest_slider_value(self.value)
        self.slider.setValue(new_slider_val)

    # started
    def backward_timeout(self):
        """
        timeout handler for backward animation
        """
        current = self.slider.value()
        self.slider.setValue((current - self.animate_every) % self.SLIDER_STEPS)

    # started
    def forward_timeout(self):
        """
        timeout handler for forward animation
        """
        current = self.slider.value()
        self.slider.setValue((current + self.animate_every) % self.SLIDER_STEPS)

    # started
    def context_menu_requested(self, pos):
        """
        handler of customContextMenuRequested

        Items on menu:
            Show *slider or value* depending on which is shown at the moment
            Animation step - currently without function
        """
        menu = QMenu("Context menu", self)

        switch_widgets_action = QAction(self)
        if self.slider_widget.isHidden():
            switch_widgets_action.setText("Show slider")
        else:
            switch_widgets_action.setText("Show value")
        switch_widgets_action.triggered.connect(self.switch_visible_widget)

        anim_step_action = QAction("Animation options", self)
        anim_step_action.triggered.connect(self.anim_step_trigered)

        tracking_action = QAction(self)
        if self.slider.hasTracking():
            tracking_action.setText("Turn tracking off")
        else:
            tracking_action.setText("Turn tracking on")
        tracking_action.triggered.connect(self.tracking_action_triggered)

        menu.addActions([switch_widgets_action, anim_step_action, tracking_action])
        menu.exec(self.mapToGlobal(pos))

    # started
    def tracking_action_triggered(self):
        if self.slider.hasTracking():
            self.slider.setTracking(False)
        else:
            self.slider.setTracking(True)

    # started
    def anim_step_trigered(self, _):
        """
        handler for triggered signal of menu action
        """
        # TODO Implement animation step
        if self.timer_backward.isActive():
            self.play_backward_clicked()
        if self.timer_forward.isActive():
            self.play_forward_clicked()

        self.value_widget.hide()
        self.slider_widget.hide()
        self.anim_settings_widget.show()
        self.animate_every_edit.setFocus()

    # started
    def animate_every_finished(self):
        current = int(self.animate_every_edit.text())
        if current < 1 or current > self.SLIDER_STEPS // 2:
            self.animate_every_edit.setText(str(self.animate_every))
        else:
            self.animate_every = current
            self.animation_period_edit.setFocus()

    # started
    def animation_period_finished(self):
        current = int(self.animation_period_edit.text())
        if current < 0:
            self.animation_period_edit.setText(str(self.animation_period))
        else:
            self.animation_period = current

    # started
    def animation_period_return(self):
        self.anim_settings_widget.hide()
        self.slider_widget.show()

    def create_anim_settings_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.anim_settings_widget.setLayout(layout)

        step_label = QLabel("Step:", self.anim_settings_widget)
        self.animate_every_edit = QLineEdit(str(self.animate_every), self.anim_settings_widget)
        period_label = QLabel("Period:", self.anim_settings_widget)
        self.animation_period_edit = QLineEdit(str(self.animation_period), self.anim_settings_widget)

        self.animate_every_edit.setMaximumWidth(30)
        self.animation_period_edit.setMinimumWidth(20)

        layout.addWidget(step_label)
        layout.addWidget(self.animate_every_edit)
        layout.addWidget(period_label)
        layout.addWidget(self.animation_period_edit)

        self.animate_every_edit.editingFinished.connect(self.animate_every_finished)
        self.animation_period_edit.editingFinished.connect(self.animation_period_finished)
        self.animation_period_edit.returnPressed.connect(self.animation_period_return)

        validator = QIntValidator()
        self.animate_every_edit.setValidator(validator)
        self.animation_period_edit.setValidator(validator)

    def create_main_layout(self):
        """
        creates HBox layout for self
        button fixed sizes are set here
        """
        layout = QHBoxLayout(self)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        play_backward_button = QPushButton(self.BACKWARD_PLAY_LABEL, self)
        step_backward_button = QPushButton('<', self)
        slider_widget = QWidget(self)
        value_widget = QWidget(self)
        anim_settings_widget = QWidget(self)
        step_forward_button = QPushButton('>', self)
        play_forward_button = QPushButton(self.FORWARD_PLAY_LABEL, self)

        layout.addWidget(play_backward_button)
        layout.addWidget(step_backward_button)
        layout.addWidget(slider_widget)
        layout.addWidget(value_widget)
        layout.addWidget(anim_settings_widget)
        layout.addWidget(step_forward_button)
        layout.addWidget(play_forward_button)

        buttons_width = play_backward_button.height()
        play_arrow_font = QFont('Arial', 14)
        play_backward_button.setFixedSize(buttons_width, buttons_width)
        play_backward_button.clicked.connect(self.play_backward_clicked)
        play_backward_button.setFont(play_arrow_font)
        play_forward_button.setFixedSize(buttons_width, buttons_width)
        play_forward_button.clicked.connect(self.play_forward_clicked)
        play_forward_button.setFont(play_arrow_font)

        step_backward_button.setFixedSize(buttons_width, buttons_width)
        step_backward_button.clicked.connect(self.step_backward_clicked)
        step_forward_button.setFixedSize(buttons_width, buttons_width)
        step_forward_button.clicked.connect(self.step_forward_clicked)

        self.play_backward_button = play_backward_button
        self.play_forward_button = play_forward_button
        self.slider_widget = slider_widget
        self.value_widget = value_widget
        self.anim_settings_widget = anim_settings_widget

    def create_slider_layout(self):
        """
        creates layout for slider_widget
        slider is set up here
        """
        layout = QHBoxLayout(self.slider_widget)
        self.slider_widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self.low_edit = QLineEdit(str(self.low), self.slider_widget)
        self.slider = QSlider(Qt.Horizontal, self.slider_widget)
        self.high_edit = QLineEdit(str(self.high), self.slider_widget)

        layout.addWidget(self.low_edit)
        layout.addWidget(self.slider)
        layout.addWidget(self.high_edit)

        validator = QDoubleValidator()

        self.low_edit.setMaximumWidth(40)
        self.low_edit.setCursorPosition(0)
        self.low_edit.setValidator(validator)
        self.low_edit.editingFinished.connect(self.low_edit_finished)
        self.high_edit.setMaximumWidth(40)
        self.high_edit.setCursorPosition(0)
        self.high_edit.setValidator(validator)
        self.high_edit.editingFinished.connect(self.high_edit_finished)

        self.slider.setMaximum(self.SLIDER_STEPS)
        self.slider.setTracking(False)
        self.slider.setValue(self._get_closest_slider_value(self.value))
        self.slider.valueChanged.connect(self.slider_value_changed)

    def slider_value_changed(self, value):
        """
        handler for valueChanged signal of slider
        calculates actual value of the slider (slider values are from 0 to SLIDER_STEPS)
        updates value_edit
        emits valueChanged signal of self, cought by ManipulateWidget
        """
        actual = self.low + (self.high - self.low) * value / self.SLIDER_STEPS
        if float(self.value_edit.text()) != actual:
            self.value_edit.setText(str(actual))
        self.value = actual
        self.valueChanged.emit(actual)

    def create_value_layout(self):
        """
        creates layout for value_widget
        it is not necessary to set up solo value_widget as it only contains one value_edit, it's done this way for
        consistency (and maybe future edits)
        QDoubleValidator is set for value_edit - it disallows characters other than numbers and . in value_edit,
        doesn't check range
        """
        layout = QHBoxLayout(self.value_widget)
        self.value_widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self.value_edit = QLineEdit(str(self.value), self.value_widget)
        layout.addWidget(self.value_edit)

        self.value_edit.setValidator(QDoubleValidator())
        self.value_edit.editingFinished.connect(self.value_edit_finished)


    def value_edit_finished(self):
        """
        handler of editingFinished of value_edit
        checks the value, then finds the nearest possible value of the slider and sets it. By changing the slider
        the value_edit is then changed to this new value (correcting the passed value)
        """
        current = float(self.value_edit.text())
        if current < self.low:
            self.value_edit.setText(str(float(self.low)))
            self.slider.setValue(0)
        elif current > self.high:
            self.value_edit.setText(str(float(self.high)))
            self.slider.setValue(self.SLIDER_STEPS)
        else:
            val = self._get_closest_slider_value(current)
            self.slider.setValue(val)
            if self.value_edit.text() != str(self.value):
                self.value_edit.setText(str(self.value))

    def _get_closest_slider_value(self, val):
        normalized = val - self.low
        size_of_step = (self.high - self.low) / self.SLIDER_STEPS
        # TODO: make size_of_step attribute
        cca_steps = normalized / size_of_step
        rounded = decimal.Decimal(cca_steps).quantize(1, rounding=decimal.ROUND_HALF_UP)
        return rounded

    # done differently
    def switch_visible_widget(self):
        """
        switches the two widgets by hiding one and showing the other
        focus is set to window to remove it from value_edit
        """
        if self.slider_widget.isHidden():
            self.value_widget.hide()
            self.anim_settings_widget.hide()
            self.slider_widget.show()
        else:
            self.slider_widget.hide()
            self.anim_settings_widget.hide()
            self.value_widget.show()

            self.window().setFocus()

    # started
    def play_backward_clicked(self, _=None):
        """
        starts/stops animation of the slider backward
        when lowest value is reached, it underflows to the highest and continues down
        button label is changed to square when animation is started
        does nothing when the other animation is playing
        """
        if self.timer_backward.isActive():
            self.timer_backward.stop()
            self.play_backward_button.setText(self.BACKWARD_PLAY_LABEL)
            self.play_forward_button.setDisabled(False)
        else:
            self.timer_backward.start(self.animation_period)
            self.play_backward_button.setText(self.STOP_ANIMATION_LABEL)
            self.play_forward_button.setDisabled(True)

    # started
    def play_forward_clicked(self, _=None):
        """
        starts animation of the slider forward
        when highest value is reached, it overflows to the lowest and continues up
        button label is changed to square when animation is started
        does nothing when the other animation is playing
        """
        if self.timer_forward.isActive():
            self.timer_forward.stop()
            self.play_forward_button.setText(self.FORWARD_PLAY_LABEL)
            self.play_backward_button.setDisabled(False)
        else:
            self.timer_forward.start(self.animation_period)
            self.play_forward_button.setText(self.STOP_ANIMATION_LABEL)
            self.play_backward_button.setDisabled(True)

    # no need
    def step_backward_clicked(self, _):
        """
        lowers the slider value by one step, doesn't underflow
        """
        current = self.slider.value()
        if current > 0:
            self.slider.setValue(current - 1)

    # no need
    def step_forward_clicked(self, _):
        """
        rises the slider value by one step, doesn't overflow
        """
        current = self.slider.value()
        if current < self.SLIDER_STEPS:
            self.slider.setValue(current + 1)


class ManipulateWidget(QWidget):

    def __init__(self, callback, period=50):
        super().__init__()

        self.callback = callback
        self.period = period

        self.time_of_last_change = time()

        self.names, self.limits, self.defaults = self.get_arguments()
        self.grid = QGridLayout(self)
        self.setLayout(self.grid)

        self.rows = self.make_rows()

    def make_rows(self):
        rows = []

        for i, (name, (low, high), default) in enumerate(zip(self.names, self.limits, self.defaults)):
            name_label = QLabel(name, self)
            row = ManipulateRowWidget(low, high, default, self)
            row.valueChanged.connect(self.something_changed)
            self.grid.addWidget(name_label, i, 0, alignment=Qt.AlignRight)
            self.grid.addWidget(row, i, 1)
            rows.append(row)

        return rows

    def something_changed(self, *_):
        now = time()
        if now - self.time_of_last_change < self.period / 1000:
            if any([r.timer_forward.isActive() or r.timer_backward.isActive() or r.slider.hasTracking()
                    for r in self.rows]):
                return

        args = []

        for r in self.rows:
            args.append(r.value)

        self.time_of_last_change = now
        print(f"calling callback with arguments {args}")
        self.callback(*args)

    # done
    def make_callback(self):
        self.something_changed()

    # done
    def get_arguments(self):
        signature = inspect.signature(self.callback)
        params = signature.parameters
        names = list(params)
        limits = []
        defaults = []

        for param in params.values():
            default = param.default

            if isinstance(default, collections.Sequence):
                if len(default) == 2 and default[0] < default[1]:
                    float(default[0])
                    float(default[1])
                    limits.append(tuple(default))
                    defaults.append(default[0])
                elif len(default) == 3 and default[0] <= default[2] <= default[1]:
                    float(default[0])
                    float(default[1])
                    float(default[2])
                    limits.append(tuple(default[0:2]))
                    defaults.append(default[2])
                else:
                    raise ValueError("Unable to parse such arguments")

            else:
                limits.append((0, 1))
                defaults.append(0)

        return names, limits, defaults
