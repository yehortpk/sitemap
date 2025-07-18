import asyncio
import logging

from aiohttp import ClientResponseError, ClientError
from lxml.etree import ParserError

from parser import HTMLParser
from scrapper import StaticScrapper

logger = logging.getLogger(__name__)


class ScrapperRunner:
    @staticmethod
    async def handle_request(url: str) -> dict[str, list[str]]:
        try:
            res = await StaticScrapper(url).fetch()
        except ClientResponseError as e:
            logger.error(f"HTTP error {e.status} for URL {url}: {e.message}")
            # Handle or log specific HTTP error codes
            return {}

        except ClientError as e:
            # This covers connection errors, timeouts, etc.
            logger.error(f"Client error for URL {url}: {e}")

            return {}

        except asyncio.TimeoutError:
            logger.error(f"Timeout error for URL {url}")

            return {}

        except Exception as e:
            # Catch-all for unexpected exceptions
            logger.error(f"Unexpected error for URL {url}: {e}")

            return {}

        try:
            parser = HTMLParser(res.html)
            links = parser.extract_same_domain_links(url)
            return links
        except ParserError as e:
            logger.error(f"{url} {e}")
            return {}

        except Exception as e:
            # Catch-all for unexpected exceptions
            logger.error(f"Unexpected error for URL {url}: {e}")

            return {}


