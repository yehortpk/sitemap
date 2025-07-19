import re
from urllib.parse import urldefrag, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from collections import defaultdict

from lxml import html


class HTMLParser:
    def __init__(self, content: str):
        self.content = content
        self.tree = html.fromstring(self.content)

    def extract_links(self, base_url: str = None, domain:str = None) -> dict[str, set[str]]:
        """
        Extracts links from `tree`
        :param base_url:
        :param domain:
        :return:
        """
        if base_url:
            self.tree.make_links_absolute(base_url)

        links: dict[str, set] = {}

        for element, attribute, link, pos in self.tree.iterlinks():
            if element.tag == 'a' and attribute == "href":
                link_domain, url = self._extract_domain(link), self._normalize_url(link)
                if link_domain is None and domain:
                    link_domain = domain

                domain_links = links.get(link_domain, set())
                domain_links.add(url)
                links[link_domain] = domain_links

        return links

    def extract_same_domain_links(self, domain: str) -> dict[str, list[str]]:
        """
        Extracts links from the same domain
        :param domain:
        :return:
        """
        same_domain_links = defaultdict(list)
        domain = self._extract_domain(domain)

        links = self.extract_links(domain)
        for links_domain in links:
            if links_domain and links_domain.endswith(domain):
                same_domain_links[links_domain].extend(links[links_domain])

        return same_domain_links

    @staticmethod
    def _extract_domain(url: str):
        if not url:
            return None

        #In case scheme not specified
        if not url.startswith("https://"):
            url = "https://" + url

        domain = urlparse(url).netloc

        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9]'  # First character of the domain
            r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'  # Sub domain + hostname
            r'[a-zA-Z]{2,}$'  # TLD
        )

        if not url or not domain_regex.match(domain):
            return None

        return domain

    @staticmethod
    def _normalize_url(url: str):
        parsed = urlparse(url)
        scheme, netloc, path, params, query, fragment = parsed

        if not scheme:
            # Check if netloc is empty; if so, treat path as netloc
            if not netloc and path and '.' in path.split('/')[0]:
                netloc = path.split('/')[0]
                path = '/' + '/'.join(path.split('/')[1:])
            scheme = "https://"

        if not netloc and path:
            # In case the URL is just a path without domain, leave it as-is
            return urlunparse((scheme, '', path, params, query, ''))

        normalized = urlunparse((scheme, netloc, path, params, query, ''))
        return normalized


class RobotsParser:
    def __init__(self, host: str):
        self.robots_parser = RobotFileParser()
        self.robots_parser.set_url(f"{host}/robots.txt")
        self.robots_parser.read()

    def can_fetch(self, url) -> bool:
        return self.robots_parser.can_fetch('*', url)