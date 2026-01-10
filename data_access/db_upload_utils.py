import duckdb
from dataclasses import asdict
from typing import List, Optional

# Import domain models
from models.article import Article, ArticleSummary, ContentBlock
from models.threads import Comment, CommentThread
from data_access.db_bootstrap import BlogRepository

class BlogDAO:
    def __init__(self, connection: duckdb.DuckDBPyConnection):
        self.con = connection

    # ---------------------------------------------------------
    # INSERTS & DELETES
    # ---------------------------------------------------------

    def insert_article(self, article: Article):
        """
        Inserts an Article.
        Note: We convert ContentBlock objects to dicts for DuckDB STRUCT compatibility.
        """
        # Convert list of dataclasses to list of dicts for STRUCT compatibility
        blocks_data = [asdict(b) for b in article.content_blocks]

        self.con.execute("""
            INSERT INTO articles (id, title, date_created, author, topics, article_img_link, content_blocks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            article.id, 
            article.title, 
            article.date_created, 
            article.author, 
            article.topics, 
            article.article_img_link, 
            blocks_data
        ))

    def insert_comment(self, article_id: int, comment: Comment, parent_id: Optional[int] = None):
        """
        Recursively inserts a comment and its replies.
        """
        # 1. Insert current comment
        result = self.con.execute("""
            INSERT INTO comments (article_id, parent_id, author_name, text, avatar_url)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
        """, (
            article_id, 
            parent_id, 
            comment.author_name, 
            comment.text, 
            comment.avatar_url
        )).fetchone()
        
        current_id = result[0]

        # 2. Recursively insert replies
        for reply in comment.replies:
            self.insert_comment(article_id, reply, parent_id=current_id)

    def insert_thread(self, article_id: int, thread: CommentThread):
        """
        Inserts a full thread attached to an article.
        """
        for comment in thread.comments:
            self.insert_comment(article_id, comment, parent_id=None)

    def delete_article(self, article_id: int):
        """
        Deletes an article and its associated comments.
        """
        # Delete comments first due to FK constraint (if enforced, otherwise good practice)
        self.con.execute("DELETE FROM comments WHERE article_id = ?", (article_id,))
        self.con.execute("DELETE FROM articles WHERE id = ?", (article_id,))

    # ---------------------------------------------------------
    # QUERIES
    # ---------------------------------------------------------

    def get_article(self, article_id: int) -> Optional[Article]:
        row = self.con.execute("""
            SELECT id, title, date_created, author, topics, article_img_link, content_blocks 
            FROM articles 
            WHERE id = ?
        """, (article_id,)).fetchone()

        if not row:
            return None

        # DuckDB returns STRUCTs as dicts automatically in Python
        content_blocks = [
            ContentBlock(text=b['text'], is_header=b['is_header']) 
            for b in row[6]
        ]

        return Article(
            id=row[0],
            title=row[1],
            date_created=row[2],
            author=row[3],
            topics=row[4],
            article_img_link=row[5],
            content_blocks=content_blocks
        )

    def get_summaries(self, limit: int, offset: int) -> List[ArticleSummary]:
        rows = self.con.execute("""
            SELECT id, title, date_created, author, topics, article_img_link 
            FROM articles
            ORDER BY id ASC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        return [
            ArticleSummary(
                id=r[0],
                title=r[1],
                date_created=r[2],
                author=r[3],
                topics=r[4],
                article_img_link=r[5]
            ) for r in rows
        ]

    def get_total_article_count(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM articles").fetchone()[0]

    def get_comment_thread(self, article_id: int) -> CommentThread:
        rows = self.con.execute("""
            SELECT id, parent_id, author_name, text, avatar_url 
            FROM comments 
            WHERE article_id = ?
            ORDER BY id ASC
        """, (article_id,)).fetchall()

        # Build the Tree
        temp_map = {} 
        root_comments = []

        # Pass 1: Instantiate all objects
        for r in rows:
            cid, pid, author, text, avatar = r
            c = Comment(author_name=author, text=text, avatar_url=avatar)
            temp_map[cid] = (c, pid)

        # Pass 2: Link parents and children
        for cid, (comment_obj, pid) in temp_map.items():
            if pid is None:
                root_comments.append(comment_obj)
            else:
                if pid in temp_map:
                    parent_obj = temp_map[pid][0]
                    parent_obj.replies.append(comment_obj)
                else:
                    root_comments.append(comment_obj)

        return CommentThread(comments=root_comments)


if __name__ == "__main__":
    # --- TEST BLOCK ---
    print("--- STARTING DAO TESTS ---")
    
    # 1. Setup Connection
    repo = BlogRepository("duck.db")
    dao = BlogDAO(repo.con)

    # 2. Create Dummy Data
    test_id = 9999
    dummy_article = Article(
        id=test_id,
        title="Test Article",
        date_created="2026-01-01",
        author="TestBot",
        topics=["Testing", "DuckDB"],
        article_img_link="https://picsum.photos/seed/picsum/536/354",
        content_blocks=[
            ContentBlock("Hello World", is_header=True),
            ContentBlock("This is a test body.", is_header=False)
        ]
    )

    dummy_thread = CommentThread(comments=[
        Comment("User1", "First!", "img1.jpg", replies=[
            Comment("User2", "Second!", "img2.jpg")
        ])
    ])

    # 3. Insert
    print(f"Inserting Article ID {test_id}...")
    try:
        dao.insert_article(dummy_article)
        dao.insert_thread(test_id, dummy_thread)
        print("Insert successful.")
    except Exception as e:
        print(f"Insert failed (might already exist): {e}")

    # 4. Read Verification
    print("\nReading Article...")
    fetched_article = dao.get_article(test_id)
    if fetched_article:
        print(f"Found: {fetched_article.title} by {fetched_article.author}")
        print(f"Blocks: {len(fetched_article.content_blocks)}")
        print(f"First Block: {fetched_article.content_blocks[0]}")
    else:
        print("Article NOT FOUND!")

    print("\nReading Comments...")
    fetched_thread = dao.get_comment_thread(test_id)
    print(f"Root comments: {len(fetched_thread.comments)}")
    if fetched_thread.comments:
        print(f"First comment: {fetched_thread.comments[0].text}")
        print(f"Replies to first: {len(fetched_thread.comments[0].replies)}")

    # 5. Summaries Test
    print("\nTesting Summaries...")
    sums = dao.get_summaries(limit=5, offset=0)
    print(f"Fetched {len(sums)} summaries.")
