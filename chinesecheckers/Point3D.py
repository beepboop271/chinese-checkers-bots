import math
from typing import Optional

from chinesecheckers.Point2D import Point2D

_SQRT_2 = math.sqrt(2)


# https://www.redblobgames.com/grids/hexagons/#coordinates
class Point3D(object):
    __slots__ = ("x", "y", "z")

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.z = -x - y

    def __sub__(self, other: "Point3D") -> "Point3D":
        return Point3D(self.x-other.x, self.y-other.y)

    @staticmethod
    def from_2d(point: Point2D) -> "Point3D":
        return Point3D(point.x, point.y)

    @staticmethod
    def board_normalize(start: "Point3D", end: "Point3D") -> Optional["Point3D"]:
        diff = end - start
        board_dist = math.hypot(diff.x, diff.y, diff.z) / _SQRT_2
        if not board_dist.is_integer():
            return None

        board_dist = int(board_dist)
        return Point3D(diff.x//board_dist, diff.y//board_dist)
