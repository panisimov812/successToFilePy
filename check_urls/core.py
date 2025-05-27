import time
import os
import base64
from datetime import datetime
from typing import Dict, Optional, Tuple
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from requests.exceptions import RequestException
from .http_client import HttpClient
from rich.console import Console
from rich.progress import track

console = Console()

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
            console.print(f"[yellow]→ Редирект (Код {status_code}): {url}[/yellow]")
            response = http_client.get(url, allow_redirects=False, headers=headers)
            new_url = response.headers.get("Location")
            if new_url:
                console.print(f"[yellow]  Переход на: [underline]{new_url}[/underline][/yellow]")
                HttpStatusHandler.handle_success_status(
                    http_client.get(new_url, headers=headers).status_code, new_url, writer
                )

    @staticmethod
    def handle_error_status(status_code: int, url: str):
        if status_code < 200 or status_code >= 400:
            console.print(f"[red]× Ошибка (Код {status_code}): {url}[/red]")

    @staticmethod
    def handle_network_error(url: str, error: Exception):
        console.print(f"[purple]! Сетевая ошибка при обработке {url}: {error}[/purple]")

class CheckUrlsCore:
    def __init__(self):
        self.http_client = HttpClient()
        self.status_handler = HttpStatusHandler()
        self.report_data = {
            "details": [],
            "summary": {"total": 0, "success": 0, "redirects": 0, "errors": 0, "network_errors": 0}
        }

    def _generate_pie_chart(self) -> str:
        """Генерирует круговую диаграмму статусов в base64."""
        fig, ax = plt.subplots(figsize=(6, 6))
        labels = ['Success (2xx)', 'Redirects (3xx)', 'Errors (4xx/5xx)', 'Network Errors']
        sizes = [
            self.report_data["summary"]["success"],
            self.report_data["summary"]["redirects"],
            self.report_data["summary"]["errors"],
            self.report_data["summary"]["network_errors"]
        ]
        colors = ['#4CAF50', '#FFC107', '#F44336', '#9C27B0']
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')
        ax.set_title('Status Distribution')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _generate_response_time_chart(self) -> str:
        """Генерирует гистограмму времени ответа в base64."""
        if not self.report_data["details"]:
            return ""

        response_times = [item["response_time"] for item in self.report_data["details"] if item["response_time"]]
        if not response_times:
            return ""

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(response_times, bins=10, color='#2196F3', edgecolor='black')
        ax.set_xlabel('Response Time (ms)')
        ax.set_ylabel('Frequency')
        ax.set_title('Response Time Distribution')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')


    def _save_html_report(self, output_file: str):
        """Сохраняет HTML-отчёт с графиками."""
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
        template = env.get_template('report_template.html')

        html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=self.report_data["summary"],
            details=self.report_data["details"],
            pie_chart=f"data:image/png;base64,{self._generate_pie_chart()}",
            response_time_chart=f"data:image/png;base64,{self._generate_response_time_chart()}"
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

    def check_urls(self, input_file: str, output_file: str,
                 headers: Optional[Dict[str, str]] = None,
                 normalize: bool = True,
                 report_file: Optional[str] = None):
        """Основной метод проверки URL."""
        try:
            with open(input_file, "r") as input_f:
                urls = [url.strip() for url in input_f if url.strip()]

            with open(output_file, "w") as output_f:
                for url in track(urls, description="[blue]Проверка URL..."):
                    normalized_url = normalize_url(url) if normalize else url
                    start_time = time.time()

                    try:
                        response = self.http_client.get(normalized_url, headers=headers)
                        response_time = int((time.time() - start_time) * 1000)

                        # Запись данных для отчёта
                        self._update_report_data(normalized_url, response.status_code, response_time)
                        self._handle_response(response, normalized_url, output_f, headers)

                    except RequestException as e:
                        self._handle_network_error(normalized_url, e)

            if report_file:
                self._save_html_report(report_file)

        except IOError as e:
            console.print(f"[bold red]Ошибка работы с файлами: {e}[/bold red]")

    def _update_report_data(self, url: str, status_code: int, response_time: int):
        """Обновляет данные для отчёта."""
        self.report_data["details"].append({
            "url": url,
            "status": status_code,
            "response_time": response_time
        })

        if 200 <= status_code < 300:
            self.report_data["summary"]["success"] += 1
        elif 300 <= status_code < 400:
            self.report_data["summary"]["redirects"] += 1
        else:
            self.report_data["summary"]["errors"] += 1
        self.report_data["summary"]["total"] += 1

    def _handle_response(self, response, url: str, output_f, headers: Optional[Dict[str, str]]):
        """Обрабатывает HTTP-ответ."""
        if 200 <= response.status_code < 300:
            self.status_handler.handle_success_status(response.status_code, url, output_f)
        elif 300 <= response.status_code < 400:
            self.status_handler.handle_redirect_status(
                response.status_code, url, output_f, self.http_client, headers
            )
        else:
            self.status_handler.handle_error_status(response.status_code, url)

    def _handle_network_error(self, url: str, error: Exception):
        """Обрабатывает сетевые ошибки."""
        self.report_data["details"].append({
            "url": url,
            "status": None,
            "response_time": None
        })
        self.report_data["summary"]["network_errors"] += 1
        self.report_data["summary"]["total"] += 1
        self.status_handler.handle_network_error(url, error)