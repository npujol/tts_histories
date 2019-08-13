import sys
import re
import html
import os
import argparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from gtts import gTTS
from collections import namedtuple

URL_BASE = "https://www.wattpad.com"

Chapter = namedtuple("Chapter", field_names=["id", "url", "title", "content"])
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
            .encode("ascii", "ignore")
            .decode("utf-8")
            .partition("-")[0]
            .strip()
        )
        self.title = RE_CLEAN.sub(" ", title)
        author = html_story.find("a", attrs={"class": "send-author-event on-navigate"})
        self.author = "".join(e.string for e in author)

        summary = html_story.find("pre")
        self.summary = "".join(e.string for e in summary)

        index_story = html_story.find_all("li", attrs={"data-part-id": True})
        for t in index_story:
            url_chapter = (
                URL_BASE
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
    def __init__(self, url):
        self.url = url
        self.title = ""
        self.content = ""
        self.extract_info()

    def extract_info(self):
        chapter_html = get_content(self.url)
        title = (
            str(chapter_html.title.string)
            .encode("ascii", "ignore")
            .decode("utf-8")
            .partition("-")[0]
            .strip()
        )
        self.title = RE_CLEAN.sub(" ", title)
        self.content = self.chapter_content(chapter_html).replace(" y ", ", y ")

    def create_TTS(self):
        tts = gTTS(spanish_correction(self.title + " " + self.content), lang="es")
        tts.save(f"{self.title}.mp3")
        print("Chapter tts story")

    def chapter_content(self, chapter_html):
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
            page = self.url + f"/page/{i}"
            chapter_html = get_content(page)
            return content


class FileStory:
    def __init__(self, filename, language="es"):
        self.filename = filename
        self.language = language
        self.text_story = ""
        self.clean_text()

    def clean_text(self):
        with open(self.filename) as f:
            content = f.readlines()
        content = " ".join([x.strip() for x in content])
        self.text_story = content

    def create_TTS(self):
        tts = gTTS(spanish_correction(self.text_story), lang=self.language)
        file_name = self.filename.split(".")
        tts.save("{}.mp3".format(file_name[0]))
        print("Complete tts story")


def get_content(url):
    MOZILLA = {"User-Agent": "Mozilla/5.0"}
    req = Request(url, headers=MOZILLA)
    html_content = urlopen(req).read()
    return BeautifulSoup(html_content, "html.parser")


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
    parser.add_argument("-f", "--file", help="from direction", action="store_true")
    parser.add_argument(
        "-ch", "--chapter", help="from Wattad chapter", action="store_true"
    )
    args = parser.parse_args()

    if args.story_dir and os.path.isfile(args.story_dir):
        story = FileStory(args.story_dir)
    elif args.wattpad:
        story = WattpadStory(args.story_dir)
        story.save_text_story()
    elif args.chapter:
        story = WattapadChapter(args.story_dir)
    else:
        parser.help
    story.create_TTS()
