import json
import math
import socket
import threading

from typing import Dict, List, Optional, Sequence, Tuple, Union, cast

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

SQRT_2 = math.sqrt(2)

pygame.init()
comicsans_28 = pygame.font.SysFont("Comic Sans MS", 28)

ClientPayload = Optional[Union[str, List[Tuple[int, int]]]]
ServerMessage = Optional[Union[int, List[List[int]]]]
PossibleMoveList = Dict[Tuple[int, int], List[Tuple[int, int]]]


def draw_board(
    surf: pygame.Surface,
    board: List[List[int]],
    is_client_turn: bool,
    highlight: Tuple[int, int],
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
    if len(highlight) > 0:
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                cell = board[x][y]
                if x == highlight[0] and y == highlight[1]:
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


def is_valid_hop(
    source: Tuple[int, int],
    dest: Tuple[int, int],
    is_first: bool
) -> Tuple[bool, bool]:
    if (source[0] < 0
        or source[1] < 0
        or dest[0] < 0
        or dest[1] < 0
        or source[0] >= BOARD_SIZE
        or source[1] >= BOARD_SIZE
        or dest[0] >= BOARD_SIZE
        or dest[1] >= BOARD_SIZE
    ):
        return (False, False)
    if board[dest[0]][dest[1]] != 0:
        return (False, False)

    diff = (dest[0]-source[0], dest[1]-source[1])
    board_dist = math.hypot(diff[0], diff[1], -diff[0] - diff[1]) / SQRT_2

    if not board_dist.is_integer():
        return (False, False)
    board_dist = int(board_dist)

    dx = diff[0]//board_dist
    dy = diff[1]//board_dist

    cur_x = source[0]+dx
    cur_y = source[1]+dy
    gaps: List[int] = [0]
    while not (cur_x == dest[0] and cur_y == dest[1]):
        if board[cur_x][cur_y] == 0:
            gaps[-1] += 1
        else:
            if len(gaps) == 2:
                return (False, False)
            gaps.append(0)
        cur_x += dx
        cur_y += dy

    if len(gaps) == 1:
        return (gaps[0] == 0 and is_first, True)
    else:
        return (gaps[0] == gaps[1], False)


with socket.socket() as sock:
    sock.connect((HOST, PORT))

    def send(msg: str, payload: ClientPayload) -> None:
        print(
            f'sending {{"msg": "{msg}", "payload": {payload}}}\n'
                .replace("(", "[")  # noqa - flake8 wants it one tab left, which is nonsense
                .replace(")", "]")
        )
        sock.send(bytes(
            f'{{"msg": "{msg}", "payload": {payload}}}\n'
                .replace("(", "[")  # noqa
                .replace(")", "]"),
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

    receive()  # we dont need the starting player message

    def move(source: Sequence[int], dest: Sequence[int]) -> None:
        board[dest[0]][dest[1]] = board[source[0]][source[1]]
        board[source[0]][source[1]] = 0

    def handle_incoming(
        request_move_flag: threading.Event,
        game_over_flag: threading.Event,
        hops: List[List[int]]
    ) -> None:
        while True:
            msg, payload = receive()
            print(msg, payload)
            if msg == "move":
                payload = cast(List[List[int]], payload)
                move(payload[0], payload[-1])
                hops.clear()
                for hop in payload:
                    hops.append(hop)
                request_move_flag.clear()
            elif msg == "request_move":
                request_move_flag.set()
            elif msg == "game_over":
                game_over_flag.set()
            else:
                raise RuntimeError("wtf 3")

    request_move_flag = threading.Event()
    game_over_flag = threading.Event()
    last_move_hops: List[List[int]] = []
    sock_thread = threading.Thread(
        target=handle_incoming,
        args=(request_move_flag, game_over_flag, last_move_hops),
        daemon=True
    )
    sock_thread.start()

    display = pygame.display.set_mode((window_size, window_size), pygame.RESIZABLE)
    pygame.display.set_caption(f"Player {player_id} ({NAMES[player_id]})")
    clock = pygame.time.Clock()
    current_move_chain: List[Tuple[int, int]] = []
    single_hop_move = False

    while not game_over_flag.is_set():
        if (not request_move_flag.is_set()
            and len(current_move_chain) > 0
        ):
            single_hop_move = False
            current_move_chain.clear()

        if len(current_move_chain) > 0:
            draw_board(display, board, request_move_flag.is_set(), current_move_chain[-1])
        else:
            draw_board(display, board, request_move_flag.is_set(), [])  # type: ignore

        if len(last_move_hops) > 0:
            draw_hop_overlay(display, last_move_hops)  # type: ignore
        if len(current_move_chain) > 0:
            draw_hop_overlay(display, current_move_chain)

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
                game_over_flag.set()
            elif event.type == pygame.MOUSEBUTTONUP:
                if len(last_move_hops) > 0:
                    last_move_hops.clear()
                if request_move_flag.is_set():
                    selected_point = board_coords_from_pixel(event.pos)
                    if selected_point is not None:
                        if len(current_move_chain) > 0:
                            hop_check = is_valid_hop(
                                current_move_chain[-1],
                                selected_point,
                                len(current_move_chain) == 1
                            )
                            if hop_check[0] and not single_hop_move:
                                single_hop_move = hop_check[1]
                                move(current_move_chain[-1], selected_point)
                                current_move_chain.append(selected_point)
                        elif board[selected_point[0]][selected_point[1]] == player_id:
                            current_move_chain.append(selected_point)
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_RETURN
                    and request_move_flag.is_set()
                    and len(current_move_chain) > 0
                ):
                    send("make_move", current_move_chain)
                    move(current_move_chain[-1], current_move_chain[0])
                    current_move_chain.clear()
                    single_hop_move = False
                elif event.key == pygame.K_z and len(current_move_chain) > 0:
                    if len(current_move_chain) < 2:
                        single_hop_move = False
                    else:
                        move(current_move_chain[-1], current_move_chain[-2])
                    current_move_chain.pop()
                elif event.key == pygame.K_ESCAPE and len(current_move_chain) > 0:
                    if len(current_move_chain) > 1:
                        move(current_move_chain[-1], current_move_chain[0])
                    single_hop_move = False
                    current_move_chain.clear()

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()
