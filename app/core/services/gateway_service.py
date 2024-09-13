# app/core/services/gateway_service.py

from fastapi import HTTPException
from app.core.entities.gateway_entity import GatewayEntity

class GatewayService:
    """
    Service layer for managing gateway operations including access control and redirection.
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

    def handle_redirection(self, request_path: str, request_port: int) -> str:
        """
        Handles redirection based on the configured rules.

        :param request_path: The path of the incoming request
        :param request_port: The port of the incoming request
        :return: A URL to redirect to or an empty string if no redirection is needed
        """
        if not self.gateway.config.get('redirection', {}).get('enabled', False):
            return ""

        for rule in self.gateway.config['redirection']['rules']:
            if rule['action'] == 'redirect':
                if 'source_port' in rule and request_port == rule['source_port']:
                    return f"https://{self.gateway.listen_address}:{rule['destination_port']}{request_path}"
                if 'source_path' in rule and rule['source_path'].strip('*') in request_path:
                    return request_path.replace(rule['source_path'].strip('*'), rule['destination_path'])

        return ""
