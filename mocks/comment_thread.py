from dataclasses import dataclass, field
from typing import List

from models.threads import CommentThread , Comment


def get_comment_thread(thread_id : str) -> CommentThread:
    return CommentThread(comments=[
        Comment(
            author_name="Head Comment",
            text="If you're going to lead a space frontier, it has to be government; it'll never be private enterprise. Because the space frontier is dangerous, and it's expensive, and it has unquantified risks.",
            avatar_url="https://dummyimage.com/50x50/ced4da/6c757d.jpg",
            replies=[
                Comment(
                    author_name="Commenter Name",
                    text="And under those conditions, you cannot establish a capital-market evaluation of that enterprise. You can't get investors.",
                    avatar_url="https://dummyimage.com/50x50/ced4da/6c757d.jpg"
                ),
                Comment(
                    author_name="Commenter Name",
                    text="When you put money directly to a problem, it makes a good headline.",
                    avatar_url="https://dummyimage.com/50x50/ced4da/6c757d.jpg"
                )
            ]
        ),
        Comment(
            author_name="Commenter Name",
            text="When I look at the universe and all the ways the universe wants to kill us, I find it hard to reconcile that with statements of beneficence.",
            avatar_url="https://dummyimage.com/50x50/ced4da/6c757d.jpg"
        )
    ])