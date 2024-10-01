from __future__ import annotations

from .base_strategy import LoadBalancingStrategy

class LeastConnectionsStrategy(LoadBalancingStrategy):
    """
    Implements least-connections load balancing strategy.
    Tracks the number of active connections to each server.
    """
    def __init__(self, servers: list[dict]):
        super().__init__(servers)
        self.server_connections = {server['address']: 0 for server in servers}

    def get_next_server(self) -> dict:
        # Return the server with the fewest active connections
        return min(self.servers, key=lambda server: self.server_connections[server['address']])

    def increment_connection(self, server: dict):
        self.server_connections[server['address']] += 1

    def decrement_connection(self, server: dict):
        self.server_connections[server['address']] = max(0, self.server_connections[server['address']])
