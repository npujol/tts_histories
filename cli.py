import logging
from pathlib import Path
from app.models import Language
from app.file import FileStory
from click.core import Context, Option
from typing import Optional
from app.tts_stories import combine_audio

import click

from app.wattpad import Wattpad
from app.ao3 import AO3


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


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--language",
    type=click.Choice(Language.list()),
    default=Language.SPANISH,
    prompt="Story's language",
    help="""Story's language.
        Available languages:
        SPANISH = "es-ES"
        ENGLISH = "en-US"
        GERMAN = "de-DE"
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
def run(language, wattpad, file, ao3) -> None:
    """Runs the tts for the given story"""
    if file:
        file_path = CURRENT_PATH.joinpath(file)
        story = FileStory(file_path, language)
        story.run()

    if wattpad:
        story = Wattpad(url=wattpad, language=language)
        filename = story.save()
        file_story = FileStory(filename, story.story.language)
        file_story.run()

    if ao3:
        story = AO3(url=ao3, language=language)
        filename = story.save()
        file_story = FileStory(filename, story.story.language)
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
def merge(filename, path) -> None:
    """Merge *.mp3 files from a path"""
    combine_audio(path, filename)


if __name__ == "__main__":
    cli()
