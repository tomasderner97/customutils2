from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPolygonF
from math import sqrt


class Box:

    def __init__(self, left, top, right, bottom):
        """
        Helper class for Qt QPainter graphics. 
        Holds information about a rectangle, usable for drawRect, drawEllipse...
        Origin point is always 0,0
        Is callable, call returns QRectF
        """

        if left > right:
            raise ValueError("'left' must be smaller than 'right'")
        if top > bottom:
            raise ValueError("'top' must be smaller than 'bottom'")

        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):

        return self.right - self.left

    @property
    def height(self):

        return self.bottom - self.top

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
            self.top = -hratio * height
            self.bottom = (1 - hratio) * height

    def __call__(self, xtranslate=0, ytranslate=0):
        """
        Returns QRectF, can be translate by xtranslate, ytranslate
        """

        # docs: QRectF(qreal x, qreal y, qreal width, qreal height)
        return QRectF(self.left + xtranslate, self.top + ytranslate, self.width, self.height)


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
                 head,
                 tail=0,
                 arrowhead_length=None,
                 arrowhead_width=None,
                 tail_width=None,
                 relative=True):
        """
        Helper class for Qt QPainter graphics. 
        Creates a down facing arrow as a QPolygonF
        Origin point is always 0,0
        Is callable, call returns QPolygonF
        arrow dimensions are by default relative to length, absolute dimensions can be set
        """

        if not relative and not (arrowhead_length and arrowhead_width and tail_width):
            raise ValueError("'relative' cannot be set to False without providing all dimensions")

        if tail > head:
            raise ValueError("'tail' must be smaller than 'head'")

        if not arrowhead_length:
            arrowhead_length = 0.25

        if not arrowhead_width:
            arrowhead_width = 2 / sqrt(3) * arrowhead_length

        if not tail_width:
            tail_width = 0.1

        self.head = head
        self.tail = tail
        self.arrowhead_length = arrowhead_length
        self.arrowhead_width = arrowhead_width
        self.tail_width = tail_width
        self.relative = relative

        self.points = self._recalculate_points()

    def set_origin(self, ratio):
        """
        Set new origin as a ratio of length away from tail.
        """

        length = self.length
        self.tail = -ratio * length
        self.head = (1 - ratio) * length
        self._recalculate_points()

    def _recalculate_points(self):

        if self.relative:
            length = self.length
            al = self.arrowhead_length * length
            aw = self.arrowhead_width * length
            tw = self.tail_width * length
        else:
            al = self.arrowhead_length
            aw = self.arrowhead_width
            tw = self.tail_width

        return [
            QPointF(0, self.head),
            QPointF(aw / 2, self.head - al),
            QPointF(tw / 2, self.head - al),
            QPointF(tw / 2, self.tail),
            QPointF(-tw / 2, self.tail),
            QPointF(-tw / 2, self.head - al),
            QPointF(-aw / 2, self.head - al)
        ]

    @property
    def length(self):

        return self.head - self.tail

    def __call__(self, xtranslate=0, ytranslate=0):

        polygon = QPolygonF(self.points)
        polygon.translate(xtranslate, ytranslate)
        return polygon


class save:
    """
    Class for with block, remembers and restores current transformation.
    """

    def __init__(self, painter):

        self.painter = painter

    def __enter__(self):

        self.painter.save()

    def __exit__(self, *args):

        self.painter.restore()


from PyQt5.QtCore import Qt
