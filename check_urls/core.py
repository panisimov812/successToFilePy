import requests
from requests.exceptions import RequestException
from typing import Optional
from .http_client import HttpClient  # Добавьте этот импорт

class HttpStatusHandler:
    @staticmethod
    def handle_success_status(status_code: int, url: str, writer):
        if 200 <= status_code < 300:
            print(f"Успех (Код состояния: {status_code}): {url}")
            writer.write(f"{url}\n")

    @staticmethod
    def handle_redirect_status(status_code: int, url: str, writer, http_client):
        if 300 <= status_code < 308:
            response = http_client.get(url, allow_redirects=False)
            new_url = response.headers.get("Location")
            if new_url:
                print(f"Забираем {new_url} из Location в хедере")
                HttpStatusHandler.handle_success_status(
                    http_client.get(new_url).status_code, new_url, writer
                )
            else:
                print(f"Ошибка: заголовок Location отсутствует для {url}")

    @staticmethod
    def handle_error_status(status_code: int, url: str):
        if status_code < 200 or status_code >= 400:
            print(f"Ошибка (Код состояния: {status_code}): {url}")

class CheckUrlsCore:
    def __init__(self):
        self.http_client = HttpClient()  # Теперь HttpClient определен
        self.status_handler = HttpStatusHandler()

    def check_urls(self, input_file: str, output_file: str):
        try:
            with open(input_file, "r") as input_f, open(output_file, "w") as output_f:
                for url in input_f:
                    url = url.strip()
                    if not url.startswith("http"):
                        print(f"Некорректный URL: {url}")
                        continue

                    try:
                        response = self.http_client.get(url)
                        self.status_handler.handle_success_status(response.status_code, url, output_f)
                        self.status_handler.handle_redirect_status(response.status_code, url, output_f, self.http_client)
                        self.status_handler.handle_error_status(response.status_code, url)
                    except RequestException as e:
                        print(f"Сетевая ошибка при обработке {url}: {e}")
        except IOError as e:
            print(f"Ошибка работы с файлами: {e}")