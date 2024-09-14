# app/core/services/gateway_service.py
from __future__ import annotations

import logging
from itertools import cycle

from fastapi import HTTPException

from app.core.entities.gateway_entity import GatewayEntity
from app.core.services.rate_limiter import RateLimiter

# Configure logging based on the entity configuration


def configure_logging(log_config):
    if log_config.get('enabled', False):
        logging.basicConfig(
            level=getattr(
                logging, log_config.get(
                    'log_level', 'INFO',
                ).upper(), logging.INFO,
            ),
            format=log_config.get(
                'log_format', '%(levelname)s:     %(asctime)s - %(name)s - %(message)s',
            ),
            handlers=[
                logging.FileHandler(
                    log_config.get(
                        'log_file', 'guardian.log',
                    ),
                ),
                logging.StreamHandler(),
            ],
        )


logger = logging.getLogger('guardian')


class GatewayService:
    """
    Service layer for managing gateway operations including access control,
    redirection, load balancing, and advanced security features.
    """

    def __init__(self, gateway: GatewayEntity):
        """
        Initializes the service with a specific gateway entity.

        :param gateway: The gateway entity containing configuration and state
        """
        self.gateway = gateway
        configure_logging(self.gateway.logging)
        self.server_iterator = cycle(self.gateway.load_balancing.get('servers', [])) if self.gateway.load_balancing.get('enabled', False) else None

        # Initialize Rate Limiter
        if self.gateway.security.get('rate_limiting', {}).get('enabled', False):
            rate_limit_config = self.gateway.security['rate_limiting']
            self.rate_limiter: RateLimiter | None = RateLimiter(
                max_requests=rate_limit_config['max_requests_per_minute'],
                ban_duration=rate_limit_config['ban_duration'],
            )
        else:
            self.rate_limiter = None

    def start(self):
        """
        Starts the gateway, setting up the necessary configurations and listening
        on the specified address and port.
        """
        logger.info(f"Starting {self.gateway.name} version {self.gateway.version}...")
        logger.info(f"Listening on {self.gateway.listen_address}:{
                    self.gateway.listen_port
        }")

    def check_access(self, client_ip: str):
        """
        Checks if the client IP is allowed or blocked based on the gateway configuration.

        :param client_ip: The IP address of the client making the request
        :raises HTTPException: If the IP is blocked or rate limit exceeded
        """
        logger.info(f"Checking access for IP: {client_ip}")
        if self.rate_limiter and not self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429, detail='Too many requests. You are temporarily banned.',
            )

        if client_ip in self.gateway.blocked_ips:
            logger.warning(f"Access denied for blocked IP: {client_ip}")
            raise HTTPException(
                status_code=403, detail='Access denied: Your IP is blocked.',
            )
        if self.gateway.allowed_ips and client_ip not in self.gateway.allowed_ips:
            logger.warning(
                f"Access denied for IP not in allowed list: {client_ip}",
            )
            raise HTTPException(
                status_code=403, detail='Access denied: Your IP is not allowed.',
            )
        logger.info(f"Access granted for IP: {client_ip}")

    def handle_redirection(self, request_path: str, request_port: int) -> str:
        """
        Handles redirection based on the configured rules.

        :param request_path: The path of the incoming request
        :param request_port: The port of the incoming request
        :return: A URL to redirect to or an empty string if no redirection is needed
        """
        if not self.gateway.redirection.get('enabled', False):
            return ''

        for rule in self.gateway.redirection.get('rules', []):
            if rule['action'] == 'redirect':
                if 'source_port' in rule and request_port == rule['source_port']:
                    redirect_url = f"https://{self.gateway.listen_address}:{
                        rule['destination_port']
                    }{request_path}"
                    logger.info(f"Redirecting from port {request_port} to {
                                rule['destination_port']
                    } with URL {redirect_url}")
                    return redirect_url
                if 'source_path' in rule and rule['source_path'].strip('*') in request_path:
                    redirect_url = request_path.replace(
                        rule['source_path'].strip(
                            '*',
                        ), rule['destination_path'],
                    )
                    logger.info(f"Redirecting path {
                                request_path
                    } to {redirect_url}")
                    return redirect_url

        return ''

    def get_next_server(self) -> dict:
        """
        Retrieves the next server in the load balancing pool based on the selected strategy.

        :return: A dictionary containing the address and port of the next server
        """
        if not self.server_iterator:
            logger.error('Load balancing is disabled or misconfigured.')
            raise HTTPException(
                status_code=503, detail='Load balancing is disabled or misconfigured.',
            )

        next_server = next(self.server_iterator)
        logger.info(f"Routing to next server: {
                    next_server['address']
        }:{next_server['port']}")
        return next_server
