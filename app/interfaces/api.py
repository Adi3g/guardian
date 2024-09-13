# app/interfaces/api.py

from fastapi import APIRouter, Depends
from app.infrastructure.config_loader import load_config
from app.core.services.gateway_service import GatewayService

router = APIRouter()

@router.get("/start-gateway")
def start_gateway():
    """
    API endpoint to start the security gateway.

    :return: A message indicating the status of the gateway
    """
    config = load_config('config.yaml')
    service = GatewayService(config)
    service.start()
    return {"message": f"{config.name} started successfully on {config.listen_address}:{config.listen_port}"}
