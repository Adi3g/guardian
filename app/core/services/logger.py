# Configure logging based on the entity configuration
from __future__ import annotations

import logging


def configure_logging(log_config):
    if log_config.get('enabled', False):
        logging.basicConfig(
            level=getattr(logging, log_config.get('log_level', 'INFO').upper(), logging.INFO),
            format=log_config.get('log_format', '%(levelname)s: %(asctime)s - %(name)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_config.get('log_file', 'guardian.log')),
                logging.StreamHandler(),
            ],
        )


logger = logging.getLogger('guardian')
