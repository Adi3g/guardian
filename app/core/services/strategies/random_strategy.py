from __future__ import annotations

import random

from .base_strategy import LoadBalancingStrategy

class RandomStrategy(LoadBalancingStrategy):
    """
    Implements random load balancing strategy.
    """
    def get_next_server(self) -> dict:
        return random.choice(self.servers)
