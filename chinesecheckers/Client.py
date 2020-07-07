import collections
import json
import socket
import threading

from typing import Deque, Dict, List, Optional, Tuple, Union, cast

import pygame  # type: ignore

HOST = "127.0.0.1"
PORT = 41047

window_size: int = 680
cell_size = window_size // 17
radius = cell_size // 2

BOARD_SIZE = 17

COLOURS = [
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255)
]
NAMES = ["", "red", "green", "blue", "yellow", "magenta", "cyan"]

pygame.init()
comicsans_28 = pygame.font.SysFont("Comic Sans MS", 28)

ClientPayload = Optional[Union[int, str, List[List[int]]]]
ServerMessage = Optional[Union[int, List[int], List[List[int]]]]
PossibleMoveList = Dict[Tuple[int, int], List[List[int]]]


def draw_board(
    surf: pygame.Surface,
    board: List[List[int]],
    is_client_turn: bool,
    possible_moves: PossibleMoveList
) -> None:
    surf.fill((0, 0, 0))

    if is_client_turn:
        surf.blit(
            comicsans_28.render("your turn", True, COLOURS[0]),
            (cell_size*10, 20)
        )

    draw_x_start = -radius * 12
    draw_y = 0
    draw_x = draw_x_start
    if len(possible_moves) > 0:
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                cell = board[x][y]
                if (x, y) in possible_moves:
                    pygame.draw.circle(
                        surf,
                        (255, 128, 0),
                        (draw_x+radius, draw_y+radius),
                        radius
                    )
                if cell >= 0:
                    pygame.draw.circle(
                        surf,
                        COLOURS[cell],
                        (draw_x+radius, draw_y+radius),
                        int(radius*0.8)
                    )
                draw_x += radius
                draw_y += cell_size
            draw_x_start += cell_size
            draw_x = draw_x_start
            draw_y = 0
    else:
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                cell = board[x][y]
                if cell >= 0:
                    pygame.draw.circle(
                        surf,
                        COLOURS[cell],
                        (draw_x+radius, draw_y+radius),
                        int(radius*0.8)
                    )
                draw_x += radius
                draw_y += cell_size
            draw_x_start += cell_size
            draw_x = draw_x_start
            draw_y = 0


def board_coords_from_pixel(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    board_y = pos[1]//cell_size
    if board_y < 0 or board_y >= BOARD_SIZE:
        return None

    board_x = (pos[0] + radius*(12-board_y)) // cell_size
    if board_x < 0 or board_x >= BOARD_SIZE:
        return None

    return (board_x, board_y)


DELTAS = [
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (-1, 1),
    (1, -1)
]


def get_possible(board: List[List[int]], source: Tuple[int, int]) -> PossibleMoveList:
    possible: PossibleMoveList = {}
    visited = [[False]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    q: Deque[Tuple[int, int]] = collections.deque()
    q.append(source)

    for direction in DELTAS:
        x = source[0]+direction[0]
        y = source[1]+direction[1]
        if (
            x >= 0
            and x < BOARD_SIZE
            and y >= 0
            and y < BOARD_SIZE
            and board[x][y] == 0
        ):
            possible[(x, y)] = [[source[0], source[1]], [x, y]]

    while len(q) > 0:
        p = q.popleft()
        print(p)

        for direction in DELTAS:
            dx = direction[0]
            dy = direction[1]
            cur_x = p[0]+dx
            cur_y = p[1]+dy
            dist = 1
            while (
                cur_x >= 0
                and cur_x < BOARD_SIZE
                and cur_y >= 0
                and cur_y < BOARD_SIZE
                and board[cur_x][cur_y] == 0
            ):
                cur_x += dx
                cur_y += dy
                dist += 1
            if (
                cur_x >= 0
                and cur_x < BOARD_SIZE
                and cur_y >= 0
                and cur_y < BOARD_SIZE
                and board[cur_x][cur_y] > 0
            ):
                print("1", cur_x, cur_y, dist)
                cur_x += dx
                cur_y += dy
                dist -= 1
                while (
                    cur_x >= 0
                    and cur_x < BOARD_SIZE
                    and cur_y >= 0
                    and cur_y < BOARD_SIZE
                    and board[cur_x][cur_y] == 0
                    and dist > 0
                ):
                    cur_x += dx
                    cur_y += dy
                    dist -= 1
                if (
                    cur_x >= 0
                    and cur_x < BOARD_SIZE
                    and cur_y >= 0
                    and cur_y < BOARD_SIZE
                    and board[cur_x][cur_y] == 0
                    and dist == 0
                    and not visited[cur_x][cur_y]
                ):
                    print("2", cur_x, cur_y, dist)
                    visited[cur_x][cur_y] = True
                    q.append((cur_x, cur_y))
                    if p == source:
                        possible[(cur_x, cur_y)] = [[source[0], source[1]], [cur_x, cur_y]]
                    else:
                        prev = possible[p]
                        new = list(prev)
                        new.append([cur_x, cur_y])
                        possible[(cur_x, cur_y)] = new

    return possible


with socket.socket() as sock:
    sock.connect((HOST, PORT))

    def send(msg: str, payload: ClientPayload) -> None:
        print(f'sending {{"msg": "{msg}", "payload": {payload}}}\n')
        sock.send(bytes(
            f'{{"msg": "{msg}", "payload": {payload}}}\n',
            "ascii"
        ))

    def receive() -> Tuple[str, ServerMessage]:
        data = json.loads(sock.recv(2048))  # type: ignore
        print(data)
        return (
            data.get("msg", "error"),
            data.get("payload", None)
        )

    send("hello", 12345)
    msg, payload = receive()
    if msg == "no":
        raise RuntimeError("server not accepting new players")
    if msg != "assign_id":
        raise RuntimeError("wtf")

    player_id = cast(int, payload)
    print(f"You are player {player_id} ({NAMES[player_id]})")
    if player_id == 1:
        input("press enter to start the game")
        send("ready", "true")  # str(True) -> "True" which is not valid json

    msg, payload = receive()
    if msg != "board_init":
        raise RuntimeError("wtf 2")
    board = cast(List[List[int]], payload)

    def swap(points: List[int]) -> None:
        p = board[points[0]][points[1]]
        board[points[0]][points[1]] = board[points[2]][points[3]]
        board[points[2]][points[3]] = p

    def handle_incoming(request_move_flag: threading.Event) -> None:
        while True:
            print("wow")
            msg, payload = receive()
            print(msg, payload)
            if msg == "swap":
                swap(cast(List[int], payload))
                request_move_flag.clear()
            elif msg == "request_move":
                request_move_flag.set()
            else:
                raise RuntimeError("wtf 3")

    request_move_flag = threading.Event()
    sock_thread = threading.Thread(
        target=handle_incoming,
        args=(request_move_flag,),
        daemon=True
    )
    sock_thread.start()

    display = pygame.display.set_mode((window_size, window_size), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    running = True
    source: Optional[Tuple[int, int]] = None
    possible_moves: PossibleMoveList = {}

    while running:
        if (not request_move_flag.is_set()
            and (source is not None or len(possible_moves) > 0)
        ):
            source = None
            possible_moves = {}

        draw_board(display, board, request_move_flag.is_set(), possible_moves)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                window_size = min(event.w, event.h)
                window_size = 34 * (window_size//34)
                cell_size = window_size // 17
                radius = cell_size // 2
                display = pygame.display.set_mode(
                    (window_size, window_size),
                    pygame.RESIZABLE
                )
            elif event.type == pygame.QUIT:
                running = False
            elif (event.type == pygame.MOUSEBUTTONUP
                  and request_move_flag.is_set()
            ):
                selected_point = board_coords_from_pixel(event.pos)
                if selected_point is not None:
                    if len(possible_moves) > 0:
                        if selected_point in possible_moves:
                            send("make_move", possible_moves[selected_point])
                        else:
                            source = None
                            possible_moves = {}
                    elif board[selected_point[0]][selected_point[1]] == player_id:
                        source = selected_point
                        possible_moves = get_possible(board, selected_point)

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()
