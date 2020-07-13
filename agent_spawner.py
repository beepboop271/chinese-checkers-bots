import threading
import time

from typing import List, Tuple

from chinesecheckers.agents.Agent import Agent
from chinesecheckers.agents.evaluators import evaluators
from chinesecheckers.agents import agents

agents_to_spawn: List[Tuple[str, str]] = [
    # ("max", "random"),
    ("max", "distance"),
    ("max", "distance"),
    ("max", "distance"),
    ("max", "distance"),
    ("max", "distance"),
]

spawned_agents: List[Tuple[Agent, threading.Thread]] = []

for agent in agents_to_spawn:
    print("spawning", agent)
    a = agents[agent[0]]("127.0.0.1", 41047, evaluators[agent[1]])
    t = threading.Thread(target=a.play, daemon=True)
    t.start()
    spawned_agents.append((a, t))

while True:
    time.sleep(1)
