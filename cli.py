import logging
from pathlib import Path
from app.serializers import Language, TTSType
from app.file import FileStory
from click.core import Context, Option
from typing import Optional
from app.telegram_handler import send_to_telegram
from app.tts_stories import merge_audio_files

import click

from app.wattpad import Wattpad
from app.ao3 import AO3
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
    "--language",
    type=click.Choice(Language.list()),
    default=Language.SPANISH,
    prompt="Story's language",
    help=f"""Story's language.
        Available languages:
        {Language.available_str_values()}
    """,
)
@click.option(
    "--tts_type",
    type=click.Choice(TTSType.list()),
    default=TTSType.GOOGlE,
    prompt="TTS model Type",
    help=f"""Available TTS:
        {TTSType.available_str_values()}
    """,
)
@click.option(
    "--file/--no-file",
    is_flag=True,
    default=False,
    callback=prompt_file,
)
@click.option(
    "--wattpad/--no-wattpad",
    is_flag=True,
    default=False,
    callback=prompt_wattpad,
)
@click.option(
    "--ao3/--no-ao3",
    is_flag=True,
    default=False,
    callback=prompt_ao3,
)
def run(
    language: Language,
    tts_type: TTSType,
    wattpad: str,
    file: str,
    ao3: str,
) -> None:
    """Runs the tts for the given story"""
    if file:
        file_path = CURRENT_PATH.joinpath(file)
        story = FileStory(file_path, language, tts_type)
        story.run()

    if wattpad:
        story = Wattpad(url=wattpad, language=language)
        filename = story.save()
        if filename is not None:
            file_story = FileStory(filename, story.story.language, tts_type)
            file_story.run()

    if ao3:
        story = AO3(url=ao3, language=language)
        filename = story.save()
        if filename is not None:
            file_story = FileStory(filename, story.story.language, tts_type)
            file_story.run()


@cli.command()
@click.option(
    "--filename",
    default="UNKNOWN",
    type=str,
    prompt="Filename",
    help="Filename for the output, default value is UNKNOWN",
)
@click.option(
    "--path",
    type=Path,
    prompt="Folder's path",
    help="Path for the output with the *.mp3 files",
)
def merge(filename: str, path: Path) -> None:
    """Merge *.mp3 files from a path"""
    merge_audio_files(filename, path)


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
def run_tts(source: str, out_path: Path, google: bool):
    path = out_path.joinpath("out.mp3") if out_path.is_dir() else out_path
    if google:
        return make_tts(
            source=source,
            tts_type=TTSType.GOOGlE,
            out_path=path,
        )
    return make_tts(source=source, out_path=path)


if __name__ == "__main__":
    cli()
