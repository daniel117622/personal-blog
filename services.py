import os
from flask import g
from typing import Union

# Import Sources
import mocks
from data_access.db_bootstrap import BlogRepository
from data_access.db_upload_utils import BlogDAO
from models.article import Article

# --- CONFIGURATION ---
USE_MOCK_DATA = os.environ.get('USE_MOCK_DATA', 'True') == 'True'

class MockService:
    """Adapts the mocks module to the standard interface"""
    def get_article(self, article_id: int):
        # Mocks typically expect strings, but we standardize on int here
        return mocks.fill_article(str(article_id))
    
    def get_comment_thread(self, article_id: int):
        return mocks.get_comment_thread("mock_id")

    def get_summaries(self, limit: int, offset: int):
        # Mocks currently defined as (offset, limit)
        return mocks.get_summaries(offset, limit)

    def get_total_count(self):
        return mocks.get_total_count()
    
    def delete_article(self, article_id: int):
        print(f"[MOCK] Would delete article ID: {article_id}")
        return True
    
class RealService:
    """Manages the DuckDB connection and DAO"""
    def get_dao(self) -> BlogDAO:
        # Check if we are inside a Flask context (g available)
        if g:
            if 'dao' not in g:
                repo = BlogRepository("duck.db")
                g.dao = BlogDAO(repo.con)
            return g.dao
        else:
            # Fallback for testing without Flask (CLI scripts)
            repo = BlogRepository("duck.db")
            return BlogDAO(repo.con)

    def get_article(self, article_id: int):
        return self.get_dao().get_article(article_id)

    def get_comment_thread(self, article_id: int):
        return self.get_dao().get_comment_thread(article_id)

    def get_summaries(self, limit: int, offset: int):
        return self.get_dao().get_summaries(limit, offset)

    def get_total_count(self):
        return self.get_dao().get_total_article_count()
    
    def create_article(self, article: Article):
        self.get_dao().insert_article(article)

    def delete_article(self, article_id: int):
        self.get_dao().delete_article(article_id)
        
def get_service() -> Union[MockService, RealService]:
    if USE_MOCK_DATA:
        return MockService()
    return RealService()


# --- TESTING BLOCK ---
if __name__ == "__main__":
    print(f"--- TESTING SERVICE FACTORY (MODE: {'MOCK' if USE_MOCK_DATA else 'REAL'}) ---")
    
    # 1. Get the active service
    service = get_service()
    
    # 2. Test Fetching a Summary List
    print("\n[Test 1] Fetching Summaries:")
    summaries = service.get_summaries(limit=2, offset=0)
    print(f"Fetched {len(summaries)} items.")
    if len(summaries) > 0:
        print(f"Sample: {summaries[0]}")

    # 3. Test Total Count
    print("\n[Test 2] Total Count:")
    count = service.get_total_count()
    print(f"Total articles: {count}")
    
    # 4. Test Fetching an Article
    # Note: For real DB, ensure ID 9999 (or similar) exists via db_upload_utils.py
    test_id = 1 if USE_MOCK_DATA else 9999
    print(f"\n[Test 3] Fetching Article ID {test_id}:")
    try:
        article = service.get_article(test_id)
        if article:
            print(f"Success: {article}")
        else:
            print("Article not found (normal if DB is empty)")
    except Exception as e:
        print(f"Error fetching article: {e}")