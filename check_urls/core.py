from requests.exceptions import RequestException
from typing import Optional, Dict
from .http_client import HttpClient
from rich.console import Console
from rich.progress import track



def normalize_url(url: str) -> str:
    """
    Нормализует URL, добавляя 'https://www.', если это необходимо.

    :param url: Исходный URL.
    :return: Нормализованный URL.
    """
    if not url.startswith(("http://", "https://", "www.")):
        url = "https://www." + url
    elif url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
    elif url.startswith("www."):
        url = "https://" + url
    return url


console = Console()


class HttpStatusHandler:
    @staticmethod
    def handle_success_status(status_code: int, url: str, writer):
        if 200 <= status_code < 300:
            console.print(f"[green]✓ Успех (Код {status_code}): {url}[/green]")
            writer.write(f"{url}\n")

    @staticmethod
    def handle_redirect_status(status_code: int, url: str, writer, http_client: HttpClient,
                               headers: Optional[Dict[str, str]] = None):
        if 300 <= status_code < 308:
            console.print(f"yellow→ Редирект (Код {status_code}): {url}[/yellow]")
            response = http_client.get(url, allow_redirects=False, headers=headers)
            new_url = response.headers.get("Location")
            if new_url:
                console.print(f"[yellow] Переход на: [underline]{new_url}[/underline][/yellow]")
                print(f"Забираем {new_url} из Location в хедере")
                HttpStatusHandler.handle_success_status(
                    http_client.get(new_url, headers=headers).status_code, new_url, writer
                )
            else:
                print(f"Ошибка: заголовок Location отсутствует для {url}")

    @staticmethod
    def handle_error_status(status_code: int, url: str):
        if status_code < 200 or status_code >= 400:
            console.print(f"[red]× Ошибка (Код {status_code}): {url}[/red]")
            print(f"Ошибка (Код состояния: {status_code}): {url}")

    @staticmethod
    def handle_network_error(url: str, error: Exception):
        console.print(f"[purple]! Сетевая ошибка при обработке {url}: {error}[/purple]")


class CheckUrlsCore:
    def __init__(self):
        self.http_client = HttpClient()
        self.status_handler = HttpStatusHandler()

    def check_urls(self, input_file: str, output_file: str, headers: Optional[Dict[str, str]] = None,
                   normalize: bool = True):
        try:
            with open(input_file, "r") as input_f:
                urls = [url.strip() for url in input_f if url.strip()]

            with open(output_file, "w") as output_f:
                for url in track(urls, description="[blue]Проверка URL..."):
                    normalized_url = normalize_url(url) if normalize else url
                    try:
                        response = self.http_client.get(normalized_url, headers=headers)
                        self.status_handler.handle_success_status(response.status_code, normalized_url, output_f)
                        self.status_handler.handle_redirect_status(response.status_code, normalized_url, output_f,
                                                                   self.http_client, headers)
                        self.status_handler.handle_error_status(response.status_code, normalized_url)
                    except RequestException as e:
                        self.status_handler.handle_network_error(normalized_url, e)
        except IOError as e:
            console.print(f"[bold red]Ошибка работы с файлами: {e}[/bold red]")
