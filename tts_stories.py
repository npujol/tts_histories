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

Chapter = recordtype("Chapter", field_names=["id", "url", "title", "content"])
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
        self.split_story()

    def split_story(self):
        html_story = get_content(self.url)

        title = (
            str(html_story.title.string)
        )
        self.title = RE_CLEAN.sub(" ", title)
        author = html_story.find("a", attrs={"class": "send-author-event on-navigate"})
        self.author = "".join(e.string for e in author)

        summary = html_story.find("pre")
        self.summary = "".join(e.string for e in summary)

        index_story = html_story.find_all("li", attrs={"data-part-id": True})
        for t in index_story:
            url_chapter = (
                URL_BASE_WATTPAD
                + html.unescape(t.a.get("href")).replace("\u2022" * 3, "").strip()
            )
            self.chapters.append(
                Chapter(
                    t.get("data-part-id"),
                    url_chapter,
                    html.unescape(t.text).replace("\u2022" * 3, "").strip(),
                    self.chapter_content(url_chapter).replace(" y ", ", y "),
                )
            )

    def chapter_content(self, url_chapter):
        chapter_html = get_content(url_chapter)
        content = ""
        i = 1
        while i == 1 or (str(i) in chapter_html.title.string):
            article_texts = chapter_html.findAll(attrs={"data-p-id": True})
            chapter = "\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in article_texts
            )
            content += chapter
            i += 1
            page = url_chapter + f"/page/{i}"
            chapter_html = get_content(page)
        return content

    def save_text_story(self):
        with open(f"{self.title}.txt", "w", encoding="utf8") as outfile:
            outfile.write("Título ")
            outfile.write(self.title)
            outfile.write(" Autor ")
            outfile.write(self.title)

            outfile.write(self.summary)
            for ch in self.chapters:
                outfile.write(ch.title)
                outfile.write(ch.content)
            print(f"{self.title}.txt")

    def create_TTS(self):
        for val, ch in enumerate(self.chapters):
            tts = gTTS(
                spanish_correction(ch.title + " " + ch.content), lang=self.language
            )
            tts.save(f"{self.title} Ch:{val}.mp3")
            print(f"{self.title} Ch:{val}.mp3")

        print("Complete tts story")


class WattapadChapter:
    def __init__(self, url, language="es", filename=None):
        self.url = url
        self.title = ""
        self.text = ""
        self.language = language
        self.filename = filename
        self.extract_info()
        self.make()

    def make(self):
        if not self.filename and not os.path.isfile(f"{self.title}.txt"):
            self.filename = save_text(self.title, " ".join([self.title, self.text]))
        else:
            print(f"{self.title} has been saved")
        if self.filename and not os.path.isfile(f"{self.title}.mp3"):
            FileStory(self.filename, self.language)
        else:
            print(f"{self.title} already has an audio")

    def extract_info(self):
        chapter_html = get_content(self.url)
        title = str(chapter_html.title.string)       
        self.title = RE_CLEAN.sub(" ", title)
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
        self.title = filename.split(".")[0]
        self.language = language
        self.text = read_content(self.filename)
        create_TTS(self.title, self.text, self.language)    

def get_content(url):
    MOZILLA = {"User-Agent": "Mozilla/5.0"}
    req = Request(url, headers=MOZILLA)
    html_content = urlopen(req).read()
    return BeautifulSoup(html_content, "html.parser")

def read_content(filename):
    with open(filename) as f:
        content = f.readlines()
    content = " ".join([x.strip() for x in content])
    return content

def create_TTS(title, text, language):
    print(f"Init tts story: {title}")
    tts = gTTS(text, lang=language)
    tts.save("{title}.mp3")
    print(f"Complete tts story: {title}")

def save_text(title, text):
        with open(f"{title}.txt", "w", encoding="utf8") as outfile:
            print(f"Init save story: {title}")
            outfile.write(text)
            print(f"Complete save story: {title}")
        return f"{title}.txt"

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
        default="es", type=str, 
        choices=LANGUAGE)
    args = parser.parse_args()

    if args.story_dir and os.path.isfile(args.story_dir):
        story = FileStory(args.story_dir)
    elif args.wattpad:
        story = WattpadStory(args.story_dir)
    elif args.chapter:
        story = WattapadChapter(args.story_dir)
    else:
        print("What kind of story is it? Use --help")

