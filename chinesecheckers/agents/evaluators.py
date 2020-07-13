import math
import random
from typing import Callable, Dict

from chinesecheckers.agents import SLOT_ENDPOINTS, WIN_SLOTS, generate_slot_coords
from chinesecheckers.agents.GameBoardNode import GameBoardNode


def _generate_random_evaluator(root: GameBoardNode) -> Callable[[GameBoardNode], float]:
    def _random_evaluator(node: GameBoardNode) -> float:
        return random.randint(1, 100)

    return _random_evaluator


def _generate_distance_evaluator(root: GameBoardNode) -> Callable[[GameBoardNode], float]:
    # use a closure to precompute fixed values for the agent
    if WIN_SLOTS[root.num_players] is None:
        raise ValueError("invalid num players")

    # >:( typescript would know that it can't be None (i think...?)
    target_slot: int = WIN_SLOTS[root.num_players][root.agent_player_id-1]  # type: ignore
    endpoint = SLOT_ENDPOINTS[target_slot]
    coords_to_check = sorted(
        tuple(generate_slot_coords(target_slot)),
        key=lambda point: math.hypot(point[0]-endpoint[0], point[1]-endpoint[1]),
    )

    def _distance_evaluator(node: GameBoardNode) -> float:
        i: int = 0
        slot = coords_to_check[0]
        while node.state[slot[0]][slot[1]] == node.agent_player_id:
            i += 1
            if i >= 10:
                return 1000000
            slot = coords_to_check[i]

        dist: float = 0
        for piece in node.pieces[node.agent_player_id]:
            # https://www.redblobgames.com/grids/hexagons/#distances
            dist += (
                abs(piece[0]-slot[0])
                + abs(piece[1]-slot[1])
                + abs(-piece[0]-piece[1]+slot[0]+slot[1])
            ) / 2

        # impossible for dist to be 0
        return 1000/dist

    return _distance_evaluator


evaluators: Dict[str, Callable[[GameBoardNode], Callable[[GameBoardNode], float]]] = {
    "random": _generate_random_evaluator,
    "distance": _generate_distance_evaluator,
}
