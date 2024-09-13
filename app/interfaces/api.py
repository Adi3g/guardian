# app/interfaces/api.py

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from app.infrastructure.config_loader import load_config
from app.core.services.gateway_service import GatewayService
import httpx

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
async def handle_request(path: str, request: Request):
    """
    Generic API endpoint to handle incoming requests, apply redirection rules, and load balancing.

    :param path: The path of the incoming request
    :param request: The incoming request object
    :return: A redirection response, load balanced response, or the requested content
    """
    redirect_url = service.handle_redirection(request_path=f"/{path}", request_port=request.url.port)
    if redirect_url:
        return RedirectResponse(url=redirect_url)

    try:
        next_server = service.get_next_server()
        # Forward the request to the next server
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{next_server['address']}:{next_server['port']}/{path}")
            return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Error handling request", "error": str(e)})

@router.get("/health")
def health_check():
    """
    Health check endpoint to monitor the status of the gateway.

    :return: A message indicating the health status of the gateway
    """
    return {"status": "healthy", "message": "The Guardian gateway is running properly."}
