# app/core/entities/gateway_entity.py

from typing import List, Dict

class GatewayEntity:
    """
    Represents the core entity of the security gateway, containing configurations
    and rules for traffic management.
    """

    def __init__(self, name: str, version: str, listen_address: str, listen_port: int, allowed_ips: List[str], blocked_ips: List[str]):
        """
        Initializes a new instance of the GatewayEntity.

        :param name: Name of the gateway
        :param version: Version of the gateway
        :param listen_address: IP address the gateway listens on
        :param listen_port: Port the gateway listens on
        :param allowed_ips: List of allowed IP addresses
        :param blocked_ips: List of blocked IP addresses
        """
        self.name = name
        self.version = version
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.allowed_ips = allowed_ips
        self.blocked_ips = blocked_ips