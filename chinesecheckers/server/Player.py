from typing import BinaryIO, Optional


class Player(object):
    __slots__ = ("_rfile", "_wfile", "_PLAYER_ID")

    def __init__(self, rfile: BinaryIO, wfile: BinaryIO, player_id: int):
        self._rfile = rfile
        self._wfile = wfile
        self._PLAYER_ID = player_id

    def send(self, msg: str, payload: Optional[str] = None) -> None:
        if payload is None:
            print(f'sending {{"msg": "{msg}"}} to {self._PLAYER_ID}')
            self._wfile.write(bytes(
                f'{{"msg": "{msg}"}}',
                "ascii"
            ))
        else:
            print(f'sending {{"msg": "{msg}", "payload": {payload}}} to {self._PLAYER_ID}')
            self._wfile.write(bytes(
                f'{{"msg": "{msg}", "payload": {payload}}}',
                "ascii"
            ))

    @property
    def PLAYER_ID(self) -> int:
        return self._PLAYER_ID
