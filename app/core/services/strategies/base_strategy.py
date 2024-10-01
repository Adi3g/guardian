from __future__ import annotations

from abc import ABC
from abc import abstractmethod

class LoadBalancingStrategy(ABC):
    """
    Abstract base class for all load balancing strategies.
    """
    def __init__(self, servers: list[dict]):
        self.servers = servers

    @abstractmethod
    def get_next_server(self) -> dict:
        pass

    def handle_server_failure(self, server: dict):
        """
        Handles server failures, allowing strategies to react.
        """
        pass
