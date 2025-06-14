import os, uvicorn
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Depends
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

# Health check
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root():
    return {"status": "ok"}

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
    # This endpoint is now a full alias of search_tickets
    return cw.search_tickets(status, keyword, page, pageSize)

# ---------- company & contact ----------
@app.get("/companies/{id}")
def get_company(id: int, auth: bool = Depends(verify_key)):
    return cw.get_company(id)

@app.get("/contacts/{id}")
def get_contact(id: int, auth: bool = Depends(verify_key)):
    return cw.get_contact(id)

# This section is not needed for Fly.io deployments
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)
