import os, uvicorn
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException, Depends
from cw_client import ConnectWiseClient

API_KEY = os.getenv("SERVER_API_KEY")  # your own secret for this proxy

app = FastAPI(title="ConnectWise MCP proxy")
cw = ConnectWiseClient()

def verify_key(x_api_key: str = Header(...)):
    if API_KEY is None:
        raise HTTPException(500, "SERVER_API_KEY not set on server")
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid X-Api-Key")
    return True

# ---------- health-check root ----------
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root():
    return {"status": "ok"}

# ---------- debug helper  (TEMPORARY) ----------
@app.get("/debug/key", include_in_schema=False)
def debug_key(x_api_key: str = Header(None)):
    """
    Returns the key your request sent, the key stored on the server,
    and whether they match. Remove this once 401 issues are solved.
    """
    server_key = os.getenv("SERVER_API_KEY")
    return {
        "received": x_api_key,
        "server_var": server_key,
        "match": x_api_key == server_key,
    }

# ---------- ticket endpoints ----------
@app.get("/tickets/search")
def search_tickets(
    status: Optional[str] = None,
    page: int = 1,
    pageSize: int = 25,
    auth: bool = Depends(verify_key)
):
    return cw.search_tickets(status=status, page=page, page_size=pageSize)

@app.get("/tickets/latest")
def latest_ticket(auth: bool = Depends(verify_key)):
    return cw.latest_ticket()

@app.get("/tickets")
def list_tickets(page: int = 1, pageSize: int = 25, auth: bool = Depends(verify_key)):
    return cw.list_tickets(page=page, page_size=pageSize)

# ---------- company & contact ----------
@app.get("/companies/{id}")
def get_company(id: int, auth: bool = Depends(verify_key)):
    return cw.get_company(id)

@app.get("/contacts/{id}")
def get_contact(id: int, auth: bool = Depends(verify_key)):
    return cw.get_contact(id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

# Triggering a new deployment on Fly.io
import os, uvicorn
from typing import Optional
# ... the rest of the file stays the same
