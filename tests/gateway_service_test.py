from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.entities.gateway_entity import GatewayEntity
from app.core.services.gateway_service import GatewayService

@pytest.fixture
def gateway_entity():
    return GatewayEntity(
        name='Test Gateway',
        version='1.0.0',
        listen_address='0.0.0.0',
        listen_port=8080,
        allowed_ips=['192.168.1.10'],
        blocked_ips=['192.168.1.100'],
        redirection={
            'enabled': True,
            'rules': [
                {'name': 'Redirect HTTP to HTTPS', 'source_port': 80, 'destination_port': 443, 'action': 'redirect'},
            ],
        },
        load_balancing={
            'enabled': True,
            'strategy': 'round_robin',
            'servers': [{'address': '192.168.2.20', 'port': 8081}],
        },
        logging={'enabled': False},  # Disable logging for tests
        security={'rate_limiting': {'enabled': False}},  # Disable rate limiting for tests
    )

@pytest.fixture
def gateway_service(gateway_entity):
    return GatewayService(gateway_entity)

def test_gateway_service_check_access_allowed_ip(gateway_service):
    client_ip = '192.168.1.10'
    # Should not raise an exception
    gateway_service.check_access(client_ip)

def test_gateway_service_check_access_blocked_ip(gateway_service):
    client_ip = '192.168.1.100'
    with pytest.raises(HTTPException) as excinfo:
        gateway_service.check_access(client_ip)

    assert excinfo.value.status_code == 403
    assert 'Access denied' in str(excinfo.value.detail)

def test_gateway_service_redirection(gateway_service):
    redirect_url = gateway_service.handle_redirection('/path', 80)
    assert redirect_url == 'https://0.0.0.0:443/path'

def test_gateway_service_load_balancing(gateway_service):
    server = gateway_service.get_next_server()
    assert server['address'] == '192.168.2.20'
    assert server['port'] == 8081
