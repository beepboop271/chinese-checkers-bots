import collections
import threading
import time

from typing import Deque

from chinesecheckers.agents.Agent import Agent
from chinesecheckers.agents.GameBoardNode import GameBoardNode


class MaxAgent(Agent):
    __slots__ = ("d", "pruned", "popped")

    def manage_tree_forever(
        self,
        game_over_flag: threading.Event,
        explore_flag: threading.Event,
    ) -> None:
        d: Deque[GameBoardNode] = collections.deque()
        self.d = d
        self.pruned = 0
        self.popped = 0

        # log_thread = threading.Thread(
        #     target=self.periodically_log,
        #     daemon=True
        # )
        # log_thread.start()

        while self._root is None:
            pass

        d.append(self._root)

        while True:
            if explore_flag.is_set():
                if len(d) == 0:
                    print("ROOT APPEND")
                    d.append(self._root)
                node = d.popleft()

                if not node.pruned:
                    self.popped += 1
                    pieces = node.pieces[node.current_player_id]
                    for piece in pieces:
                        moves = node.get_moves_from_point(piece)
                        for hop_chain in moves.values():
                            new = GameBoardNode(node, hop_chain)
                            node.children[(piece, hop_chain[-1])] = new
                            new.backprop_max()
                            d.append(new)
                else:
                    self.pruned += 1
            else:
                if game_over_flag.is_set():
                    return
                if len(d) > 0:
                    print("CLEAR")
                    d.clear()

    def periodically_log(self) -> None:
        while True:
            time.sleep(1)
            print("log", len(self.d), self.popped, self.d[-1].depth-self._root.depth if len(self.d) > 1 else 0, sorted([(str(c), round(1000/c.score)) for c in self._root.children.values()], key=lambda x: x[1], reverse=True))
