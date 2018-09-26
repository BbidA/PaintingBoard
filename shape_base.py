import math

from PyQt5.QtCore import QPoint

CIRCLE = 'circle'
TRIANGLE = 'triangle'
SQUARE = 'square'
RECTANGLE = 'rectangle'


class Shape:

    def __init__(self) -> None:
        super().__init__()
        self.__lines = []
        self.__tag = ''

    def __repr__(self):
        return 'Shape(tag={})'.format(self.__tag)

    @classmethod
    def from_points(cls, points):
        line = Line()
        for point in points:
            line.add_point(point)

        shape = cls()
        shape.__lines.append(line)
        return shape

    @property
    def lines(self):
        return self.__lines

    @property
    def points(self):
        p = []
        for line in self.lines:
            p += line.points

        return p

    @property
    def tag(self):
        # self.update_shape_type()
        return self.__tag

    @tag.setter
    def tag(self, t):
        self.__tag = t

    def addLine(self, line):
        assert isinstance(line, Line)
        self.__lines.append(line)

    def clear(self):
        self.__lines.clear()
        self.__tag = ''

    def update_shape_type(self):
        lines_number = len(self.__lines)
        # set tag according to the number of the lines
        self.__tag = {
            1: CIRCLE,
            2: TRIANGLE,
            3: SQUARE,
            4: RECTANGLE
        }.get(lines_number, 'No tags to show')

    def showLinesOnBoard(self, board):
        pass

    def doNormalization(self):
        pass


class Line:

    def __init__(self) -> None:
        super().__init__()
        self.__points = []

    def __getitem__(self, item):
        return self.__points[item]

    def add_point(self, point):
        assert isinstance(point, Point)
        self.__points.append(point)

    def addPoint(self, x, y):
        self.__points.append(Point(x, y))

    def get_q_point(self, position):
        point = self.__points[position]
        return QPoint(point.x, point.y)

    @property
    def q_points(self):
        return [QPoint(a.x, a.y) for a in self.__points]

    @property
    def points(self):
        return self.__points

    def points_number(self):
        return len(self.__points)

    def clear(self):
        self.__points.clear()


class Point:

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def dist_to(self, point):
        return math.sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)
