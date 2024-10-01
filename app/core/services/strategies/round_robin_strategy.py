# round_robin_strategy.py
from __future__ import annotations

from itertools import cycle

from .base_strategy import LoadBalancingStrategy

class RoundRobinStrategy(LoadBalancingStrategy):
    """
    Implements round-robin load balancing strategy.
    """
    def __init__(self, servers: list[dict]):
        super().__init__(servers)
        self.server_iterator = cycle(servers)

    def get_next_server(self) -> dict:
        return next(self.server_iterator)
