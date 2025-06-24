import aiohttp

from models import ScrappingResult, ScrapperConfig

def import_config():
    import json
    import os

    CONFIG_FILEPATH = 'scrapper.json'

    if not os.path.exists(CONFIG_FILEPATH):
        print("scrapper.json doesn't exist, load default scrapper parameters")
        return ScrapperConfig()

    with open(CONFIG_FILEPATH, 'r') as file:
        data:dict[str, any] = json.load(file)
        return ScrapperConfig(
            headers=data.get('headers'),
            timeout_ms=data.get('timeout_ms'),
            cookies=data.get('cookies'),
            proxy=data.get('proxy')
        )



class StaticScrapper:
    def __init__(self, url: str):
        self.url = url

    async def fetch(self) -> ScrappingResult:
        config: ScrapperConfig = import_config()

        async with aiohttp.ClientSession(
                headers=config.headers,
                cookies=config.cookies,
                proxy=config.proxy,
                timeout=config.timeout_ms
        ) as session:
            async with session.get(self.url) as response:
                html = await response.text()
                result = ScrappingResult(
                    url=str(response.url),
                    status=response.status,
                    html=html
                )

                return result

