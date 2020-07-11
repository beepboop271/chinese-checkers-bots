from typing import List

from chinesecheckers import BOARD_SIZE
from chinesecheckers.Point2D import Point2D
from chinesecheckers.Point3D import Point3D


class GameBoard(object):
    __slots__ = ("_num_players", "_board", "_win_statuses", "_remaining_players")

    def __init__(self, num_players: int, initialize_board: bool = False):
        self._num_players: int = num_players
        self._board: List[List[int]] = []
        self._win_statuses: List[bool] = [False] * (num_players+1)
        self._remaining_players: int = num_players
        if initialize_board:
            self.reset()

    def __str__(self) -> str:
        return str(self._board)

    def get_copy(self) -> "GameBoard":
        new_board = GameBoard(self._num_players)
        new_board._board = []

        for row in self._board:
            new_board._board.append(list(row))

        return new_board

    def reset(self) -> None:
        if self._num_players == 2:
            self._board = [
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2,  2,  2],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2,  2, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [ 1,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            ]
        elif self._num_players == 3:
            self._board = [
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  3,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  2, -1, -1, -1, -1],
                [-1, -1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  2,  2, -1, -1, -1, -1],
                [-1,  1,  1,  1,  0,  0,  0,  0,  0,  0,  2,  2,  2, -1, -1, -1, -1],
                [ 1,  1,  1,  1,  0,  0,  0,  0,  0,  2,  2,  2,  2, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            ]
        elif self._num_players == 4:
            self._board = [
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  3,  3, -1, -1, -1, -1],
                [-1, -1, -1, -1,  4,  4,  4,  4,  0,  0,  0,  0,  0,  0,  0,  0,  0],
                [-1, -1, -1, -1,  4,  4,  4,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1],
                [-1, -1, -1, -1,  4,  4,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1],
                [-1, -1, -1, -1,  4,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1],
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                [-1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2, -1, -1, -1, -1],
                [-1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2, -1, -1, -1, -1],
                [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2,  2, -1, -1, -1, -1],
                [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2,  2,  2, -1, -1, -1, -1],
                [-1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            ]
        elif self._num_players == 6:
            self._board = [
                # 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  5, -1, -1, -1, -1],  # 0
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  5,  5, -1, -1, -1, -1],  # 1
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  5,  5,  5, -1, -1, -1, -1],  # 2
                [-1, -1, -1, -1, -1, -1, -1, -1, -1,  5,  5,  5,  5, -1, -1, -1, -1],  # 3
                [-1, -1, -1, -1,  6,  6,  6,  6,  0,  0,  0,  0,  0,  4,  4,  4,  4],  # 4
                [-1, -1, -1, -1,  6,  6,  6,  0,  0,  0,  0,  0,  0,  4,  4,  4, -1],  # 5
                [-1, -1, -1, -1,  6,  6,  0,  0,  0,  0,  0,  0,  0,  4,  4, -1, -1],  # 6
                [-1, -1, -1, -1,  6,  0,  0,  0,  0,  0,  0,  0,  0,  4, -1, -1, -1],  # 7
                [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],  # 8
                [-1, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  3, -1, -1, -1, -1],  # 9
                [-1, -1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  3,  3, -1, -1, -1, -1],  # 10
                [-1,  1,  1,  1,  0,  0,  0,  0,  0,  0,  3,  3,  3, -1, -1, -1, -1],  # 11
                [ 1,  1,  1,  1,  0,  0,  0,  0,  0,  3,  3,  3,  3, -1, -1, -1, -1],  # 12
                [-1, -1, -1, -1,  2,  2,  2,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 13
                [-1, -1, -1, -1,  2,  2,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 14
                [-1, -1, -1, -1,  2,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 15
                [-1, -1, -1, -1,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 16
            ]
        else:
            raise ValueError(f"Invalid number of players: {self._num_players}")

    def in_board(self, point: Point2D) -> bool:
        return (
            point.x >= 0
            and point.x < BOARD_SIZE
            and point.y >= 0
            and point.y < BOARD_SIZE
        )

    def maybe_do_move(self, hops: List[Point2D], player_id: int) -> bool:
        if not self.in_board(hops[0]):
            return False

        source_x = hops[0].x
        source_y = hops[0].y
        if self._board[source_x][source_y] != player_id:
            # Cannot move a piece that is not your own
            return False

        piece = self._board[source_x][source_y]
        self._board[source_x][source_y] = 0
        if len(hops) == 2:
            # possible adjacent hop
            if not self.is_valid_hop(hops[0], hops[1], True):
                self._board[source_x][source_y] = piece
                return False
        else:
            for i in range(len(hops)-1):
                if not self.is_valid_hop(hops[i], hops[i+1], False):
                    self._board[source_x][source_y] = piece
                    return False

        self._board[hops[-1].x][hops[-1].y] = piece
        self._check_winners()
        return True

    def is_valid_hop(
        self,
        source: Point2D,
        dest: Point2D,
        allow_single: bool,
    ) -> bool:
        if not (self.in_board(source) and self.in_board(dest)):
            # out of bounds
            return False

        if self._board[dest.x][dest.y] != 0:
            # destination isn't empty
            return False

        source_3d = Point3D.from_2d(source)
        dest_3d = Point3D.from_2d(dest)

        step = Point3D.board_normalize(source_3d, dest_3d)

        if step is None:
            # hop is not in a straight line
            return False

        dx = step.x
        dy = step.y
        cur_x = source.x+dx
        cur_y = source.y+dy
        gaps: List[int] = [0]
        while not (cur_x == dest.x and cur_y == dest.y):
            if self._board[cur_x][cur_y] == 0:
                gaps[-1] += 1
            else:
                if len(gaps) == 2:
                    # more than one piece in between
                    return False
                gaps.append(0)
            cur_x += dx
            cur_y += dy

        if len(gaps) == 1:
            return gaps[0] == 0 and allow_single
        else:
            return gaps[0] == gaps[1]

    # slot: one of the triangles surrounding the board where
    # pieces start and end in. slot 0 is the top most, then
    # ascending clockwise
    _SLOT_BOUNDS = (
        (9, 12, 3, False),
        (13, 16, 4, True),
        (9, 12, 12, False),
        (4, 7, 13, True),
        (0, 3, 12, False),
        (4, 7, 4, True),
    )

    def _check_slot(
        self,
        slot_number: int,
        player_id: int,
    ) -> bool:
        start_x, end_x, y_edge, pointing_up = GameBoard._SLOT_BOUNDS[slot_number]
        if pointing_up:
            scan = 4
            for x in range(start_x, end_x+1):
                for y in range(y_edge, y_edge+scan):
                    print("check", x, y, "for", player_id)
                    if self._board[x][y] != player_id:
                        return False
                scan -= 1
            return True
        else:
            scan = 0
            for x in range(start_x, end_x+1):
                for y in range(y_edge-scan, y_edge+1):
                    if self._board[x][y] != player_id:
                        return False
                scan += 1
            return True

    # _WIN_SLOTS[i][j] is the slot that player j+1
    # needs to fill to win, in a game of i players
    _WIN_SLOTS = (
        None,
        None,
        (3, 0),
        (4, 0, 2),
        (4, 5, 1, 2),
        None,
        (3, 4, 5, 0, 1, 2),
    )

    def _check_winners(self) -> None:
        slots = GameBoard._WIN_SLOTS[self._num_players]
        if slots is None:
            raise ValueError("bad num players")

        for i in range(len(slots)):
            print("check slot", slots[i], "for player", i+1)
            if not self._win_statuses[i+1] and self._check_slot(slots[i], i+1):
                self._remaining_players -= 1
                self._win_statuses[i+1] = True
        print(self._win_statuses)

    def is_winner(self, player_id: int) -> bool:
        return self._win_statuses[player_id]

    @property
    def remaining_players(self) -> int:
        return self._remaining_players
