from math import acos, degrees


class Vector2D:

    def __init__(self, x, y):

        self._x = x
        self._y = y

        self._abs = None

    @property
    def x(self):

        return self._x

    @property
    def y(self):

        return self._y

    def normalized(self):

        norm = abs(self)
        return Vector2D(self.x / norm, self.y / norm)

    def norm(self, p=2):

        return (self.x**p + self.y**p)**(1 / p)

    def normal(self):

        return Vector2D(self.y, -self.x)

    def angle(self, second=None, deg=False):
        """
        Returns the angle between self and second vector. If no second vector is passed, 
        returns its angle from horizontal. If deg is True, retruns degrees, default is radians
        """

        if not second:
            second = Vector2D(1, 0)

        angle_radians = acos(self @ second / (abs(self) * abs(second)))

        if deg:
            return degrees(angle_radians)
        else:
            return angle_radians

    def get(self):

        return self.x, self.y

    def __add__(self, second):

        return Vector2D(self.x + second.x, self.y + second.y)

    def __sub__(self, second):

        return Vector2D(self.x - second.x, self.y - second.y)

    def __mul__(self, scalar):

        return Vector2D(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):

        return Vector2D(self.x / scalar, self.y / scalar)

    def __matmul__(self, second):

        return self.x * second.x + self.y * second.y

    def __neg__(self):

        return Vector2D(-self.x, -self.y)

    def __abs__(self):
        """ Returns the absolute value of the vector, meaning euclidean norm. Is lazy. """

        if self._abs is None:
            self._abs = (self.x**2 + self.y**2)**0.5

        return self._abs

    def __eq__(self, second):

        return self.x == second.x and self.y == second.y

    def __repr__(self):

        return f"Vector2D(x={self.x}, y={self.y})"


def main():

    pass


if __name__ == '__main__':
    main()
