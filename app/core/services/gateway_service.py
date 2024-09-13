# app/core/services/gateway_service.py

from app.core.entities.gateway_entity import GatewayEntity

class GatewayService:
    """
    Service layer for managing gateway operations such as starting, stopping,
    and processing configurations.
    """

    def __init__(self, gateway: GatewayEntity):
        """
        Initializes the service with a specific gateway entity.

        :param gateway: The gateway entity containing configuration and state
        """
        self.gateway = gateway

    def start(self):
        """
        Starts the gateway, setting up the necessary configurations and listening
        on the specified address and port.
        """
        print(f"Starting {self.gateway.name} version {self.gateway.version}...")
        print(f"Listening on {self.gateway.listen_address}:{self.gateway.listen_port}")
