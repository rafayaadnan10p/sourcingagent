# Import all models here so that:
# 1. Alembic's autogenerate sees every table via Base.metadata
# 2. Relationships can resolve forward references at startup
from app.models.user import User
from app.models.search import Search
from app.models.search_result import SearchResult

__all__ = ["User", "Search", "SearchResult"]
