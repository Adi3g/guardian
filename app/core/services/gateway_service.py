from __future__ import annotations

import logging
import urllib.parse
from datetime import timedelta
from itertools import cycle

from fastapi import HTTPException

from .logger import logger
from app.core.entities.gateway_entity import GatewayEntity
from app.core.services.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.services.auth import create_access_token
from app.core.services.auth import verify_token
from app.core.services.logger import configure_logging
from app.core.services.rate_limiter import RateLimiter
from app.core.services.session_manager import SessionManager
from app.core.services.waf import WAF

class GatewayService:
    """
    Service layer for managing gateway operations including access control,
    redirection, load balancing, rate limiting, and WAF.
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

        # Initialize WAF
        if self.gateway.security.get('waf', {}).get('enabled', False):
            self.waf: WAF | None = WAF(self.gateway.security['waf'])  # Assign WAF instance
        else:
            self.waf = None  # Use None when WAF is disabled

        # Initialize Session Manager
        if self.gateway.security.get('session_management', {}).get('enabled', False):
            session_config = self.gateway.security['session_management']
            self.session_manager: SessionManager | None = SessionManager(session_config['session_timeout'])
        else:
            self.session_manager = None

    def start(self):
        """
        Starts the gateway, setting up the necessary configurations and listening
        on the specified address and port.
        """
        logger.info(f"Starting {self.gateway.name} version {self.gateway.version}...")
        logger.info(f"Listening on {self.gateway.listen_address}:{self.gateway.listen_port}")

    def check_access(self, client_ip: str):
        """
        Checks if the client IP is allowed or blocked based on the gateway configuration.

        :param client_ip: The IP address of the client making the request
        :raises HTTPException: If the IP is blocked or rate limit exceeded
        """
        logger.info(f"Checking access for IP: {client_ip}")
        if self.rate_limiter and not self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail='Too many requests. You are temporarily banned.')

        if client_ip in self.gateway.blocked_ips:
            logger.warning(f"Access denied for blocked IP: {client_ip}")
            raise HTTPException(status_code=403, detail='Access denied: Your IP is blocked.')

        if self.gateway.allowed_ips and client_ip not in self.gateway.allowed_ips:
            logger.warning(f"Access denied for IP not in allowed list: {client_ip}")
            raise HTTPException(status_code=403, detail='Access denied: Your IP is not allowed.')

        logger.info(f"Access granted for IP: {client_ip}")

    def handle_redirection(self, request_path: str, request_port: int, query_params: dict = {}) -> str:
        """
        Handles redirection based on the configured rules and includes query parameters.

        :param request_path: The path of the incoming request
        :param request_port: The port of the incoming request
        :param query_params: The query parameters of the incoming request
        :return: A URL to redirect to or an empty string if no redirection is needed
        """
        if not self.gateway.redirection.get('enabled', False):
            return ''

        for rule in self.gateway.redirection.get('rules', []):
            if rule['action'] == 'redirect':
                # Handling redirection based on source port
                if 'source_port' in rule and request_port == rule['source_port']:
                    redirect_url = f"https://{self.gateway.listen_address}:{rule['destination_port']}{request_path}"

                    # Append query parameters to the redirect URL
                    if query_params:
                        query_string = urllib.parse.urlencode(query_params)
                        redirect_url = f"{redirect_url}?{query_string}"

                    logger.info(f"Redirecting from port {request_port} to {rule['destination_port']} with URL {redirect_url}")
                    return redirect_url

                # Handling redirection based on source path
                if 'source_path' in rule and rule['source_path'].strip('*') in request_path:
                    redirect_url = request_path.replace(rule['source_path'].strip('*'), rule['destination_path'])

                    # Append query parameters to the redirect URL
                    if query_params:
                        query_string = urllib.parse.urlencode(query_params)
                        redirect_url = f"{redirect_url}?{query_string}"

                    logger.info(f"Redirecting path {request_path} to {redirect_url}")
                    return redirect_url

        return ''

    def inspect_request_with_waf(self, request_content: str):
        """
        Inspects the request using the WAF before further processing.

        :param request_content: The content of the incoming request
        :raises HTTPException: If the WAF detects malicious content
        """
        if self.waf:
            self.waf.inspect_request(request_content)

    def get_next_server(self) -> dict:
        """
        Retrieves the next server in the load balancing pool based on the selected strategy.

        :return: A dictionary containing the address and port of the next server
        """
        if not self.server_iterator:
            logger.error('Load balancing is disabled or misconfigured.')
            raise HTTPException(status_code=503, detail='Load balancing is disabled or misconfigured.')

        next_server = next(self.server_iterator)
        logger.info(f"Routing to next server: {next_server['address']}:{next_server['port']}")
        return next_server

    def start_session(self, user_id: str) -> str:
        """
        Starts a session for the given user.

        :param user_id: The ID of the user
        :return: The session ID
        """
        if not self.session_manager:
            raise HTTPException(status_code=500, detail='Session management is not enabled.')

        return self.session_manager.create_session(user_id)

    def validate_session(self, session_id: str):
        """
        Validates if a session is active and valid.

        :param session_id: The session ID
        :raises HTTPException: If the session is invalid or expired
        """
        if not self.session_manager:
            raise HTTPException(status_code=500, detail='Session management is not enabled.')

        if not self.session_manager.validate_session(session_id):
            raise HTTPException(status_code=401, detail='Session expired or invalid. Please log in again.')

    def authenticate_user(self, user_id: str) -> str:
        """
        Authenticates the user and returns a JWT token.

        :param user_id: The ID of the user
        :return: JWT token if authentication is successful
        """
        # TODO! validate the user credentials here.

        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(data={'sub': user_id}, expires_delta=token_expires)
        return token

    def verify_jwt(self, token: str):
        """
        Verifies the validity of a JWT token.

        :param token: The JWT token
        :raises HTTPException: If the token is invalid or expired
        """
        return verify_token(token)
