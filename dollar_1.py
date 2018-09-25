import functools

from math import atan2, cos, sin
from shape_base import Point


def recognizeShape(shape):
    """$1 algorithm to recognize shape

    Parameters
    ----------

    shape : Shape
        shape to be recognized

    Returns
    -------

    shape_type : str
        type of this shape
    """
    # get all points of this shape
    lines = shape.lines
    points = []
    for line in lines:
        points += line.points

    return resample(points, 128)


def resample(points, n):
    """Resample a points path into n evenly spaced points."""
    assert 32 <= n <= 256
    assert len(points) >= 1

    increment = path_length(points) / (n - 1)
    accumulative_dist = 0
    new_points = [points[0]]
    latest_inserted_point = None

    i = 1
    while i < len(points):
        if latest_inserted_point is not None:
            previous_point = latest_inserted_point
            latest_inserted_point = None
        else:
            previous_point = points[i - 1]

        dist = points[i].dist_to(previous_point)
        if accumulative_dist + dist > increment:
            excess_to_dist_ratio = (increment - accumulative_dist) / dist
            new_x = (points[i].x - previous_point.x) * excess_to_dist_ratio + previous_point.x
            new_y = (points[i].y - previous_point.y) * excess_to_dist_ratio + previous_point.y
            new_point = Point(new_x, new_y)
            new_points.append(new_point)
            # let new point be next start point
            latest_inserted_point = new_point
            i -= 1
            accumulative_dist = 0
        else:
            accumulative_dist += dist

        i += 1

    return new_points


def path_length(points):
    dist = 0
    for i in range(1, len(points)):
        dist += points[i].dist_to(points[i - 1])

    return dist


def rotate_to_zero(points):
    centroid = find_centroid(points)
    theta = atan2(centroid.y - points[0].y, centroid.x - points[0].x)
    return rotate_by(points, theta)


def find_centroid(points):
    p_sum = functools.reduce(lambda a, b: a + b, points)
    return Point(p_sum.x / len(points), p_sum.y / len(points))


def rotate_by(points, theta):
    centroid = find_centroid(points)
    new_points = []
    for point in points:
        x = (point.x - centroid.x) * cos(theta) - (point.y - centroid.y) * sin(theta) + centroid.x
        y = (point.x - centroid.x) * sin(theta) + (point.y - centroid.y) * cos(theta) + centroid.y
        new_points.append(Point(x, y))

    return new_points


def scale_to_square(points, size):
    new_points = []
    width, height = bounding_box(points)
    for p in points:
        x = p.x * (size / width)
        y = p.y * (size / height)
        new_points.append(Point(x, y))

    return new_points


def bounding_box(points):
    assert len(points) >= 1

    max_x = min_x = points[0].x
    max_y = min_y = points[0].y

    for point in points:
        if point.x < min_x:
            min_x = point.x
        if point.y < min_y:
            min_y = point.y

        if point.x > max_x:
            max_x = point.x
        if point.y > max_y:
            max_y = point.y

    # width and height
    return max_x - min_x, max_y - min_y


def translate_to_origin(points):
    centroid = find_centroid(points)
    new_points = []
    for p in points:
        x = p.x - centroid.x
        y = p.y - centroid.y
        new_points.append(Point(x, y))

    return new_points
