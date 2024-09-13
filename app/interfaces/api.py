# app/interfaces/api.py

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from app.infrastructure.config_loader import load_config
from app.core.services.gateway_service import GatewayService

router = APIRouter()

# Load the configuration and initialize the service
config = load_config('config.yaml')
service = GatewayService(config)

@router.get("/start-gateway")
def start_gateway():
    """
    API endpoint to start the security gateway.

    :return: A message indicating the status of the gateway
    """
    service.start()
    return {"message": f"{config.name} started successfully on {config.listen_address}:{config.listen_port}"}

@router.get("/check-access")
def check_access(request: Request):
    """
    API endpoint to check access for a given IP address.

    :param request: The incoming request object containing the client's IP
    :return: A message indicating whether access is allowed
    """
    client_ip = request.client.host
    service.check_access(client_ip)
    return {"message": "Access granted"}

@router.get("/{path:path}")
def handle_request(path: str, request: Request):
    """
    Generic API endpoint to handle incoming requests and apply redirection rules.

    :param path: The path of the incoming request
    :param request: The incoming request object
    :return: A redirection response or the requested content
    """
    redirect_url = service.handle_redirection(request_path=f"/{path}", request_port=request.url.port)
    if redirect_url:
        return RedirectResponse(url=redirect_url)
    return {"message": f"Request handled for path: /{path}"}
