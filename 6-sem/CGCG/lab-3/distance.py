import math
from point import Point


def dist(p1: Point, p2: Point) -> float:
    return math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y))
