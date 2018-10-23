import matplotlib.pyplot as plt
from matplotlib.widgets import Slider as SliderOrig
from collections import namedtuple, Sequence
import six


__version__ = "1.0"


class Slider(SliderOrig):
    """
    The original matplotlib Slider only passed a val parameter to the update function, which is
    a problem when we have more sliders calling the same update function. This class inherits
    Slider and adds the name property and edits the set_val function to pass items dictionary and 
    name of updated slider (itself) to update function
    """

    def __init__(self, ax, name, label, valmin, valmax, valinit, items_dict, **kwargs):

        SliderOrig.__init__(self, ax, label, valmin, valmax, valinit, **kwargs)

        self.name = name
        self.items_dict = items_dict

    def set_val(self, val):
        """
        Set slider value to *val*
        function coppied from original Slider

        Parameters
        ----------
        val : float
        """
        xy = self.poly.xy
        xy[2] = val, 1
        xy[3] = val, 0
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % val)
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        if not self.eventson:
            return
        for cid, func in six.iteritems(self.observers):
            func(self.items_dict, self.name)  # changed this line


class SliderSetup:
    """
    This class functions as a container for slider settings.
    """

    def __init__(self, name, label='', minv=0, maxv=1, init=0, step=0):
        """
        Parameters
        ----------

        name : str
            name of the slider, under which it is saved to items dict
        label : str, optional
            label shown to the left to the slider, default is name
        minv, maxv : float, optional
            min and max value for slider, default is 0 and 1 respectively
        init : float, optional
            initial value of slider, default is 0 or minv if minv > 0
        step : float, not implemented
        """

        self.name = name
        self.label = label if label else name
        self.minv = minv
        self.maxv = maxv
        self.init = init if minv <= init <= maxv else minv
        self.step = step


def make_sliders(fig,
                 ax,
                 sliders,
                 update,
                 init=None,
                 flags="",
                 sld_height=0.02,
                 sld_length=0.7,
                 sld_spacing=0.02):

    items = dict(fig=fig, ax=ax)

    if not isinstance(sliders, Sequence):
        sliders = [sliders]

    fig.tight_layout()

    noautoscale = "noasc" in flags or "noautoscale" in flags
    clear = "clear" in flags

    def update_helper(items, changed):

        if noautoscale:
            old_xlim = items["ax"].get_xlim()
            old_ylim = items["ax"].get_ylim()

        if clear:
            old_xlabel = items["ax"].get_xlabel()
            old_ylabel = items["ax"].get_ylabel()
            items["ax"].clear()

        update(items, changed)

        if noautoscale:
            items["ax"].set_xlim(old_xlim)
            items["ax"].set_ylim(old_ylim)
        else:
            items["ax"].relim()
            items["ax"].autoscale_view()

        if clear:
            # if labels changed during update, leave them, else restore old ones
            if not items["ax"].get_xlabel():
                items["ax"].set_xlabel(old_xlabel)
            if not items["ax"].get_ylabel():
                items["ax"].set_ylabel(old_ylabel)

    for i, sld in enumerate(reversed(sliders)):

        left = (1 - sld_length) / 2
        bottom = sld_spacing + i * (sld_spacing + sld_height)

        sld_ax = plt.axes([left, bottom, sld_length, sld_height])
        items[sld.name] = Slider(sld_ax, sld.name, sld.label, sld.minv, sld.maxv, sld.init, items)
        items[sld.name].on_changed(update_helper)

        fig.add_axes(sld_ax)

    if init:
        init(items)
    update(items)

    bottom_space = sld_height * len(sliders) + sld_spacing * (len(sliders) + 1)

    if ax.get_xlabel():  # make space for possible xlabel
        bottom_space += 0.04

    fig.subplots_adjust(bottom=0.05 + bottom_space)
    fig.canvas.draw_idle()
    ax.relim()
    ax.autoscale_view()

    return items
