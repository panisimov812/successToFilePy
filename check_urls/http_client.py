import requests
from requests import Response
from typing import Optional, Dict

class HttpClient:
    def __init__(self):
        self.session = requests.Session()

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, allow_redirects: bool = True) -> Response:
        return self.session.get(url, headers=headers, allow_redirects=allow_redirects, timeout=10)