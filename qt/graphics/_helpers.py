import numpy as np
from PyQt5.QtGui import QPainter


def angle_from_vertical(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    rads = np.angle(dx + dy * 1j)
    degs = np.rad2deg(rads)
    return (degs - 90) % 360


if __name__ == "__main__":
    print(angle_from_vertical(0, 0, 1, -1))


def scale_of_painter(p: QPainter):
    """
    Returns absolute scale factor of QPainter as a tupple of sx, sy.
    Works with successive translations and scaling applied, as well as rotations,
    but fails if rotation is followed by scaling. 
    Shear wasn't tested. 
    """
    qtf = p.transform()

    scale_x = np.sqrt(qtf.m11()**2 + qtf.m21()**2)
    scale_y = np.sqrt(qtf.m12()**2 + qtf.m22()**2)

    return scale_x, scale_y


def paint_axes(p: QPainter,
               xtick_every=0,
               ytick_every=0,
               xlabels="down",
               ylabels="left",
               opacity=0.5):

    from PyQt5.QtGui import QPen, QColor
    from PyQt5.QtCore import Qt, QLineF

    cur_pen = p.pen()

    color = QColor(Qt.black)
    color.setAlphaF(opacity)
    pen = QPen(color)

    xscale, yscale = scale_of_painter(p)

    xlength = 10000 / xscale
    ylength = 10000 / yscale

    xline_width = 2 / yscale
    yline_width = 2 / xscale

    xtick_length = 10 / yscale
    ytick_length = 10 / xscale

    if not xtick_every:
        xtick_every = 50 / xscale

    if not ytick_every:
        ytick_every = 50 / yscale

    pen.setWidthF(xline_width)
    p.setPen(pen)
    p.drawLine(-xlength / 2, 0, xlength / 2, 0)

    pen.setWidthF(yline_width)
    p.setPen(pen)
    p.drawLine(0, -ylength / 2, 0, ylength / 2)

    p.save()

    for i in range(int(xlength / 2 / xtick_every)):
        p.translate(xtick_every, 0)
        p.drawLine(QLineF(0, -xtick_length / 2, 0, xtick_length / 2))

    p.restore()
    p.save()

    for i in range(int(xlength / 2 / xtick_every)):
        p.translate(-xtick_every, 0)
        p.drawLine(QLineF(0, -xtick_length / 2, 0, xtick_length / 2))

    p.restore()
    p.save()

    pen.setWidthF(xline_width)
    p.setPen(pen)

    for i in range(int(ylength / 2 / ytick_every)):
        p.translate(0, ytick_every)
        p.drawLine(QLineF(-ytick_length / 2, 0, ytick_length / 2, 0))

    p.restore()
    p.save()

    for i in range(int(ylength / 2 / ytick_every)):
        p.translate(0, -ytick_every)
        p.drawLine(QLineF(-ytick_length / 2, 0, ytick_length / 2, 0))

    p.restore()
