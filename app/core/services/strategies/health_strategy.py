from __future__ import annotations

import time
from typing import Dict
from typing import List

from .base_strategy import LoadBalancingStrategy

class LoadBalancingStrategyWithHealth(LoadBalancingStrategy):
    """
    Extends the base strategy class with basic health checking.
    Acts as a wrapper for any base load balancing strategy.
    """
    def __init__(self, base_strategy: LoadBalancingStrategy):
        self.base_strategy = base_strategy
        self.servers = base_strategy.servers
        self.server_health: dict[str, bool] = {server['address']: True for server in self.servers}
        self.failed_servers: dict[str, float] = {}  # Track failed servers and their failure times

    def handle_server_failure(self, server: dict):
        """
        Mark the server as unhealthy and exclude it temporarily.
        """
        self.server_health[server['address']] = False
        self.failed_servers[server['address']] = time.time()

    def get_healthy_servers(self) -> list[dict]:
        """
        Return only servers marked as healthy.
        """
        # Re-check the failed servers after a cooldown (e.g., 60 seconds)
        cooldown_period = 60
        current_time = time.time()

        for address, failure_time in list(self.failed_servers.items()):
            if current_time - failure_time > cooldown_period:
                # Assume the server might have recovered, mark as healthy
                self.server_health[address] = True
                del self.failed_servers[address]

        return [server for server in self.servers if self.server_health[server['address']]]

    def get_next_server(self) -> dict:
        """
        Delegate to the base strategy but only return healthy servers.
        """
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            raise Exception('No healthy servers available')

        # Set the base strategy's server list to the healthy servers only
        self.base_strategy.servers = healthy_servers
        return self.base_strategy.get_next_server()  # Use the base strategy to select a healthy server
