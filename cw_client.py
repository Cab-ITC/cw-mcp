import os, base64, requests
from fastapi import HTTPException

class ConnectWiseClient:
    """
    Thin wrapper around the ConnectWise REST API (read-only for now).
    """

    def __init__(self):
        # ---------- credentials ----------
        self.company   = os.getenv("CW_COMPANY")          # e.g. itcubed
        self.public    = os.getenv("CW_PUBLIC_KEY")       # from API Keys tab
        self.private   = os.getenv("CW_PRIVATE_KEY")      # from API Keys tab
        self.client_id = os.getenv("CW_CLIENT_ID")        # 5-32 chars, letters / numbers / dashes

        # canonical base path *must* include /apis/3.0/
        self.base_url = os.getenv(
            "CW_BASE_URL",
            "https://api-na.myconnectwise.net/v2025_1/apis/3.0"
        )
        if not all([self.company, self.public, self.private, self.client_id]):
            raise RuntimeError("CW_* env vars not fully set")

        # ---------- build session ----------
        creds = f"{self.company}+{self.public}:{self.private}"
        token = base64.b64encode(creds.encode()).decode()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "ClientID":      self.client_id,  # exact case matters
            # versioned Accept header required by CW 
            #   (2025.1 in cloud NA right now – change when CW bumps)
            "Accept": "application/vnd.connectwise.com+json; version=2025.1"
        })

    # ---------- helper ----------
    def _get(self, url: str, **params):
        r = self.session.get(url, params=params, timeout=30)
        if r.status_code >= 400:
            # bubble ConnectWise error straight to FastAPI / caller
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

    # ---------- public wrappers ----------
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
