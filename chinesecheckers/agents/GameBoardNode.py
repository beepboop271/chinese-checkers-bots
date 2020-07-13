import collections

from typing import Callable, Dict, Deque, List, Optional, Set, Tuple

from chinesecheckers import BOARD_SIZE, in_board
from chinesecheckers.agents import WIN_SLOTS, generate_slot_coords

_PossibleMoveList = Dict[Tuple[int, int], List[Tuple[int, int]]]


class GameBoardNode(object):
    __slots__ = (
        "parent",
        "num_players",
        "hop_chain",
        "state",
        "pieces",
        "evaluator",
        "score",
        "win_statuses",
        "remaining_players",
        "current_player_id",
        "agent_player_id",
        "children",
        "best_child",
        "pruned",
        "depth",
    )

    def __init__(
        self,
        parent: Optional["GameBoardNode"] = None,
        hops_from_parent: List[Tuple[int, int]] = [],
    ):
        self.parent = parent
        self.children: Dict[Tuple[Tuple[int, int], Tuple[int, int]], GameBoardNode] = {}
        self.best_child: Optional[GameBoardNode] = None
        self.pruned: bool = False

        if parent is None:
            return

        self.depth: int = parent.depth+1

        self.num_players: int = parent.num_players

        self.hop_chain = hops_from_parent

        self.state: List[List[int]] = [
            list(row) for row in parent.state
        ]
        self.pieces: List[Set[Tuple[int, int]]] = [
            piece_set.copy() for piece_set in parent.pieces
        ]

        self.win_statuses: List[bool] = list(parent.win_statuses)
        self.remaining_players: int = parent.remaining_players

        self.current_player_id: int = parent.current_player_id
        self.evaluator: Callable[[GameBoardNode], float] = parent.evaluator

        self.agent_player_id: int = parent.agent_player_id

        self._do_move()

        self.current_player_id = (parent.current_player_id+1) % (self.num_players+1)
        if self.current_player_id == 0:
            self.current_player_id = 1
        while self.win_statuses[self.current_player_id]:
            self.current_player_id = (self.current_player_id+1) % (self.num_players+1)
            if self.current_player_id == 0:
                self.current_player_id = 1

    @staticmethod
    def root_init(
        board: List[List[int]],
        evaluator: Callable[["GameBoardNode"], Callable[["GameBoardNode"], float]],
        agent_player_id: int,
        current_player_id: int,
    ) -> "GameBoardNode":
        new = GameBoardNode()
        num_players = max(max(row) for row in board)
        new.num_players = num_players
        new.state = [list(row) for row in board]
        new.pieces = [set() for _ in range(num_players+1)]
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                p = board[x][y]
                if p > 0:
                    new.pieces[p].add((x, y))
        new.win_statuses = [False] * (num_players+1)
        new.remaining_players = num_players
        new.score = 0
        new.agent_player_id = agent_player_id
        new.current_player_id = current_player_id
        new.depth = 0
        new.evaluator = evaluator(new)
        return new

    def _do_move(self) -> None:
        dest = self.hop_chain[-1]
        source = self.hop_chain[0]
        self.state[dest[0]][dest[1]] = self.state[source[0]][source[1]]
        self.state[source[0]][source[1]] = 0
        self._check_winners()
        self.pieces[self.current_player_id].remove(source)
        self.pieces[self.current_player_id].add(dest)
        self.score = self.evaluator(self)

    def _check_slot(
        self,
        slot_number: int,
        player_id: int,
    ) -> bool:
        for x, y in generate_slot_coords(slot_number):
            if self.state[x][y] != player_id:
                return False
        return True

    def _check_winners(self) -> None:
        slots = WIN_SLOTS[self.num_players]
        if slots is None:
            raise ValueError("bad num players")

        for i in range(len(slots)):
            if not self.win_statuses[i+1] and self._check_slot(slots[i], i+1):
                self.remaining_players -= 1
                self.win_statuses[i+1] = True

    def _scan(
        self,
        source_x: int, source_y: int,
        dx: int, dy: int
    ) -> Optional[Tuple[int, int]]:
        cur_x = source_x+dx
        cur_y = source_y+dy
        if not in_board(cur_x, cur_y):
            return None

        dist = 1
        while self.state[cur_x][cur_y] == 0:
            cur_x += dx
            cur_y += dy
            dist += 1
            if not in_board(cur_x, cur_y):
                return None

        if self.state[cur_x][cur_y] == -1:
            return None

        cur_x += dx
        cur_y += dy
        if not in_board(cur_x, cur_y) or self.state[cur_x][cur_y] != 0:
            return None

        dist -= 1
        while dist > 0:
            cur_x += dx
            cur_y += dy
            dist -= 1
            if not in_board(cur_x, cur_y) or self.state[cur_x][cur_y] != 0:
                return None

        return (cur_x, cur_y)

    _DELTAS = (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (-1, 1),
        (1, -1)
    )

    def get_moves_from_point(
        self,
        source: Tuple[int, int],
    ) -> _PossibleMoveList:
        possible: _PossibleMoveList = {}
        visited = [[False]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        q: Deque[Tuple[int, int]] = collections.deque()
        q.append(source)
        visited[source[0]][source[1]] = True

        original = self.state[source[0]][source[1]]
        self.state[source[0]][source[1]] = 0

        for direction in GameBoardNode._DELTAS:
            x = source[0]+direction[0]
            y = source[1]+direction[1]
            if in_board(x, y) and self.state[x][y] == 0:
                possible[(x, y)] = [source, (x, y)]

        while len(q) > 0:
            p = q.popleft()

            for direction in GameBoardNode._DELTAS:
                maybe_dest = self._scan(p[0], p[1], direction[0], direction[1])
                if maybe_dest is not None and not visited[maybe_dest[0]][maybe_dest[1]]:
                    visited[maybe_dest[0]][maybe_dest[1]] = True
                    q.append(maybe_dest)
                    if p == source:
                        possible[maybe_dest] = [source, maybe_dest]
                    else:
                        new = list(possible[p])
                        new.append(maybe_dest)
                        possible[maybe_dest] = new

        self.state[source[0]][source[1]] = original
        return possible

    def prune(self) -> int:
        self.pruned = True
        pruned = 1
        for child in self.children.values():
            pruned += child.prune()
        return pruned

    def size(self) -> int:
        size = 1
        for child in self.children.values():
            size += child.size()
        return size

    def __str__(self) -> str:
        return str((self.hop_chain[0], self.hop_chain[-1]))

    def backprop_max(self) -> None:
        if self.parent is None:
            return
        if self.score > self.parent.score:
            self.parent.score = self.score
            self.parent.best_child = self
            self.parent.backprop_max()
