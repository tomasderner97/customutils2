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
