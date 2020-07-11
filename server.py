import threading
import time

from chinesecheckers.server.GameHost import GameHost

with GameHost("0.0.0.0", 41047) as server:
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    while server.running:
        time.sleep(0.5)

    server.shutdown()
