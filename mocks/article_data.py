from dataclasses import dataclass
from typing import List

from models.article import Article , ArticleSummary , ContentBlock
from models.threads import CommentThread , Comment

def fill_article(article_id : int) -> Article:
    # In real life: data = requests.get(f'https://api.mysite.com/posts/{article_id}').json()
    return Article(
        id=article_id,
        title=f"This is a mock Post!",
        date_created="January 10, 2026",
        author="_Kühaku_",
        topics=["Mock topic", "Free", "Information Theory"],
        article_img_link="https://dummyimage.com/900x400/ced4da/6c757d.jpg",
        content_blocks=[
            ContentBlock(
                text="Science is an enterprise that should be cherished as an activity of the free human mind. Because it transforms who we are, how we live, and it gives us an understanding of our place in the universe.",
                is_header=False
            ),
            ContentBlock(
                text="The universe is large and old, and the ingredients for life as we know it are everywhere, so there's no reason to think that Earth would be unique in that regard. Whether of not the life became intelligent is a different question, and we'll see if we find that.",
                is_header=False
            ),
            ContentBlock(
                text="If you get asteroids about a kilometer in size, those are large enough and carry enough energy into our system to disrupt transportation, communication, the food chains, and that can be a really bad day on Earth.",
                is_header=False
            ),
            ContentBlock(
                text="I have odd cosmic thoughts every day",
                is_header=True
            ),
            ContentBlock(
                text="For me, the most fascinating interface is Twitter. I have odd cosmic thoughts every day and I realized I could hold them to myself or share them with people who might be interested.",
                is_header=False
            ),
            ContentBlock(
                text="Venus has a runaway greenhouse effect. I kind of want to know what happened there because we're twirling knobs here on Earth without knowing the consequences of it. Mars once had running water. It's bone dry today. Something bad happened there as well.",
                is_header=False
            )
        ]
    )

MOCK_SUMMARIES  : ArticleSummary = [
        ArticleSummary(
            id=i,
            title=f"This is a mock Post! {i}",
            date_created="January 10, 2026",
            author="_Kühaku_",
            topics=["Mock topic", "Free", "Information Theory"],
            article_img_link="https://dummyimage.com/900x400/ced4da/6c757d.jpg"
        ) for i in range(1, 24) ]

def get_summaries(page_start: int, number_of_articles: int) -> List[ArticleSummary]:
    """
    Simulates: SELECT * FROM articles LIMIT number_of_articles OFFSET page_start
    """
    return MOCK_SUMMARIES[page_start : page_start + number_of_articles]

def get_total_count():
    return len(MOCK_SUMMARIES)