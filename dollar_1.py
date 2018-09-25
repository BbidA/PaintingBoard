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
