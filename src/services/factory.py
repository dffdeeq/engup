from sqlalchemy.ext.asyncio import AsyncSession

from src.libs.adapter import Adapter
from src.repos.factory import RepoFactory
from src.settings import Settings


class ServiceFactory:
    def __init__(self, repo: RepoFactory, adapter: Adapter, session: AsyncSession, settings: Settings) -> None:
        self.repo = repo
        self.adapter = adapter
        self.session = session
        self.settings = settings
