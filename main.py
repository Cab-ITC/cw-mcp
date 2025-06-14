import os, uvicorn, yaml
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import Response, FileResponse
from cw_client import ConnectWiseClient

API_KEY = os.getenv("SERVER_API_KEY")

app = FastAPI(title="ConnectWise MCP proxy")
cw = ConnectWiseClient()

def verify_key(x_api_key: str = Header(None)):
    if API_KEY is None:
        raise HTTPException(500, "SERVER_API_KEY not set on server")
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid X-Api-Key")
    return True

# --- NEW ENDPOINT FOR CUSTOM CONNECTOR MANIFEST ---
@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def get_ai_plugin_json():
    return FileResponse("ai-plugin.json")

# --- Endpoint for ChatGPT Actions ---
@app.get("/.well-known/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml() -> Response:
    openapi_json = app.openapi()
    openapi_yaml = yaml.dump(openapi_json, indent=2)
    return Response(content=openapi_yaml, media_type="text/yaml")

# Health check
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root():
    return {"status": "ok"}

# ... (rest of your endpoints remain the same) ...

# ---------- ticket endpoints ----------
@app.get("/tickets/search")
def search_tickets(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    pageSize: int = 25,
    auth: bool = Depends(verify_key)
):
    return cw.search_tickets(status, keyword, page, pageSize)

@app.get("/tickets/latest")
def latest_ticket(auth: bool = Depends(verify_key)):
    return cw.latest_ticket()

@app.get("/tickets")
def list_tickets(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    pageSize: int = 25,
    auth: bool = Depends(verify_key)
):
    return cw.search_tickets(status, keyword, page, pageSize)

# ---------- company & contact ----------
@app.get("/companies/{id}")
def get_company(id: int, auth: bool = Depends(verify_key)):
    return cw.get_company(id)

@app.get("/contacts/{id}")
def get_contact(id: int, auth:bool = Depends(verify_key)):
    return cw.get_contact(id)
