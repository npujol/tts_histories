# from ao3 import AO3Loader
# from watpad import WTFLoader
from urllib.parse import urlparse

_loaders = [] # [AO3Loader(), WTFLoader()]

def load_article(url):
    parsed_url = urlparse(url)
    for loader in _loaders:
        if loader.can_handle(parsed_url):
            return loader.load(url)

