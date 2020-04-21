from dataclasses import dataclass


@dataclass(frozen=True)
class MetaInfo:
    title: str = None
    title_original: str = None
    description: str = None
    country: str = None
    url_info: str = None
