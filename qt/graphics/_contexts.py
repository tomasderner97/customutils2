class scale:

    def __init__(self, painter, x, y=0):
        """
        Class for with block, remembers and restores current transformation and scales painter.

        Parameters
        ----------
        painter : QPainter
        x : float
            Scale factor for x
        y : float
            Scale factor for y
        """

        self.x = x
        self.y = y if y else x

        self.painter = painter

    def __enter__(self):

        self.painter.save()
        self.painter.scale(self.x, self.y)

    def __exit__(self, *args):

        self.painter.restore()


class rotate:

    def __init__(self, painter, angle):
        """
        Class for with block, remembers and restores current transformation and rotates painter.

        Parameters
        ----------
        painter : QPainter
        angle : float
            Angle to rotate in degrees
        """

        self.angle = angle
        self.painter = painter

    def __enter__(self):

        self.painter.save()
        self.painter.rotate(self.angle)

    def __exit__(self, *args):

        self.painter.restore()


class translate:

    def __init__(self, painter, x=0, y=0):
        """
        Class for with block, remembers and restores current transformation and translates painter.

        Parameters
        ----------
        painter : QPainter
        angle : float
            Angle to rotate in degrees
        """

        self.x = x
        self.y = y
        self.painter = painter

    def __enter__(self):

        self.painter.save()
        self.painter.translate(self.x, self.y)

    def __exit__(self, *args):

        self.painter.restore()


class sensible_coordinates:

    def __init__(self, painter, xtrans=0, ytrans=0, xscale=1, yscale=1, y_axis_up=True):
        """
        Class for with block, sets usual cartesian coordinates.

        Parameters
        ----------
        painter : QPainter
        """

        self.xtrans = xtrans
        self.ytrans = ytrans
        self.xscale = xscale
        self.yscale = yscale
        self.y_axis_up = y_axis_up
        self.painter = painter

    def __enter__(self):

        height = self.painter.device().height()

        self.painter.save()

        if self.y_axis_up:
            self.painter.translate(0, height / 2)
            self.painter.scale(1, -1)
            self.painter.translate(0, -height / 2)

        self.painter.translate(self.xtrans, self.ytrans)
        self.painter.scale(self.xscale, self.yscale)

    def __exit__(self, *args):

        self.painter.restore()
