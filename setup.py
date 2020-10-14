import os
from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="tts_stories",
    version="0.1",
    description="Create TSS from txt or Wattpad stories",
    url="https://github.com/npujol/tts_stories",
    author="Naivy Pujol Méndez",
    author_email="naivy.luna@gmail.com",
    license="MIT",
    py_modules=["tts_stories"],
    long_description=read("README.md"),
    zip_safe=False,
)
