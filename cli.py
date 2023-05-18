import logging
from pathlib import Path
from app.serializers import TTSType
from click.core import Context, Option
from typing import Optional
from app.telegram_handler import send_to_telegram

import click

from app.main import make_tts


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

CURRENT_PATH = Path(__file__).parent


def prompt_file(
    ctx: Context,
    param: Option,
    is_file: bool,
) -> Optional[list[str]]:
    if is_file:
        value = ctx.params.get("path")
        if not value:
            value = click.prompt("Story's path")
        return value


def prompt_wattpad(
    ctx: Context, param: Option, is_wattpad: bool
) -> Optional[list[str]]:
    if is_wattpad:
        value = ctx.params.get("url")
        if not value:
            value = click.prompt("Wattpad story's url")
        return value


def prompt_ao3(
    ctx: Context, param: Option, is_ao3: bool
) -> Optional[list[str]]:
    if is_ao3:
        value = ctx.params.get("url")
        if not value:
            value = click.prompt("AO3 story's url")
        return value


# TODO Check https://typer.tiangolo.com/


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--path",
    type=Path,
    prompt="Folder's path",
    help="Path for the output with the *.mp3 files",
)
def send(path: Path) -> None:
    send_to_telegram(path, "temp")


@cli.command()
@click.option(
    "--source",
    default="UNKNOWN",
    type=str,
    prompt="source",
    help="source for the output, default value is UNKNOWN",
)
@click.option(
    "--out_path",
    type=Path,
    default="/home/naivy/Datos/tts__file_output/",
    prompt="Folder's path",
    help="Path for the output with the *.mp3 files",
)
def make_tts_coqui(source: str, out_path: Path) -> None:
    path = out_path.joinpath("out.mp3") if out_path.is_dir() else out_path
    make_tts(source=source, out_path=path)


@cli.command()
@click.option(
    "--source",
    default="UNKNOWN",
    type=str,
    prompt="source",
    help="source for the output, default value is UNKNOWN",
)
@click.option(
    "--out_path",
    type=Path,
    default="/home/naivy/Datos/tts__file_output/",
    prompt="Folder's path",
    help="Path for the output with the *.mp3 files",
)
@click.option(
    "--google/--no-google",
    is_flag=True,
    default=False,
)
@click.option(
    "--telegram/--no-send",
    is_flag=True,
    default=False,
)
def run_tts(source: str, out_path: Path, google: bool, telegram: bool):
    if google:
        return make_tts(
            source=source,
            tts_type=TTSType.GOOGlE,
            out_path=out_path,
            shall_send_to_telegram=telegram,
        )
    return make_tts(
        source=source,
        out_path=out_path,
        shall_send_to_telegram=telegram,
    )


if __name__ == "__main__":
    cli()
