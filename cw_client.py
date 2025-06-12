import os, base64, requests

class ConnectWiseClient:
    """
    Thin wrapper around the ConnectWise REST API.
    Only GET (read) calls for now.
    """
    def __init__(self):
        self.company   = os.getenv("CW_COMPANY")     # e.g. ITCUBED
        self.public    = os.getenv("CW_PUBLIC_KEY")
        self.private   = os.getenv("CW_PRIVATE_KEY")
        self.client_id = os.getenv("CW_CLIENT_ID")   # arbitrary 5–32 char string
        self.base_url  = os.getenv("CW_BASE_URL", "https://api-na.myconnectwise.net/v2025_1")
        if not all([self.company, self.public, self.private, self.client_id]):
            raise RuntimeError("CW_* env vars not fully set")

        # Basic‑auth header is “CompanyID+PublicKey:PrivateKey”, base64‑encoded
        creds = f"{self.company}+{self.public}:{self.private}"
        token = base64.b64encode(creds.encode()).decode()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "clientId":      self.client_id,
            "Accept":        "application/json"
        })

    # ---------- helper methods ----------

    def _get(self, url, **params):
        r = self.session.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    # ---------- public API used by FastAPI routes ----------

    def search_tickets(self, status=None, page=1, page_size=25):
        params = {"page": page, "pageSize": page_size}
        if status:
            params["conditions"] = f'status/name="{status.capitalize()}"'
        return self._get(f"{self.base_url}/service/tickets", **params)

    def latest_ticket(self):
        data = self._get(f"{self.base_url}/service/tickets",
                         orderBy="_info.lastUpdated desc",
                         pageSize=1)
        return data[0] if data else {}

    def list_tickets(self, page=1, page_size=25):
        return self.search_tickets(page=page, page_size=page_size)

    def get_company(self, id: int):
        return self._get(f"{self.base_url}/company/companies/{id}")

    def get_contact(self, id: int):
        return self._get(f"{self.base_url}/company/contacts/{id}")
