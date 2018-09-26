import functools
from math import cos, sin, sqrt, atan, pi

from shape_base import Point, Shape

golden_ratio = 0.5 * (sqrt(5) - 1)
resample_points_num = 128
reference_square_size = 50
theta_upper = pi / 4
theta_lower = - pi / 4
theta_threshold = 2. * pi / 180


def recognize_shape(shape, templates):
    """$1 algorithm to recognize shape

    Parameters
    ----------

    shape : Shape
        shape to be recognized

    templates : list
        list of templates(shape)

    Returns
    -------

    matched_shape : Shape
        type of this shape
    """
    # get all points of this shape
    points = shape.points
    points = resample(points, resample_points_num)
    points = rotate_to_zero(points)
    points = scale_to_square(points, reference_square_size)
    points = translate_to_origin(points)

    templates = process_raw_templates(templates)

    return recognize(points, templates)


def process_raw_templates(templates):
    new_templates = []
    for t in templates:
        points = t.points
        points = resample(points, resample_points_num)
        points = rotate_to_zero(points)
        points = scale_to_square(points, reference_square_size)
        points = translate_to_origin(points)
        new_t = Shape.from_points(points)
        new_t.tag = t.tag
        new_templates.append(new_t)

    return new_templates


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
    theta = atan((centroid.y - points[0].y) / (centroid.x - points[0].x))
    return rotate_by(points, -theta)


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


def recognize(points, templates):
    matched_result = None
    min_dist = float('inf')

    for template in templates:
        assert isinstance(template, Shape)
        template_points = template.points
        dist = distance_at_best_angle(points, template_points, theta_lower, theta_upper, theta_threshold)
        if dist < min_dist:
            matched_result = template
            min_dist = dist

    return matched_result


def distance_at_best_angle(points, template, lower_bound_angle, upper_bound_angle, threshold):
    x_1 = upper_bound_angle - (upper_bound_angle - lower_bound_angle) * golden_ratio
    x_2 = lower_bound_angle + (upper_bound_angle - lower_bound_angle) * golden_ratio

    f_1 = distance_at_angle(points, template, x_1)
    f_2 = distance_at_angle(points, template, x_2)

    while abs(upper_bound_angle - lower_bound_angle) > threshold:
        if f_1 < f_2:
            upper_bound_angle = x_2
            x_2 = x_1
            f_2 = f_1
            x_1 = upper_bound_angle - (upper_bound_angle - lower_bound_angle) * golden_ratio
            f_1 = distance_at_angle(points, template, x_1)
        else:
            lower_bound_angle = x_1
            x_1 = x_2
            f_1 = f_2
            x_2 = lower_bound_angle + (upper_bound_angle - lower_bound_angle) * golden_ratio
            f_2 = distance_at_angle(points, template, x_2)

    return min(f_1, f_2)


def distance_at_angle(points, template, angle):
    new_points = rotate_by(points, angle)
    return path_distance(new_points, template)


def path_distance(path_a, path_b):
    distance = 0
    for i, j in zip(path_a, path_b):
        distance += i.dist_to(j)

    return distance / len(path_a)
