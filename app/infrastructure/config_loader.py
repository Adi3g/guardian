# app/infrastructure/config_loader.py
from __future__ import annotations

import yaml

from app.core.entities.gateway_entity import GatewayEntity


def load_config(config_path: str) -> GatewayEntity:
    """
    Loads the configuration from a YAML file and creates a GatewayEntity.

    :param config_path: Path to the configuration YAML file
    :return: GatewayEntity populated with configuration data
    """
    with open(config_path) as file:
        config = yaml.safe_load(file)
    general = config.get('general', {})
    access_control = config.get('access_control', {})
    redirection = config.get('redirection', {})
    load_balancing = config.get('load_balancing', {})
    logging = config.get('logging', {})
    security = config.get('security', {})

    return GatewayEntity(
        name=general.get('gateway_name', 'Unnamed Gateway'),
        version=general.get('version', '0.0.1'),
        listen_address=general.get('listen_address', '0.0.0.0'),
        listen_port=general.get('listen_port', 8080),
        allowed_ips=access_control.get('allowed_ips', []),
        blocked_ips=access_control.get('blocked_ips', []),
        redirection=redirection,
        load_balancing=load_balancing,
        logging=logging,
        security=security,
    )
