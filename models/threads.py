from dataclasses import dataclass, field
from typing import List

@dataclass
class Comment:
    author_name: str
    text: str
    avatar_url: str
    replies: List['Comment'] = field(default_factory=list)

@dataclass
class CommentThread:
    comments: List[Comment]