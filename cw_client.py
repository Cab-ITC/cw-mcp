import os, base64, requests, logging
from fastapi import HTTPException

# Configure logging to make sure messages appear in Fly's logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConnectWiseClient:
    """
    Minimal read-only wrapper over ConnectWise Manage REST API.
    """

    def __init__(self):
        self.company   = os.getenv("CW_COMPANY")
        self.public    = os.getenv("CW_PUBLIC_KEY")
        self.private   = os.getenv("CW_PRIVATE_KEY")
        self.client_id = os.getenv("CW_CLIENT_ID")
        self.base_url  = os.getenv(
            "CW_BASE_URL",
            "https://api-na.myconnectwise.net/v2025_1/apis/3.0"
        )
        if not all([self.company, self.public, self.private, self.client_id]):
            raise RuntimeError("CW_* env vars not fully set")

        creds = f"{self.company}+{self.public}:{self.private}"
        token = base64.b64encode(creds.encode()).decode()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "ClientID":      self.client_id,  # case-sensitive!
            "Accept": "application/vnd.connectwise.com+json; version=2025.1"
        })
        
        logging.info(f"ConnectWiseClient initialized. Effective headers: {self.session.headers}")


    # ---------- helper ----------
    def _get(self, url, **params):
        logging.info(f"Making upstream ConnectWise request to: {url}")
        r = self.session.get(url, params=params, timeout=30)
        if r.status_code >= 400:
            logging.error(f"Upstream API Error! Status: {r.status_code}. URL: {r.url}. Response Body: '{r.text}'")
            raise HTTPException(r.status_code, r.text or f"Upstream ConnectWise API returned status {r.status_code} with no detail.")
        return r.json()

    # ---------- public wrappers ----------
    def search_tickets(self, status=None, page=1, page_size=25):
        p = {"page": page, "pageSize": page_size}
        if status:
            p["conditions"] = f'status/name="{status.capitalize()}"'
        return self._get(f"{self.base_url}/service/tickets", **p)

    def latest_ticket(self):
        data = self._get(
            f"{self.base_url}/service/tickets",
            orderBy="_info.lastUpdated desc",
            pageSize=1
        )
        return data[0] if data else {}

    def list_tickets(self, page=1, page_size=25):
        return self.search_tickets(page=page, page_size=page_size)

    def get_company(self, id: int):
        return self._get(f"{self.base_url}/company/companies/{id}")

    def get_contact(self, id: int):
        return self._get(f"{self.base_url}/company/contacts/{id}")
