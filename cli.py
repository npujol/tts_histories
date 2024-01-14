import logging
from pathlib import Path
from app.serializers import TTSType
from app.telegram_handler import send_to_telegram

import click

from app.main import make_tts


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

CURRENT_PATH = Path(__file__).parent


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
    type=str,
    prompt="source",
    help="source for the output, can be a url or a path",
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
    "--save_text/--no_save_text",
    is_flag=True,
    default=False,
)
@click.option(
    "--telegram/--no-send",
    is_flag=True,
    default=False,
)
def run_tts(
    source: str,
    out_path: Path,
    google: bool,
    save_text: bool,
    telegram: bool,
):
    if google:
        return make_tts(
            source=source,
            tts_type=TTSType.GOOGlE,
            out_path=out_path,
            shall_save_text=save_text,
            shall_send_to_telegram=telegram,
        )
    return make_tts(
        source=source,
        out_path=out_path,
        shall_save_text=save_text,
        shall_send_to_telegram=telegram,
    )


if __name__ == "__main__":
    cli()
