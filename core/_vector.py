from math import acos


class Vector2D:

    def __init__(self, x, y):

        self._x = x
        self._y = y

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

    def angle(self, second):

        return acos(self @ second / (abs(self) * abs(second)))

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

        return (self.x**2 + self.y**2)**0.5

    def __eq__(self, second):

        return self.x == second.x and self.y == second.y

    def __repr__(self):

        return f"Vector2D(x={self.x}, y={self.y})"


def main():

    pass


if __name__ == '__main__':
    main()
