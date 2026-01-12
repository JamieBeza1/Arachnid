from dataclasses import dataclass, field
# allows optional fields for when AI is uncertain
from typing import Optional, List

#data model to store articles under
@dataclass
class Article:
    title: str
    link: str
    description: str
    pub_date: str
    source: str
    keywords: list[str] = field(default_factory=list)

# AI related object models    
    
@dataclass
class SoftwareIdentity:
    vendor: str
    product: str
    version: str
    cve: str

@dataclass
class TitleExtraction:
    vendor: Optional[str] = None
    product: Optional[str] = None
    confidence: float = 0.0

@dataclass
class ArticleExtraction:
    vendor: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    cves: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    keywords: List[str]  = field(default_factory=list)
    