from chinesecheckers.Point2D import Point2D

BOARD_SIZE = 17


def point_in_board(point: Point2D) -> bool:
    return (
        point.x >= 0
        and point.x < BOARD_SIZE
        and point.y >= 0
        and point.y < BOARD_SIZE
    )


def in_board(x: int, y: int) -> bool:
    return (
        x >= 0
        and x < BOARD_SIZE
        and y >= 0
        and y < BOARD_SIZE
    )
