from dataclasses import dataclass

@dataclass
class ScrapperConfig:
    headers: list[tuple[str, str]] = None
    cookies: list[tuple[str, str]] = None
    proxy: str = None
    timeout_ms: float = 5000

@dataclass
class ScrappingResult:
    url: str
    status: int
    html: str