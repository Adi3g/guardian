from __future__ import annotations

import random
from itertools import cycle

from fastapi import HTTPException

class LoadBalancerService:
    """
    Service to manage load balancing across multiple strategies.
    Supports round-robin, random, and least-connections strategies.
    """

    def __init__(self, strategy: str, servers: list[dict]):
        """
        Initializes the LoadBalancerService with the selected strategy and server pool.

        :param strategy: The load balancing strategy (round-robin, least-connections, random)
        :param servers: A list of server dictionaries with 'address' and 'port' keys
        """
        self.servers = servers
        self.strategy = strategy
        self.server_connections = {server['address']: 0 for server in servers}

        if strategy == 'round-robin':
            self.server_iterator = cycle(servers)
        elif strategy == 'random':
            pass  # No special setup needed for random strategy
        elif strategy == 'least-connections':
            pass  # Least-connections handled using connection counts
        else:
            raise ValueError(f"Unsupported load balancing strategy: {strategy}")

    def get_next_server(self) -> dict:
        """
        Returns the next server based on the selected load balancing strategy.

        :return: The selected server dictionary with 'address' and 'port'
        """
        if self.strategy == 'round-robin':
            return next(self.server_iterator)
        elif self.strategy == 'random':
            return random.choice(self.servers)
        elif self.strategy == 'least-connections':
            # Select the server with the fewest active connections
            return min(self.servers, key=lambda server: self.server_connections[server['address']])
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported load balancing strategy: {self.strategy}")

    def increment_connection(self, server: dict):
        """
        Increments the active connection count for a given server.
        This is primarily used in the least-connections strategy.

        :param server: The server dictionary whose connection count is to be incremented
        """
        if self.strategy == 'least-connections':
            self.server_connections[server['address']] += 1

    def decrement_connection(self, server: dict):
        """
        Decrements the active connection count for a given server.
        This is primarily used in the least-connections strategy.

        :param server: The server dictionary whose connection count is to be decremented
        """
        if self.strategy == 'least-connections':
            self.server_connections[server['address']] = max(0, self.server_connections[server['address']])
