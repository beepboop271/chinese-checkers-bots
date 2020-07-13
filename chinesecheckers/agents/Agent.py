import abc
import socket
import threading
import time
import json

from typing import Callable, List, Optional, Tuple, Union, cast

from chinesecheckers.agents.GameBoardNode import GameBoardNode

_ClientPayload = Optional[Union[str, List[Tuple[int, int]]]]
_ServerMessage = Optional[Union[int, List[List[int]]]]


class Agent(abc.ABC):
    __slots__ = (
        "_server",
        "_player_id",
        "_board",
        "_evaluator",
        "_root",
    )

    def __init__(
        self,
        host: str,
        port: int,
        evaluator: Callable[[GameBoardNode], Callable[[GameBoardNode], float]]
    ) -> None:
        self._server = socket.socket()
        self._server.connect((host, port))
        self._send("hello", "12345")

        msg, payload = self._receive()
        if msg == "no":
            raise RuntimeError("server not accepting new players")
        if msg != "assign_id":
            raise RuntimeError("wtf")
        self._player_id = cast(int, payload)

        self._evaluator = evaluator

    def _send(self, msg: str, payload: _ClientPayload) -> None:
        print(
            f'sending {{"msg": "{msg}", "payload": {payload}}}\n'
                .replace("(", "[")  # noqa - flake8 wants it one tab left, which is nonsense
                .replace(")", "]")
        )
        self._server.send(bytes(
            f'{{"msg": "{msg}", "payload": {payload}}}\n'
                .replace("(", "[")  # noqa
                .replace(")", "]"),
            "ascii"
        ))

    def _receive(self) -> Tuple[str, _ServerMessage]:
        msg: List[bytes] = []
        while len(msg) == 0 or msg[-1][-1] != ord("}"):
            msg.append(self._server.recv(256))
        data = json.loads(b"".join(msg))  # type: ignore
        print(data)
        return (
            data.get("msg", "error"),
            data.get("payload", None)
        )

    def play(self) -> None:
        msg, payload = self._receive()
        if msg != "board_init":
            raise RuntimeError("wtf 2")
        self._board = cast(List[List[int]], payload)

        msg, payload = self._receive()
        if msg != "starting_player":
            raise RuntimeError("wtf 3")
        starting_player = cast(int, payload)

        self._root = GameBoardNode.root_init(
            self._board,
            self._evaluator,
            self._player_id,
            starting_player
        )

        print("ready")
        game_over_flag = threading.Event()
        explore_flag = threading.Event()
        sock_thread = threading.Thread(
            target=self.handle_incoming,
            args=(game_over_flag, explore_flag),
            daemon=True,
        )
        sock_thread.start()
        self.manage_tree_forever(game_over_flag, explore_flag)

    def handle_incoming(
        self,
        game_over_flag: threading.Event,
        explore_flag: threading.Event,
    ) -> None:
        while True:
            msg, payload = self._receive()
            if msg == "move":
                payload = cast(List[List[int]], payload)
                source = payload[0]
                dest = payload[-1]
                self._board[dest[0]][dest[1]] = self._board[source[0]][source[1]]
                self._board[source[0]][source[1]] = 0
                k = cast(Tuple[Tuple[int, int], Tuple[int, int]], (tuple(source), tuple(dest)))
                if k not in self._root.children:
                    print("aaaaaaaaaaaaaaaaaaaaaaaaaa")
                    self.expand_once()

                old_root = self._root
                self._root = self._root.children.pop(k)
                hi = time.perf_counter_ns()
                p = old_root.prune()
                print(time.perf_counter_ns()-hi, "ns to prune", p)
                self._root.parent = None
                self._root.score = 0
            elif msg == "request_move":
                explore_flag.set()
                print("set move")
                time.sleep(3)
                explore_flag.clear()
                print("clear move", self._root.current_player_id)
                self._send("make_move", self._root.best_child.hop_chain)  # type: ignore
            elif msg == "game_over":
                game_over_flag.set()
                self._server.close()
                return
            else:
                raise RuntimeError("wtf 4")

    def expand_once(self) -> None:
        root = self._root
        pieces = root.pieces[root.current_player_id]
        for piece in pieces:
            moves = root.get_moves_from_point(piece)
            for hop_chain in moves.values():
                new = GameBoardNode(root, hop_chain)
                root.children[(piece, hop_chain[-1])] = new
                new.backprop_max()

    @abc.abstractmethod
    def manage_tree_forever(
        self,
        game_over_flag: threading.Event,
        explore_flag: threading.Event,
    ) -> None:
        pass
