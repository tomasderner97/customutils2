from custom_utils.science.imports import *

from scipy.interpolate import UnivariateSpline as _UnivariateSpline
from scipy.optimize import curve_fit as _curve_fit
import warnings

from custom_utils.science._df_to_table import df_to_booktabs_table

__version__ = "1.0"


def use_mpl_latex_style():
    """ Changes rcParams to use latex in plots, also changes size to one good for protocols. """
    # 6 is the widest possible for latex protokol class, 3.75 is arbitrary
    plt.rcParams["figure.figsize"] = (6, 3.75)
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["text.usetex"] = True
    plt.rcParams['text.latex.unicode'] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Computer Modern"]
    plt.rcParams["text.latex.preamble"] = r"""
    \usepackage[decimalsymbol=comma]{siunitx}
    """


def use_mpl_default_style():
    """ Changes rcParams to default. """
    mpl.rcParams.update(mpl.rcParamsDefault)


def gamma_factor(v):

    return 1 / (1 - v**2 / sp.constants.c**2)**0.5


def dataframe_from_csv(csv, index_col=None, sep=r"\s*,\s*", **kwargs):
    """ Creates Pandas dataframe from comma separated values file, allows # comments and 
    blank lines. """

    separator = r"\s+" if sep == ' ' else sep
    return pd.read_csv(csv, sep=separator,
                       engine="python",
                       skip_blank_lines=True,
                       index_col=index_col,
                       comment="#",
                       ** kwargs)


def repeated_measurement_mean_and_error(values):
    """ 
    Calculates the mean and mean error of multiple measurements of one quantity.

    Parameters
    ----------
    values : sequence
        multiple values of one quantity from repeated measurement

    Returns
    -------
    mean : float
        mean of the values
    mean_error : float
        error of the mean, eg. std (ddof=1) of values divided by sqrt of number of values
    """
    array = sp.array(values)
    mean = array.mean()
    single_value_error = array.std(ddof=1)
    mean_error = single_value_error / sp.sqrt(len(array))

    return mean, mean_error


def f_line(x, a, b):
    """
    Simple line function, intended for ls regression.
    """
    return a * x + b


def f_para(x, a, b, c):
    """
    Quadratic function, intended for ls regression.
    """
    return a * x**2 + b * x + c


def f_cubic(x, a, b, c, d):
    """
    Cubic function, intended for ls regression
    """
    return a * x**3 + b * x**2 + c * x + d


def f_exp(x, a, b, c, d):
    """
    Exponential function with translation, intended for ls regression.
    """
    return a * sp.exp(b * (x + c)) + d


def f_exp_simple(x, a, b):
    """
    Exponential function without translation, intended for ls regression.
    """
    return a * sp.exp(b * x)


def f_gaussian(x, h, mu, sigma, dy):
    """
    Gaussian curve. Intended for ls regression.
    """
    return h * sp.exp(-(x - mu)**2 / (2 * sigma**2)) + dy


def f_sin(x, amp, omega, phi, dy):
    """
    Sinus curve. Intended for ls regression.
    """
    return amp * sp.sin(omega * x + phi) + dy


class FitCurve:
    """
    Class representing function fitted to some data. Objects are callable.
    Arguments are the same as for scipy.optimize.curve_fit.

    Parameters
    ----------
    f: callable
        Function to fit parameters to.
        Has to have format f(x, param1, param2, ...)
    xdata: M-length sequence
        X values of data points.
    ydata: M-length sequence
        Y values of data points.
    p0: None, scalar or N-length sequence
        Initial guess for the parameters.
    sigma: None or M-length sequence
        Determines the uncertainty of ydata.
    """

    def __init__(self, f, xdata, ydata, *args, **kwargs):
        params, cov = _curve_fit(f, xdata, ydata, *args, **kwargs)
        errors = [sp.sqrt(cov[i, i]) for i in range(len(cov))]

        if len(sp.where(cov == sp.inf)[0]) > 0:
            raise ValueError(
                "Fit unsuccessful, provide better initial parameters (p0)")

        self.params = params
        self.errors = errors
        self.xdata = sp.array(xdata)
        self.ydata = sp.array(ydata)
        self.f = lambda x: f(x, *params)

    def __call__(self, x):
        return self.f(x)

    def curve(self, start=None, end=None, res=100, overrun=0):
        """
        Calculates the curve of the fit, used as line of theoretical function.

        Parameters
        ----------
        start: float, optional
            The lowest x value. If none, lowest of original x data is used.
        end: float, optional
            The highest x value. If none, highest of original x data is used.
        resolution: int
            Number of points used in between start and end(inclusive).
        overrun: float, (float, float)
            fraction of x interval to add before start and after end.
            If tuple, the values are used for start and end separately.
        """
        if start is None:
            start = self.xdata.min()
        if end is None:
            end = self.xdata.max()

        interval_length = end - start

        try:
            start -= overrun[0] * interval_length
            end += overrun[1] * interval_length
        except TypeError:
            start -= overrun * interval_length
            end += overrun * interval_length

        xes = sp.linspace(start, end, res)
        ys = self(xes)

        return xes, ys


class Spline(_UnivariateSpline):
    """
    Thin wrapper around the scipy's UnivariateSpline. Original data is saved in xdata, ydata.
    Curve function was added. Objects are callable.
    If passed x array is not strictly increasing, raises a warning and monotonizes
    the data automaticaly.

    Parameters
    ----------
    x: Sequence like
        x data
    y: Sequence like
        y data
    and other params of UnivariateSpline.
    """

    def __init__(self, x, y, *args, **kwargs):
        try:
            _UnivariateSpline.__init__(self, x, y, *args, **kwargs)
        except ValueError as e:
            if str(e) == "x must be strictly increasing":
                warnings.warn("Spline: ValueError catched, monotonizing!")

                mono_x, mono_y = self._monotonize(x, y)
                _UnivariateSpline.__init__(
                    self, mono_x, mono_y, *args, **kwargs
                )
            else:
                raise e

        self.xdata = sp.array(x)
        self.ydata = sp.array(y)

    def curve(self, start=None, end=None, res=100, overrun=0):
        """
        Calculates the curve of the spline, used as line of theoretical function
        or a lead for an eye.

        Parameters
        ----------
        start: float, optional
            The lowest x value. If none, lowest of original x data is used.
        end: float, optional
            The highest x value. If none, highest of original x data is used.
        resolution: int
            Number of points used in between start and end(inclusive).
        overrun: float, (float, float)
            fraction of x interval to add before start and after end. If tuple,
            the values are used for start and end separately.
        """
        if start is None:
            start = self.xdata.min()
        if end is None:
            end = self.xdata.max()

        interval_length = end - start

        try:
            start -= overrun[0] * interval_length
            end += overrun[1] * interval_length
        except TypeError:
            start -= overrun * interval_length
            end += overrun * interval_length

        xes = sp.linspace(start, end, res)
        ys = self(xes)

        return xes, ys

    def _monotonize(self, xdata, ydata):
        """
        Helper function to make passed x and y value array strictly increasing.
        New in 0.1.2

        Parameters:
        -----------
        xdata: sequence
            X points
        ydata: sequence
            Y points

        Returns:
        --------
        new_x: numpy.ndarray
            monotonized X points
        new_y: numpy.ndarray
            monotonized Y points
        """
        highest = xdata[0] - 1
        new_x = []
        new_y = []

        for x, y in zip(xdata, ydata):
            if x > highest:
                new_x.append(x)
                new_y.append(y)
                highest = x

        return sp.array(new_x), sp.array(new_y)


def main():

    df = pd.DataFrame()
    df["a"] = [1, 2, 3]
    df["b"] = [5.25785, 4e-7, 18]

    return df


if __name__ == '__main__':
    df = main()
