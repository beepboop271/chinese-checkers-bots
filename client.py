import collections
import json
import socket
import threading

from typing import Deque, Dict, List, Optional, Sequence, Tuple, Union, cast

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

DELTAS = [
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (-1, 1),
    (1, -1)
]

pygame.init()
comicsans_28 = pygame.font.SysFont("Comic Sans MS", 28)

ClientPayload = Optional[Union[str, List[Tuple[int, int]]]]
ServerMessage = Optional[Union[int, List[List[int]]]]
PossibleMoveList = Dict[Tuple[int, int], List[Tuple[int, int]]]


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


def pixel_coords_from_board(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    if pos[0] < 0 or pos[0] >= BOARD_SIZE or pos[1] < 0 or pos[1] >= BOARD_SIZE:
        return None

    pixel_y = pos[1]*cell_size + radius
    pixel_x = pos[0]*cell_size - radius*(11-pos[1])
    return (pixel_x, pixel_y)


def draw_hop_overlay(surf: pygame.Surface, hops: List[Tuple[int, int]]) -> None:
    for i in range(len(hops)-1):
        pygame.draw.circle(
            surf,
            (128, 128, 128),
            pixel_coords_from_board(hops[i+1]),
            int(radius*0.2)
        )
        pygame.draw.line(
            surf,
            (128, 128, 128),
            pixel_coords_from_board(hops[i]),
            pixel_coords_from_board(hops[i+1]),
            int(radius*0.1)
        )


def in_board(x: int, y: int) -> bool:
    return x >= 0 and x < BOARD_SIZE and y >= 0 and y < BOARD_SIZE


def scan(
    board: List[List[int]],
    source_x: int, source_y: int,
    dx: int, dy: int
) -> Optional[Tuple[int, int]]:
    cur_x = source_x+dx
    cur_y = source_y+dy
    if not in_board(cur_x, cur_y):
        return None

    dist = 1
    while board[cur_x][cur_y] == 0:
        cur_x += dx
        cur_y += dy
        dist += 1
        if not in_board(cur_x, cur_y):
            return None

    if board[cur_x][cur_y] == -1:
        return None

    cur_x += dx
    cur_y += dy
    if not in_board(cur_x, cur_y) or board[cur_x][cur_y] != 0:
        return None

    dist -= 1
    while dist > 0:
        cur_x += dx
        cur_y += dy
        dist -= 1
        if not in_board(cur_x, cur_y) or board[cur_x][cur_y] != 0:
            return None

    return (cur_x, cur_y)


def get_possible(board: List[List[int]], source: Tuple[int, int]) -> PossibleMoveList:
    possible: PossibleMoveList = {}
    visited = [[False]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    q: Deque[Tuple[int, int]] = collections.deque()
    q.append(source)
    visited[source[0]][source[1]] = True

    original = board[source[0]][source[1]]
    board[source[0]][source[1]] = 0

    for direction in DELTAS:
        x = source[0]+direction[0]
        y = source[1]+direction[1]
        if in_board(x, y) and board[x][y] == 0:
            possible[(x, y)] = [source, (x, y)]

    while len(q) > 0:
        p = q.popleft()
        print(p)

        for direction in DELTAS:
            maybe_dest = scan(board, p[0], p[1], direction[0], direction[1])
            if maybe_dest is not None and not visited[maybe_dest[0]][maybe_dest[1]]:
                visited[maybe_dest[0]][maybe_dest[1]] = True
                q.append(maybe_dest)
                if p == source:
                    possible[maybe_dest] = [source, maybe_dest]
                else:
                    new = list(possible[p])
                    new.append(maybe_dest)
                    possible[maybe_dest] = new

    board[source[0]][source[1]] = original
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
        msg: List[bytes] = []
        while len(msg) == 0 or msg[-1][-1] != ord("}"):
            msg.append(sock.recv(256))
        data = json.loads(b"".join(msg))  # type: ignore
        print(data)
        return (
            data.get("msg", "error"),
            data.get("payload", None)
        )

    send("hello", "12345")
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

    def swap(p: Sequence[int], q: Sequence[int]) -> None:
        p_val = board[p[0]][p[1]]
        board[p[0]][p[1]] = board[q[0]][q[1]]
        board[q[0]][q[1]] = p_val

    def handle_incoming(request_move_flag: threading.Event, hops: List[List[int]]) -> None:
        while True:
            msg, payload = receive()
            print(msg, payload)
            if msg == "move":
                payload = cast(List[List[int]], payload)
                swap(payload[0], payload[-1])
                hops.clear()
                for hop in payload:
                    hops.append(hop)
                request_move_flag.clear()
            elif msg == "request_move":
                request_move_flag.set()
            else:
                raise RuntimeError("wtf 3")

    request_move_flag = threading.Event()
    last_move_hops: List[List[int]] = []
    sock_thread = threading.Thread(
        target=handle_incoming,
        args=(request_move_flag, last_move_hops),
        daemon=True
    )
    sock_thread.start()

    display = pygame.display.set_mode((window_size, window_size), pygame.RESIZABLE)
    pygame.display.set_caption(f"Player {player_id} ({NAMES[player_id]})")
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

        if len(last_move_hops) > 0:
            draw_hop_overlay(display, last_move_hops)  # type: ignore
        if len(possible_moves) > 0:
            hovering_point = board_coords_from_pixel(pygame.mouse.get_pos())
            if hovering_point is not None and hovering_point in possible_moves:
                draw_hop_overlay(display, possible_moves[hovering_point])

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
            elif event.type == pygame.MOUSEBUTTONUP:
                if len(last_move_hops) > 0:
                    last_move_hops.clear()
                if request_move_flag.is_set():
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
