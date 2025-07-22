import logging
import re
from collections import defaultdict
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser

from lxml import html

from errors import URLFormattingException

logger = logging.getLogger(__name__)

class HTMLParser:
    """
    Parses HTML document into DOM tree object
    """
    def __init__(self, content: str, url: str = None):
        self.content = content
        self.tree = html.fromstring(self.content)
        if url:
            if not self._is_url_valid(url):
                raise URLFormattingException
            self.tree.make_links_absolute(url)

    def extract_links(self) -> dict[str, set[str]]:
        """
        Extracts links from `tree`
        :return:
        """

        links: dict[str, set] = {}

        for element, attribute, link, pos in self.tree.iterlinks():
            if element.tag == 'a' and attribute == "href":
                try:
                    link_domain, url = self._extract_domain_from_url(link), self._normalize_url(link)
                except URLFormattingException as e:
                    logger.error(f"{link}: {e}")
                    continue

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
        domain = self._extract_domain_from_url(domain)

        links = self.extract_links()
        for links_domain in links:
            if links_domain and links_domain.endswith(domain):
                same_domain_links[links_domain].extend(links[links_domain])

        return same_domain_links


    def _extract_domain_from_url(self, url: str) -> str|None:
        if not url or not self._is_url_valid(url):
            raise URLFormattingException()

        url = self._normalize_url(url)

        domain = urlparse(url).netloc
        if isinstance(domain, bytes):
            domain = domain.decode()

        # Check if domain is valid
        if not self._is_domain_valid(domain):
            return None

        return domain

    @staticmethod
    def _normalize_url(url: str) -> str:
        """
        Normalizes url - adds scheme if not exist, change case into lower
        :param url:
        :return:
        """
        url = url.lower()
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
            return urlunparse((scheme, '', path, params, query, '')).decode()

        normalized = urlunparse((scheme, netloc, path, params, query, ''))
        if not isinstance(normalized, str):
            normalized = normalized.decode()

        return normalized

    @staticmethod
    def _is_url_valid(url: str) -> bool:
        url_regex = re.compile(
             r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*(?:\.[a-zA-Z]{2,}))(?:/[^\s]*)?/?',
            re.IGNORECASE
        )

        return bool(url_regex.match(url))

    @staticmethod
    def _is_domain_valid(domain: str) -> bool:
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9]'  # First character of the domain
            r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'  # Sub domain + hostname
            r'[a-zA-Z]{2,}$'  # TLD
        )

        return bool(domain_regex.match(domain))

class RobotsParser:
    """
    Parses robots.txt from the domain
    """
    def __init__(self, domain: str):
        self.robots_parser = RobotFileParser()
        self.robots_parser.set_url(f"{domain}/robots.txt")
        self.robots_parser.read()

    def can_fetch(self, url) -> bool:
        """
        Checks if page could be scrapped
        :param url:
        :return:
        """
        return self.robots_parser.can_fetch('*', url)