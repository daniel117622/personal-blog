import duckdb
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# --- Dataclasses (Re-imported here to ensure script is standalone-ish) ---
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
class Comment:
    author_name: str
    text       : str
    avatar_url : str
    replies    : List['Comment'] = field(default_factory=list)
      # Note: We don't map ID/ParentID back to the dataclass as the UI doesn't use them yet

@dataclass
class CommentThread:
    comments: List[Comment]

class BlogRepository:
    def __init__(self, db_path=':memory:'):
        self.con = duckdb.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Idempotent schema initialization"""
        self.con.execute("CREATE SEQUENCE IF NOT EXISTS seq_article_id START 1;")
        self.con.execute("CREATE SEQUENCE IF NOT EXISTS seq_comment_id START 1;")
        
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_article_id'),
                title VARCHAR,
                date_created VARCHAR,
                author VARCHAR,
                topics VARCHAR[],
                article_img_link VARCHAR,
                content_blocks STRUCT(text VARCHAR, is_header BOOLEAN)[]
            );
        """)
        
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_comment_id'),
                article_id INTEGER,
                parent_id INTEGER,
                author_name VARCHAR,
                text VARCHAR,
                avatar_url VARCHAR,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            );
        """)

    def get_article(self, article_id: int) -> Optional[Article]:
        # DuckDB returns STRUCTs as Python dicts
        row = self.con.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
        
        if not row:
            return None
            
        # Unpack row (Order matches table definition)
        # id, title, date, author, topics, img, blocks
        c_blocks = [ContentBlock(text=b['text'], is_header=b['is_header']) for b in row[6]]
        
        return Article(
            id=row[0],
            title=row[1],
            date_created = row[2],
            author       = row[3],
            topics       = row[4],
            article_img_link=row[5],
            content_blocks=c_blocks
        )

    def get_comment_thread(self, article_id: int) -> CommentThread:
        rows = self.con.execute("""
            SELECT id, parent_id, author_name, text, avatar_url 
            FROM comments 
            WHERE article_id = ?
            ORDER BY id ASC
        """, (article_id,)).fetchall()

        # Reconstruct Tree
        comment_map = {} # id -> Comment object
        root_comments = []

        # Pass 1: Create all Comment objects
        # We need a temporary structure to hold the objects before assigning them to parents
        # because the Dataclass 'Comment' doesn't store its own ID.
        temp_storage = {} # db_id -> Comment Object

        for r in rows:
            cid, pid, author, text, avatar = r
            c = Comment(author_name=author, text=text, avatar_url=avatar)
            temp_storage[cid] = c
            
            if pid is None:
                root_comments.append(c)
            else:
                # Assuming parent always comes before child (ORDER BY id ASC usually ensures this for chronologically added comments)
                # But to be safe, we should check if parent exists in our map.
                if pid in temp_storage:
                    temp_storage[pid].replies.append(c)
                else:
                    # If parent not found (orphaned), treat as root for safety
                    root_comments.append(c)

        return CommentThread(comments=root_comments)

if __name__ == "__main__":
    from data_access.db_print_utils import pretty_describe_table, pretty_foreign_key

    repo = BlogRepository("duck.db")
    con = repo.con

    # -----------------
    # QUERY PHASE
    # -----------------

    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

    articles_schema = con.execute("DESCRIBE articles").fetchall()
    comments_schema = con.execute("DESCRIBE comments").fetchall()

    fks = con.execute("""
        SELECT
            constraint_name,
            table_name,
            constraint_type,
            constraint_column_indexes
        FROM duckdb_constraints()
        WHERE constraint_type = 'FOREIGN KEY'
    """).fetchall()

    comment_columns = [
        c[1] for c in con.execute("PRAGMA table_info('comments')").fetchall()
    ]

    sequences = con.execute("""
        SELECT sequence_name, start_value, increment_by
        FROM duckdb_sequences()
    """).fetchall()

    article_count = con.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    comment_count = con.execute("SELECT COUNT(*) FROM comments").fetchone()[0]

    type_rows = con.execute("""
        SELECT 
            typeof(topics) AS topics_type,
            typeof(content_blocks) AS content_blocks_type
        FROM articles
        LIMIT 1
    """).fetchall()

    # -----------------
    # PRINT PHASE
    # -----------------

    print("\n--- TABLES ---")
    print(tables)

    print("\n--- ARTICLES TABLE SCHEMA ---")
    for line in pretty_describe_table(articles_schema):
        print(line)

    print("\n--- COMMENTS TABLE SCHEMA ---")
    for line in pretty_describe_table(comments_schema):
        print(line)

    print("\n--- FOREIGN KEY CONSTRAINTS ---")
    if not fks:
        print("None")
    else:
        for fk in fks:
            print(pretty_foreign_key(fk, comment_columns))

    print("\n--- SEQUENCES ---")
    for seq in sequences:
        print(f"{seq[0]} | start={seq[1]} | increment={seq[2]}")

    print("\n--- EMPTY STATE CHECKS ---")
    print(f"Articles: {article_count}")
    print(f"Comments: {comment_count}")

    print("\n--- TYPE VALIDATION ---")
    print(type_rows if type_rows else "No rows to infer types (table empty)")

    print("\n--- SCHEMA VALIDATION COMPLETE ---")