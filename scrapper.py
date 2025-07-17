import asyncio
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientTimeout, ClientResponseError, ClientError

from config import ScrapperConfig
from models import ScrappingResult


class StaticScrapper:
    def __init__(self, url: str):
        self.url = url
        self.hostname = urlparse(url).hostname

    async def fetch(self) -> ScrappingResult:
        config: ScrapperConfig = ScrapperConfig(self.url)

        try:
            async with aiohttp.ClientSession(
                    headers=config.headers,
                    cookies=config.cookies,
                    timeout=ClientTimeout(total=config.timeout_ms/1000)
            ) as session:
                async with session.get(self.url, proxy=config.proxy) as response:
                    html = await response.text()
                    result = ScrappingResult(
                        url=str(response.url),
                        status=response.status,
                        html=html
                    )

                    return result

        except ClientResponseError as e:
            print(f"HTTP error {e.status} for URL {self.url}: {e.message}")
            # Handle or log specific HTTP error codes
            return ScrappingResult(
                        url=str(response.url),
                        status=e.status,
                        html=""
                    )

        except ClientError as e:
            # This covers connection errors, timeouts, etc.
            print(f"Client error for URL {self.url}: {e}")

            return ScrappingResult(
                url=str(response.url),
                status=400,
                html=""
            )

        except asyncio.TimeoutError as e:
            print(f"Timeout error for URL {self.url}")

            return ScrappingResult(
                url=str(response.url),
                status=408,
                html=""
            )

        except Exception as e:
            # Catch-all for unexpected exceptions
            print(f"Unexpected error for URL {self.url}: {e}")

            return ScrappingResult(
                url=str(response.url),
                status=500,
                html=""
            )