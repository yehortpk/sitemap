from parser import HTMLParser
from scrapper import StaticScrapper


class ScrapperRunner:
    @staticmethod
    async def handle_request(url: str) -> dict[str, list[str]]:
        res = await StaticScrapper(url).fetch()
        parser = HTMLParser(res.html)
        links = parser.extract_same_host_links(url)
        return links
