from dataclasses import dataclass

@dataclass
class Article:
    title: str
    link: str
    description: str
    pub_date: str
    source: str