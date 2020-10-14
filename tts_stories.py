import sys
import re
import html
import os
import argparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from gtts import gTTS
from recordtype import recordtype

# Available tts languages
LANGUAGE = [
    "af-ZA",
    "sq",
    "ar-AE",
    "hy",
    "bn-BD",
    "bn-IN",
    "bs",
    "my",
    "ca-ES",
    "cmn-Hant-TW",
    "hr-HR",
    "cs-CZ",
    "da-DK",
    "nl-NL",
    "en-AU",
    "en-GB",
    "en-US",
    "eo",
    "fil-PH",
    "fi-FI",
    "fr-FR",
    "fr-CA",
    "de-DE",
    "el-GR",
    "gu",
    "hi-IN",
    "hu-HU",
    "is-IS",
    "id-ID",
    "it-IT",
    "ja-JP",
    "kn",
    "km",
    "ko-KR",
    "la",
    "lv",
    "mk",
    "ml",
    "mr",
    "ne",
    "nb-NO",
    "pl-PL",
    "pt-BR",
    "ro-RO",
    "ru-RU",
    "sr-RS",
    "si",
    "sk-SK",
    "es-MX",
    "es-ES",
    "sw",
    "sv-SE",
    "ta",
    "te",
    "th-TH",
    "tr-TR",
    "uk-UA",
    "vi-VN",
    "cy",
]
URL_BASE_WATTPAD = "https://www.wattpad.com"
WATTPAD_BASE_DIR = os.getcwd()

Chapter = recordtype(
    "Chapter", field_names=["title", "url", "saved_text", "saved_audio"]
)
RE_CLEAN = re.compile(r"\/")
RE_SPACES = re.compile(r"\s+")


class WattpadStory:
    def __init__(self, url, language="es"):
        self.url = url
        self.language = language
        self.title = ""
        self.author = ""
        self.summary = ""
        self.chapters = []
        self.get_info()
        self.make()

    def get_info(self):
        html_story = get_content(self.url)

        title = str(html_story.title.string).split("-")[0]
        self.title = RE_CLEAN.sub(" ", title)

        if not os.path.exists(os.path.join(WATTPAD_BASE_DIR, self.title)):
            os.mkdir(os.path.join(WATTPAD_BASE_DIR, self.title))

        author = html_story.find("a", attrs={"class": "send-author-event on-navigate"})
        self.author = "".join(e.string for e in author)

        summary = html_story.find("pre")
        self.summary = "".join(e.string for e in summary)

        if not os.path.isfile(
            os.path.join(WATTPAD_BASE_DIR, self.title, f"{self.title} Index.txt")
        ) or not os.path.isfile(
            os.path.join(WATTPAD_BASE_DIR, self.title, f"{self.title} Summary.txt")
        ):
            self.get_chapters(html_story)
        else:
            self.load_chapters()

    def get_chapters(self, html_story):
        story_chapters = html_story.find_all("li", attrs={"data-part-id": True})
        for ch in story_chapters:
            url_chapter = (
                URL_BASE_WATTPAD
                + html.unescape(ch.a.get("href")).replace("\u2022" * 3, "").strip()
            )
            self.chapters.append(
                Chapter(
                    ch.a.text.strip(),
                    url_chapter,
                    "",
                    "",
                )
            )
        save_text(
            f"{self.title} Summary",
            "\n".join([self.title, self.author, self.summary]),
            os.path.join(WATTPAD_BASE_DIR, self.title),
        )
        save_text(
            f"{self.title} Index",
            "\n".join([",".join([val for val in ch]) for ch in self.chapters]),
            os.path.join(WATTPAD_BASE_DIR, self.title),
        )

    def load_chapters(self):
        content_chapters = read_content(
            os.path.join(WATTPAD_BASE_DIR, self.title, f"{self.title} Index.txt")
        )
        for line in content_chapters.split("\n"):
            title, url, saved_text, saved_audio = line.split(",")
            self.chapters.append(Chapter(title, url, saved_text, saved_audio))

    def make(self):
        for chapter in self.chapters:
            if chapter.saved_text == "":
                WattapadChapter(
                    chapter.url,
                    self.language,
                    self.title,
                    chapter.title,
                )
                chapter.saved_text = os.path.join(
                    WATTPAD_BASE_DIR, self.title, f"{chapter.title}.txt"
                )
                if chapter.saved_audio == "":
                    WattapadChapter(
                        chapter.url,
                        self.language,
                        self.title,
                        chapter.title,
                        chapter.saved_text,
                    )
                    chapter.saved_audio = os.path.join(
                        WATTPAD_BASE_DIR, self.title, f"{chapter.title}.mp3"
                    )

        save_text(
            f"{self.title} Index",
            "\n".join([",".join([val for val in ch]) for ch in self.chapters]),
            os.path.join(WATTPAD_BASE_DIR, self.title),
        )


class WattapadChapter:
    def __init__(self, url, language="es", story="", title="", filename=None):
        self.url = url
        self.story = story
        self.title = title
        self.text = ""
        self.language = language
        self.filename = filename
        self.extract_info()
        self.make()

    def make(self):
        if not self.filename and not os.path.isfile(
            os.path.join(WATTPAD_BASE_DIR, self.title, f"{self.title}.txt")
        ):
            self.filename = save_text(
                self.title,
                "\n".join([self.title, self.text]),
                os.path.join(WATTPAD_BASE_DIR, self.story),
            )
        else:
            print(f"{self.title} has been saved")
        if self.filename and not os.path.isfile(
            os.path.join(WATTPAD_BASE_DIR, self.story, f"{self.title}.mp3")
        ):
            FileStory(self.filename, self.language)
        else:
            print(f"{self.title} already has an audio")

    def extract_info(self):
        chapter_html = get_content(self.url)
        if self.title == "":
            title = str(chapter_html.title.string)
            self.title = title.strip()
        self.text = self.get_chapter_text(chapter_html)

    def get_chapter_text(self, chapter_html):
        text = ""
        i = 1
        while i == 1 or (str(i) in chapter_html.title.string):
            chapter_parts = chapter_html.findAll(attrs={"data-p-id": True})
            part = "\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in chapter_parts
            )
            text += part
            i += 1
            new_page_url = self.url + f"/page/{i}"
            chapter_html = get_content(new_page_url)
        return text


class FileStory:
    def __init__(self, filename, language="es"):
        self.filename = filename
        self.title = filename.split("/")[-1].split(".")[0]
        self.language = language
        self.text = read_content(self.filename)

        self.make()

    def make(self):
        print(f"Init tts story: {self.title}")
        create_TTS(self.filename.split(".")[0], self.text, self.language)
        print(f"Complete tts story: {self.title}")


def get_content(url):
    MOZILLA = {"User-Agent": "Mozilla/5.0"}
    req = Request(url, headers=MOZILLA)
    html_content = urlopen(req).read()
    return BeautifulSoup(html_content, "html.parser")


def read_content(filename):
    with open(filename, "r", encoding="utf8") as f:
        content = f.readlines()
    content = "\n".join([x.strip() for x in content])
    return content


def create_TTS(filename, text, language):
    tts = gTTS(text, lang=language)
    tts.save(f"{filename}.mp3")


def save_text(title, text, path):
    with open(os.path.join(path, f"{title}.txt"), "w", encoding="utf8") as outfile:
        print(f"Init save story: {title}")
        outfile.write(text)
        print(f"Complete save story: {title}")
    return os.path.join(path, f"{title}.txt")


def spanish_correction(text):
    PAUSE_CORRECTIONS = [
        [" y ", ", y "],
        [" o ", ", o "],
        [" pero ", ", pero "],
        [" *** ", ""],
    ]
    for val in PAUSE_CORRECTIONS:
        text = text.replace(val[0], val[1])
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("story_dir", help="story source")
    parser.add_argument(
        "-wp", "--wattpad", help="from Wattapd story", action="store_true"
    )
    parser.add_argument("-f", "--file", help="from local storage", action="store_true")
    parser.add_argument(
        "-ch", "--chapter", help="from Wattad chapter", action="store_true"
    )
    parser.add_argument(
        "-l",
        "--language",
        help="Language for the story",
        default="es",
        type=str,
        choices=LANGUAGE,
    )
    args = parser.parse_args()

    if args.story_dir and os.path.isfile(args.story_dir):
        story = FileStory(args.story_dir)
    elif args.wattpad:
        story = WattpadStory(args.story_dir)
    elif args.chapter:
        story = WattapadChapter(args.story_dir)
    else:
        print("What kind of story is it? Use --help")
