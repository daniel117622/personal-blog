from typing import List
from dataclasses import dataclass

@dataclass
class ContentBlock:
    text     : str
    is_header: bool

@dataclass
class Article:
    id              : int
    title           : str
    date_created    : str
    author          : str
    topics          : List[str]
    article_img_link: str
    content_blocks  : List[ContentBlock]
    
@dataclass
class ArticleSummary:
    id              : int
    title           : str
    date_created    : str
    author          : str
    topics          : List[str]
    article_img_link: str
