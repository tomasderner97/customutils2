from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt


def empty_3d_scene(figsize=None):
    """
    Create empty axes completely filling the figure.
    """

    fig = plt.figure(figsize)
    ax = plt.axes(projection="3d")
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    return fig, ax
