from typing import Iterable, Tuple

# slot: one of the triangles surrounding the board where
# pieces start and end in. slot 0 is the top most, then
# ascending clockwise
SLOT_BOUNDS = (
    (9, 12, 3, False),
    (13, 16, 4, True),
    (9, 12, 12, False),
    (4, 7, 13, True),
    (0, 3, 12, False),
    (4, 7, 4, True),
)

SLOT_ENDPOINTS = (
    (12, 0),
    (16, 4),
    (12, 12),
    (4, 16),
    (0, 12),
    (4, 4),
)


def generate_slot_coords(slot_number: int) -> Iterable[Tuple[int, int]]:
    start_x, end_x, y_edge, pointing_up = SLOT_BOUNDS[slot_number]
    if pointing_up:
        scan = 4
        for x in range(start_x, end_x+1):
            for y in range(y_edge, y_edge+scan):
                yield (x, y)
            scan -= 1
    else:
        scan = 0
        for x in range(start_x, end_x+1):
            for y in range(y_edge-scan, y_edge+1):
                yield (x, y)
            scan += 1


# WIN_SLOTS[i][j] is the slot that player j+1
# needs to fill to win, in a game of i players
WIN_SLOTS = (
    None,
    None,
    (3, 0),
    (4, 0, 2),
    (4, 5, 1, 2),
    None,
    (3, 4, 5, 0, 1, 2),
)

from chinesecheckers.agents.MaxAgent import MaxAgent

agents = {
    "max": MaxAgent
}
