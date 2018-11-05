import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator
import scipy as sp
from sys import float_info


class TimeSeries:

    def __init__(self,
                 width=0,
                 height=0,
                 xlabel="",
                 ylabel="",
                 rescale_to=1 / 0.8,
                 lazy_threshold=False,
                 axes=None):
        """
         This class represents a plot of time series data. The t axis grows with growing data set,
         the y axis accomodates the data. 
         Without any data, the axis are empty, with one data point, both axis contain one tick 
         labeled with the point position. With more data, the axis have ticks generated automatically.

         Parameters
         ----------
         width : float
             Width of axes in inches, exclusive with axes
         height : float
             Height of axes in inches, exclusive with axes
         xlabel : str
             Label of x (t) axes
         ylabel : str
             Label of y axes
         rescale_to : float > 1
             When data line runs out of space, the x (t) axes rescales to 
             (the space needed to fit the data) * rescale_to
         lazy_threshold : bool or int
             If true, add_point(t, y) doesn't call add_points([t], [y]) but stores the passed values
             in lists. When the lists are lazy_threshold long, add_points is called with the lists
         axes : matplotlib.axes.Axes
             Axes to draw on. Exclusive with width and height. Passing axes implies usage of more 
             than one axes in figure.
         """

        if (width or height) and axes:
            raise ValueError("Size and axes can not be passed simultaneously.")

        # ----- SIZE ----- #
        if not width:
            width = mpl.rcParams["figure.figsize"][0]
        if not height:
            height = mpl.rcParams["figure.figsize"][1]

        # ----- ATTRIBUTES ----- #
        if rescale_to <= 1:
            raise ValueError("Value of rescale_to must be larger than 1.")
        self.rescale_to = rescale_to

        self.lazy_threshold = lazy_threshold
        self._lazy_tlist = []
        self._lazy_ylist = []

        self.last_t = -sp.inf
        self.left_tlim = None
        self.right_tlim = None
        self.min_y = sp.inf
        self.max_y = -sp.inf

        self.ts = []
        self.ys = []

        # ----- PLOT PREPARATION ----- #
        if axes:
            self.ax = axes
            self.fig = axes.get_figure()
        else:
            self.fig, self.ax = plt.subplots(figsize=(width, height))

        self.l, = self.ax.plot([], [], "k", lw=1)

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        # ----- TICKS ----- #
        self.ax.ticklabel_format(axis="both", style="sci", scilimits=(-4, 4), useMathText=True)

        self._tick_formatter = self.ax.xaxis.get_major_formatter()

        # no ticks initially
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.ax.xaxis.set_major_formatter(self._tick_formatter)
        self.ax.yaxis.set_major_formatter(self._tick_formatter)

    def add_point(self, t, y):
        """ 
        Adds point [t, y] to the line. If lazy_threshold is a number, the data are stored until
        the storage lists are lazy_threshold long.

        Parameters
        ----------
        t : float
            t point
        y : float
            y point
        """

        if self.lazy_threshold:

            self._lazy_tlist.append(t)
            self._lazy_ylist.append(y)

            if len(self._lazy_tlist) >= self.lazy_threshold:

                self.add_points(self._lazy_tlist, self._lazy_ylist)
                self._lazy_tlist = []
                self._lazy_ylist = []

        else:

            self.add_points([t], [y])

    def add_points(self, ts, ys):
        """
        Adds points to the line. 

        Parameters
        ----------
        ts : N-length sequence of floats
            x (t) data
        ys : N-length sequence of floats
            y data
        """

        if not sorted(ts) == ts:
            raise ValueError("Values of times must be increasing.")

        if ts[0] <= self.last_t:
            raise ValueError("Passed time value is lower than previous values.")

        self.last_t = ts[-1]

        self.ts += ts
        self.ys += ys

        self.l.set_data(self.ts, self.ys)

        # first or second call of this method
        if self.left_tlim is None:

            assert self.right_tlim is None

            if len(self.ts) == 1:
                self.ax.set_xticks([self.ts[0]])
                self.ax.set_yticks([self.ys[0]])

            elif len(self.ts) > 1:
                self.ax.xaxis.set_major_locator(AutoLocator())
                self.ax.yaxis.set_major_locator(AutoLocator())
                self.left_tlim = self.ts[0]
                self.right_tlim = self.ts[-1]

            self.ax.relim()
            self.ax.autoscale_view(tight=True)

            self.min_y, self.max_y = self.ax.get_ylim()

        else:

            # ----- X scaling ----- #
            if self.last_t > self.right_tlim:

                times_span = self.last_t - self.left_tlim
                new_tspan = times_span * self.rescale_to
                self.right_tlim = self.left_tlim + new_tspan
                self.ax.set_xlim(self.left_tlim, self.right_tlim)

            # ----- Y scaling ----- #
            max_y = max(ys)
            if max_y > self.max_y:
                self.max_y = max_y
                self.ax.set_ylim(top=self.max_y)

            min_y = min(ys)
            if min_y < self.min_y:
                self.min_y = min_y
                self.ax.set_ylim(bottom=self.min_y)

        self.fig.canvas.draw()
