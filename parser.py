from urllib.parse import urldefrag, urlparse
from urllib.robotparser import RobotFileParser

from lxml import html

class HTMLParser:
    def __init__(self, content: str, hostname: str = None):
        self.content = content
        self.tree = html.fromstring(self.content)

        if hostname:
            parsed_url = urlparse(hostname)
            if parsed_url.scheme:
                self.hostname = parsed_url.scheme + parsed_url.path
            self.hostname = "https://" + parsed_url.path


    def extract_links(self) -> dict[str, list[str]]:
        if self.hostname:
            self.tree.make_links_absolute(self.hostname)

        links = {}

        for element, attribute, link, pos in self.tree.iterlinks():
            if element.tag == 'a' and attribute == "href":
                link_hostname, url = urlparse(link).hostname, urldefrag(link).url
                if link_hostname is None and self.hostname:
                    link_hostname = self.hostname

                host_links: list[str] = links.get(link_hostname, [])
                host_links.append(url)
                links[link_hostname] = host_links


        return links

class RobotsParser:
    def __init__(self, host: str):
        self.robots_parser =  RobotFileParser()
        self.robots_parser.set_url(f"{host}/robots.txt")
        self.robots_parser.read()

    def can_fetch(self, url) -> bool:
        return self.robots_parser.can_fetch('*', url)