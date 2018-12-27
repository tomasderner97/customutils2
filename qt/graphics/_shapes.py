from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPolygonF
from math import sqrt
from numpy import sign


class Box:

    def __init__(self, left, bottom, right, top):
        """
        Helper class for Qt QPainter graphics. 
        Holds information about a rectangle, usable for drawRect, drawEllipse...
        Origin point is always 0,0
        Is callable, call returns QRectF
        """

        if left > right:
            raise ValueError("'left' must be smaller than 'right'")
        if bottom > top:
            raise ValueError("'bottom' must be smaller than 'top'")

        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):

        return self.right - self.left

    @property
    def height(self):

        return self.top - self.bottom

    def set_origin(self, wratio=None, hratio=None):
        """
        Sets new origin as a ratio of width and height.
        """

        if wratio is not None:
            width = self.width
            self.left = -wratio * width
            self.right = (1 - wratio) * width

        if hratio is not None:
            height = self.height
            self.bottom = -hratio * height
            self.top = (1 - hratio) * height

    def get(self, xtranslate=0, ytranslate=0):
        """
        Returns QRectF, can be translate by xtranslate, ytranslate
        """

        # docs: QRectF(qreal x, qreal y, qreal width, qreal height)
        return QRectF(self.left + xtranslate, self.bottom + ytranslate, self.width, self.height)


def box_from_dimensions(width, height, origin_xratio=0, origin_yratio=0):
    """
    Returns a Box instance with set width and height and origin given by passed ratios.
    """

    return Box(-origin_xratio * width,
               -origin_yratio * height,
               (1 - origin_xratio) * width,
               (1 - origin_yratio) * height)


class Arrow:

    def __init__(self,
                 tail=0,
                 head=0,
                 rel_arrowhead_length=0,
                 rel_arrowhead_width=0,
                 rel_tail_width=0,
                 abs_arrowhead_length=0,
                 abs_arrowhead_width=0,
                 abs_tail_width=0):
        """
        Helper class for Qt QPainter graphics. 
        Creates a down facing arrow as a QPolygonF
        Origin point is always 0,0
        Is callable, call returns QPolygonF
        arrow dimensions are by default relative to length, absolute dimensions can be set
        """

        self.head = head
        self.tail = tail

        self.set_dimensions(rel_arrowhead_length,
                            rel_arrowhead_width,
                            rel_tail_width,
                            abs_arrowhead_length,
                            abs_arrowhead_width,
                            abs_tail_width)

        self.points = None

    def set_origin(self, ratio):
        """
        Set new origin as a ratio of length away from tail.
        """

        length = self.length
        self.tail = -ratio * length
        self.head = (1 - ratio) * length
        self.points = None

    def set_dimensions(self,
                       rel_arrowhead_length=0,
                       rel_arrowhead_width=0,
                       rel_tail_width=0,
                       abs_arrowhead_length=0,
                       abs_arrowhead_width=0,
                       abs_tail_width=0):

        if (rel_arrowhead_length and abs_arrowhead_length) \
                or (rel_arrowhead_width and abs_arrowhead_width) \
                or (rel_tail_width and abs_tail_width):
            raise ValueError("Relative and absolute dimensions cannot be specified together.")

        self.rel_arrowhead_length = rel_arrowhead_length
        self.rel_arrowhead_width = rel_arrowhead_width
        self.rel_tail_width = rel_tail_width
        self.abs_arrowhead_length = abs_arrowhead_length
        self.abs_arrowhead_width = abs_arrowhead_width
        self.abs_tail_width = abs_tail_width

        self.points = None

    def make_dimensions_absolute(self,
                                 arrowhead_length=True,
                                 arrowhead_width=True,
                                 tail_width=True):

        length = abs(self.length)
        if arrowhead_length and self.rel_arrowhead_length:
            self.abs_arrowhead_length = self.rel_arrowhead_length * length
            self.rel_arrowhead_length = 0
        if arrowhead_width and self.rel_arrowhead_width:
            self.abs_arrowhead_width = self.rel_arrowhead_width * length
            self.rel_arrowhead_width = 0
        if tail_width and self.rel_tail_width:
            self.abs_tail_width = self.rel_tail_width * length
            self.rel_tail_width = 0

    def _recalculate_points(self):

        length = self.length
        sgn = sign(length)
        length *= sgn

        al = self.abs_arrowhead_length or self.rel_arrowhead_length * length
        al = al if al else 0.25 * length

        aw = self.abs_arrowhead_width or self.rel_arrowhead_width * length
        aw = aw if aw else 1.1547 * al  # const = 2/sqrt(3)

        tw = self.abs_tail_width or self.rel_tail_width * length
        tw = tw if tw else 0.1 * length

        if al > length:
            ratio = length / al
            al *= ratio
            aw *= ratio

        return [
            QPointF(self.head, 0),
            QPointF(self.head - al * sgn, aw / 2),
            QPointF(self.head - al * sgn, tw / 2),
            QPointF(self.tail, tw / 2),
            QPointF(self.tail, -tw / 2),
            QPointF(self.head - al * sgn, -tw / 2),
            QPointF(self.head - al * sgn, -aw / 2)
        ]

    @property
    def length(self):

        return self.head - self.tail

    def get(self, xtranslate=0, ytranslate=0):

        if not self.points:
            self.points = self._recalculate_points()

        polygon = QPolygonF(self.points)
        polygon.translate(xtranslate, ytranslate)
        return polygon


if __name__ == "__main__":

    from custom_utils.qt import Canvas, qt_app
    from PyQt5.QtCore import Qt

    c = Canvas()

    def redraw():

        c.p.setPen(Qt.NoPen)
        c.p.setBrush(Qt.black)
        c.p.translate(250, 250)
        arr = Arrow(-50, 50, rel_arrowhead_length=0.5)
        c.p.drawPolygon(arr.get())

    c.redraw = redraw

    qt_app(c)
