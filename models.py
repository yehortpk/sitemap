from dataclasses import dataclass


@dataclass
class ScrappingResult:
    url: str
    status: int
    html: str
