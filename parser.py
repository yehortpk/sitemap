from urllib.parse import urldefrag, urlparse
from urllib.robotparser import RobotFileParser

from lxml import html


class HTMLParser:
    def __init__(self, content: str):
        self.content = content
        self.tree = html.fromstring(self.content)

    def extract_links(self, hostname: str = None) -> dict[str, list[str]]:
        if hostname:
            hostname = self._extract_hostname(hostname)
            self.tree.make_links_absolute(hostname)

        links = {}

        for element, attribute, link, pos in self.tree.iterlinks():
            if element.tag == 'a' and attribute == "href":
                link_hostname, url = self._extract_hostname(link), urldefrag(link).url
                if link_hostname is None and hostname:
                    link_hostname = hostname

                host_links: list[str] = links.get(link_hostname, [])
                host_links.append(url)
                links[link_hostname] = host_links

        return links

    def extract_same_host_links(self, hostname: str):
        hostname = self._extract_hostname(hostname)
        return self.extract_links(hostname).get(hostname, [])

    def _extract_hostname(self, url):
        parsed_url = urlparse(url)

        if not parsed_url.netloc:
            return None

        if parsed_url.scheme:
            hostname = parsed_url.scheme + "://" + parsed_url.netloc
        else:
            hostname = "https://" + parsed_url.netloc

        return hostname


class RobotsParser:
    def __init__(self, host: str):
        self.robots_parser = RobotFileParser()
        self.robots_parser.set_url(f"{host}/robots.txt")
        self.robots_parser.read()

    def can_fetch(self, url) -> bool:
        return self.robots_parser.can_fetch('*', url)