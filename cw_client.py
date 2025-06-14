import os, base64, requests, logging
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConnectWiseClient:
    """
    Minimal read-only wrapper over ConnectWise Manage REST API.
    >> DIAGNOSTIC MODE: Pointing to httpbin.org to inspect headers <<
    """
    def __init__(self):
        # All credential setup is just for generating headers
        self.company   = os.getenv("CW_COMPANY", "DIAGNOSTIC")
        self.public    = os.getenv("CW_PUBLIC_KEY", "DIAGNOSTIC")
        self.private   = os.getenv("CW_PRIVATE_KEY", "DIAGNOSTIC")
        self.client_id = os.getenv("CW_CLIENT_ID", "itcubed-mcp")
        self.base_url  = "https://httpbin.org" # DIAGNOSTIC URL

        creds = f"{self.company}+{self.public}:{self.private}"
        token = base64.b64encode(creds.encode()).decode()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "ClientID":      self.client_id,
            "Accept": "application/vnd.connectwise.com+json; version=2025.1",
            "X-Amz-Trace-Id": "For-Testing-Only" # Custom header to test casing
        })
        logging.info(f"DIAGNOSTIC MODE: ConnectWiseClient initialized for httpbin.org.")

    def _get(self, url, **params):
        logging.info(f"Making DIAGNOSTIC request to: {url}")
        r = self.session.get(url, params=params, timeout=30)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return r.json()

    def latest_ticket(self):
        # This will now call httpbin and return the headers it sees
        return self._get(f"{self.base_url}/headers")
    
    # --- All other methods are effectively disabled in this mode ---
    def search_tickets(self, status=None, page=1, page_size=25): return {"error": "diagnostic_mode"}
    def list_tickets(self, page=1, page_size=25): return {"error": "diagnostic_mode"}
    def get_company(self, id: int): return {"error": "diagnostic_mode"}
    def get_contact(self, id: int): return {"error": "diagnostic_mode"}
