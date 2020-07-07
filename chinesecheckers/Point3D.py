import math
from typing import Optional

from chinesecheckers.Point2D import Point2D

_SQRT_2 = math.sqrt(2)


# https://www.redblobgames.com/grids/hexagons/#coordinates
class Point3D(object):
    __slots__ = ("_x", "_y", "_z")

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self._z = -x - y

    def __sub__(self, other: "Point3D") -> "Point3D":
        return Point3D(self._x-other._x, self._y-other._y)

    @staticmethod
    def from_2d(point: Point2D) -> "Point3D":
        return Point3D(point.x, point.y)

    @staticmethod
    def board_normalize(start: "Point3D", end: "Point3D") -> Optional["Point3D"]:
        diff = end - start
        board_dist = math.hypot(diff._x, diff._y, diff._z) / _SQRT_2
        if not board_dist.is_integer():
            return None

        board_dist = int(board_dist)
        return Point3D(diff._x//board_dist, diff._y//board_dist)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def z(self) -> int:
        return self._z
