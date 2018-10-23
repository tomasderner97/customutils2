import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import scipy as sp


class Measurement:

    def __init__(self, fig, ax, register_click_event=True):

        self.scale_ratio = 100
        self.fig = fig
        self.ax = ax

        self.xlim = None
        self.ylim = None
        self.xspan = 0
        self.yspan = 0
        self.horizontal_size = 0
        self.vertical_size = 0

        self.currently_editing = 0

        self.cross1_pos = None
        self.cross2_pos = None

        self.artists = []

        if register_click_event:
            self.register()

    def plot_cross(self, x, y, color="black"):

        hs = self.horizontal_size
        vs = self.vertical_size

        l1, = self.ax.plot([x], [y], ".", c=color, ms=1)
        l2, = self.ax.plot([x - 2 * hs, x - hs], [y, y], c=color, lw=1)
        l3, = self.ax.plot([x + hs, x + 2 * hs], [y, y], c=color, lw=1)
        l4, = self.ax.plot([x, x], [y - 2 * vs, y - vs], c=color, lw=1)
        l5, = self.ax.plot([x, x], [y + vs, y + 2 * vs], c=color, lw=1)

        self.artists += [l1, l2, l3, l4, l5]

    def on_click(self, event):

        if event.xdata is None or event.ydata is None:
            return

        if event.inaxes is not self.ax:
            return

        self.xlim = self.ax.get_xlim()
        self.xspan = self.xlim[1] - self.xlim[0]

        self.ylim = self.ax.get_ylim()
        self.yspan = self.ylim[1] - self.ylim[0]

        self.horizontal_size = self.xspan / self.scale_ratio
        self.vertical_size = self.yspan / self.scale_ratio

        if not self.cross1_pos:

            self.cross1_pos = (event.xdata, event.ydata)

            self.plot_cross(*self.cross1_pos)

        elif not self.cross2_pos:

            self.cross2_pos = (event.xdata, event.ydata)

            self.plot_all_components()

        else:

            x = event.xdata
            y = event.ydata

            if self.clicked_near_cross(1, x, y) and not self.currently_editing:

                self.currently_editing = 1
                self.plot_all_components(cross1_color="red")

            elif self.clicked_near_cross(2, x, y) and not self.currently_editing:

                self.currently_editing = 2
                self.plot_all_components(cross2_color="red")

            elif self.currently_editing == 1:

                self.cross1_pos = (event.xdata, event.ydata)
                self.currently_editing = 0

                self.plot_all_components()

            elif self.currently_editing == 2:

                self.cross2_pos = (event.xdata, event.ydata)
                self.currently_editing = 0

                self.plot_all_components()

            else:

                while self.artists:
                    self.artists.pop().remove()

                self.cross1_pos = None
                self.cross2_pos = None

        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        event.canvas.draw()

    def plot_line_between(self, color="grey"):

        l, = self.ax.plot(
            [self.cross1_pos[0], self.cross2_pos[0]],
            [self.cross1_pos[1], self.cross2_pos[1]],
            ":", c=color
        )
        self.artists.append(l)

    def plot_text(self):

        dx = self.cross2_pos[0] - self.cross1_pos[0]
        dy = self.cross2_pos[1] - self.cross1_pos[1]

        k = dy / dx
        angle = sp.arctan(k) / sp.pi * 180

        print(f"Angle: {angle}°, k: {k}")

        k_str = f"{k:.3f}" if sp.absolute(k) > 0.1 else f"{k:.2e}"

        signx = 1
        signy = 1
        halign = "left"
        valign = "bottom"

        if self.cross2_pos[0] > (self.xlim[0] + self.xlim[1]) / 2:
            signx = -1
            halign = "right"

        if self.cross2_pos[1] < self.cross1_pos[1]:
            signy = -1
            valign = "top"

        t = self.ax.text(self.cross2_pos[0] + signx * self.horizontal_size,
                         self.cross2_pos[1] + signy * self.vertical_size,
                         f"{angle:.2f}°, k = {k_str}",
                         horizontalalignment=halign,
                         verticalalignment=valign)

        self.artists.append(t)

    def plot_all_components(self, cross1_color="black", cross2_color="black", line_color="grey"):

        while self.artists:
            self.artists.pop().remove()

        self.plot_line_between(color=line_color)
        self.plot_cross(*self.cross1_pos, color=cross1_color)
        self.plot_cross(*self.cross2_pos, color=cross2_color)
        self.plot_text()

    def clicked_near_cross(self, cross, x, y):

        if cross == 1:
            cross_pos = self.cross1_pos
        elif cross == 2:
            cross_pos = self.cross2_pos
        else:
            raise ValueError()

        dist_to_cross_x = sp.absolute(x - cross_pos[0])
        dist_to_cross_y = sp.absolute(y - cross_pos[1])

        return dist_to_cross_x < 2 * self.horizontal_size and \
            dist_to_cross_y < 2 * self.vertical_size

    def register(self):

        self.fig.canvas.mpl_connect("button_press_event", self.on_click)


def main():
    fig, ax = plt.subplots()

    x = sp.linspace(-2 * sp.pi, 2 * sp.pi)
    y = sp.sin(x)
    ax.plot(x, y)
    m = Measurement(fig, ax)
    plt.show()


if __name__ == '__main__':
    main()
