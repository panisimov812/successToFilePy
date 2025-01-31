import click
from typing import Dict, Optional, Tuple
from .core import CheckUrlsCore, normalize_url

@click.command()
@click.option("--input", required=True, help="Path to input file")
@click.option("--output", required=True, help="Path to output file")
@click.option("--header", multiple=True, help="Headers in format 'Key:Value'")
@click.option("--no-normalize", is_flag=True, help="Disable URL normalization (do not add 'https://www.')")
def check_urls(input: str, output: str, header: Optional[Tuple[str]] = None, no_normalize: bool = False):
    """
    Проверяет URL-адреса из файла и записывает успешные в выходной файл.

    :param input: Путь к файлу с URL-адресами.
    :param output: Путь к файлу для записи успешных URL-адресов.
    :param header: Заголовки в формате 'Key:Value'.
    :param no_normalize: Отключить нормализацию URL.
    """
    headers = None
    if header:
        headers = {}
        for h in header:
            key, value = h.split(":", 1)
            headers[key.strip()] = value.strip()

    core = CheckUrlsCore()
    core.check_urls(input, output, headers, not no_normalize)

if __name__ == "__main__":
    check_urls()