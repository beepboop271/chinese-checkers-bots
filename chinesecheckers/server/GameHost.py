import json
import random
import time
import socketserver

from typing import Tuple, cast, BinaryIO, List, Optional, Union

from chinesecheckers.server.GameBoard import GameBoard
from chinesecheckers.server.Player import Player
from chinesecheckers.Point2D import Point2D

_ClientPayload = Union[int, bool, List[List[int]]]


class GameHost(socketserver.ThreadingTCPServer):
    class GameTCPHandler(socketserver.StreamRequestHandler):
        def receive(self) -> Tuple[str, _ClientPayload]:
            data = json.loads(self.rfile.readline().strip())
            return (
                data.get("msg", "error"),
                data.get("payload")
            )

        def handle(self) -> None:
            msg, data = self.receive()
            if not (msg == "hello" and data == 12345):
                self.wfile.write(bytes('{"msg": "what"}', "ascii"))
                return

            # mypy thinks self.server is a socketserver.BaseServer
            # when in fact it is a GameHost from this file
            game = cast(GameHost, self.server)

            if not game.accepting_players:
                self.wfile.write(bytes('{"msg": "no"}', "ascii"))
                return

            player = game.create_player(self.rfile, self.wfile)
            if player.PLAYER_ID == 1:
                while not (msg == "ready" and data):
                    msg, data = self.receive()
                game.create_game()

            while True:
                msg, data = self.receive()

                if msg == "make_move":
                    assert isinstance(data, List)
                    game.maybe_do_move(data, player.PLAYER_ID)

    __slots__ = (
        "_players",
        "_running",
        "_accepting_players",
        "_num_players",
        "_board",
        "_current_player",
    )

    def __init__(self, host: str, port: int) -> None:
        super().__init__((host, port), GameHost.GameTCPHandler)
        self._players: List[Player] = []
        self._running: bool = True
        self._accepting_players: bool = True

    def __enter__(self) -> "GameHost":
        # silly mypy thinks that doing "with GameHost(..) as server"
        # returns a socketserver.BaseServer unless i add this...
        return self

    def create_player(self, rfile: BinaryIO, wfile: BinaryIO) -> Player:
        player = Player(rfile, wfile, len(self._players)+1)
        self._players.append(player)
        player.send("assign_id", str(player.PLAYER_ID))
        return player

    def create_game(self) -> None:
        self._accepting_players = False
        self._num_players = len(self._players)
        self._board = GameBoard(self._num_players, True)

        self._current_player = random.randint(0, self._num_players-1)

        self._broadcast(0, "board_init", str(self._board))
        self._broadcast(0, "starting_player", str(self._current_player+1))
        time.sleep(1)

        self._request_next_move()

    def maybe_do_move(self, hops: List[List[int]], player_id: int) -> None:
        if player_id != self._current_player:
            return

        hop_points = [Point2D(p[0], p[1]) for p in hops]
        if self._board.maybe_do_move(hop_points, player_id):
            self._broadcast(0, "move", str(hops))
            if self._board.remaining_players > 0:
                time.sleep(0.5)
                self._request_next_move()
            else:
                self._broadcast(0, "game_over")
                self._running = False

    def _request_next_move(self) -> None:
        self._current_player = (self._current_player+1) % (self._num_players+1)
        if self._current_player == 0:
            self._current_player = 1

        while self._board.is_winner(self._current_player):
            self._current_player = (self._current_player+1) % (self._num_players+1)
            if self._current_player == 0:
                self._current_player = 1
        self._message_player(self._current_player, "request_move")

    def _broadcast(
        self,
        exclude_id: int,
        msg: str,
        payload: Optional[str] = None
    ) -> None:
        for player in self._players:
            if player.PLAYER_ID != exclude_id:
                player.send(msg, payload)

    def _message_player(
        self,
        player_id: int,
        msg: str,
        payload: Optional[str] = None
    ) -> None:
        for player in self._players:
            if player.PLAYER_ID == player_id:
                player.send(msg, payload)

    @property
    def running(self) -> bool:
        return self._running

    @property
    def accepting_players(self) -> bool:
        return self._accepting_players
