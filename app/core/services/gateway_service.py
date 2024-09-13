# app/core/services/gateway_service.py

from fastapi import HTTPException
from app.core.entities.gateway_entity import GatewayEntity

class GatewayService:
    """
    Service layer for managing gateway operations such as starting, stopping,
    and processing configurations, including access control.
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

    def check_access(self, client_ip: str):
        """
        Checks if the client IP is allowed or blocked based on the gateway configuration.

        :param client_ip: The IP address of the client making the request
        :raises HTTPException: If the IP is blocked
        """
        if client_ip in self.gateway.blocked_ips:
            raise HTTPException(status_code=403, detail="Access denied: Your IP is blocked.")
        if self.gateway.allowed_ips and client_ip not in self.gateway.allowed_ips:
            raise HTTPException(status_code=403, detail="Access denied: Your IP is not allowed.")
