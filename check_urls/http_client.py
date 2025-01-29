import requests
from requests import Response

class HttpClient:
    def __init__(self):
        self.session = requests.Session()

    def get(self, url: str, allow_redirects: bool = True) -> Response:
        return self.session.get(url, allow_redirects=allow_redirects, timeout=10)