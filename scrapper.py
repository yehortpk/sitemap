import aiohttp
from aiohttp import ClientTimeout

from config import ScrapperConfig
from models import ScrappingResult

class StaticScrapper:
    def __init__(self, url: str):
        self.url = url


    async def fetch(self) -> ScrappingResult:
        config: ScrapperConfig = ScrapperConfig(self.url)

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

