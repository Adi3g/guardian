from __future__ import annotations

from .strategies.base_strategy import LoadBalancingStrategy
from .strategies.health_strategy import LoadBalancingStrategyWithHealth
from .strategies.least_connections_strategy import LeastConnectionsStrategy
from .strategies.random_strategy import RandomStrategy
from .strategies.round_robin_strategy import RoundRobinStrategy

class LoadBalancerService:
    """
    Service to manage load balancing across multiple strategies.
    Supports round-robin, random, and least-connections strategies with optional health checking.
    """

    def __init__(self, strategy: str, servers: list[dict], enable_health_checking: bool = False):
        self.strategy_name = strategy
        self.servers = servers
        self.enable_health_checking = enable_health_checking
        self.strategy: LoadBalancingStrategy = self._select_strategy(strategy)

    def _select_strategy(self, strategy: str) -> LoadBalancingStrategy:
        """
        Selects the appropriate load balancing strategy based on the configuration.
        Optionally wraps the strategy with health checking if enabled.
        """
        base_strategy: LoadBalancingStrategy  # Explicitly type as LoadBalancingStrategy

        if strategy == 'round-robin':
            base_strategy = RoundRobinStrategy(self.servers)
        elif strategy == 'random':
            base_strategy = RandomStrategy(self.servers)
        elif strategy == 'least-connections':
            base_strategy = LeastConnectionsStrategy(self.servers)
        else:
            raise ValueError(f"Unsupported load balancing strategy: {strategy}")

        # Wrap the strategy with health checking if enabled
        if self.enable_health_checking:
            return LoadBalancingStrategyWithHealth(base_strategy)
        return base_strategy

    def get_next_server(self) -> dict:
        """
        Returns the next server based on the selected load balancing strategy.
        """
        return self.strategy.get_next_server()

    def handle_server_failure(self, server: dict):
        """
        Handles server failure by marking the server as unhealthy.
        This is only applicable if health checking is enabled.
        """
        if isinstance(self.strategy, LoadBalancingStrategyWithHealth):
            self.strategy.handle_server_failure(server)

    def increment_connection(self, server: dict):
        """
        Increments the active connection count for the server (used in least-connections).
        """
        if isinstance(self.strategy, LeastConnectionsStrategy):
            self.strategy.increment_connection(server)

    def decrement_connection(self, server: dict):
        """
        Decrements the active connection count for the server (used in least-connections).
        """
        if isinstance(self.strategy, LeastConnectionsStrategy):
            self.strategy.decrement_connection(server)
