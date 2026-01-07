from dataclasses import dataclass

#data model to store articles under
@dataclass
class Article:
    title: str
    link: str
    description: str
    pub_date: str
    source: str