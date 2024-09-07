from typing import List, Dict

class Gateway:
    """represents the core entity of the security gateway, containing congifurations and rules for traffic management."""

    def __init__(self, name: str, version: str, listen_address: str, listen_port: int, allowed_ips: List[str], blocked_ips: List[str]):
        """Initializes the Gateway entity with the given parameters.

        :param name: the name of the gateway
        :param version: the version of the gateway
        :param listen_address: the address the gateway listens on
        :param listen_port: the port the gateway listens on
        :param allowed_ips: the list of IP addresses allowed by the gateway
        :param blocked_ips: the list of IP addresses blocked by the gateway
        """
        self.name = name
        self.version = version
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.allowed_ips = allowed_ips
        self.blocked_ips = blocked_ips

