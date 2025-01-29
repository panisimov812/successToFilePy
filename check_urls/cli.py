import click
from .core import CheckUrlsCore

@click.command()
@click.option("--input", required=True, help="Path to input file")
@click.option("--output", required=True, help="Path to output file")
def check_urls(input: str, output: str):
    core = CheckUrlsCore()
    core.check_urls(input, output)

if __name__ == "__main__":
    check_urls()