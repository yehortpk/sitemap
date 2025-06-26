from urllib.parse import urldefrag, urlparse
from urllib.robotparser import RobotFileParser

from lxml import html

class HTMLParser:
    def __init__(self, content: str):
        self.content = content
        self.tree = html.fromstring(self.content)


    def extract_same_host_links(self, url: str):
        host = urlparse(url).hostname
        self.tree.make_links_absolute(url)

        links = [
            clean_url
            for element, attribute, link, pos in self.tree.iterlinks()
            if element.tag == "a" and attribute == "href"
               and urlparse(clean_url := urldefrag(link).url).hostname == host
        ]

        return list(links)

class RobotsParser:
    def __init__(self, host: str):
        self.robots_parser =  RobotFileParser()
        self.robots_parser.set_url(f"{host}/robots.txt")
        self.robots_parser.read()

    def can_fetch(self, url) -> bool:
        return self.robots_parser.can_fetch("*", url)