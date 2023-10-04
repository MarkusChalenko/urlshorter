from src.models.models import BlacklistedClient as BlacklistedClientModel
from src.models.models import ShortedURL as ShortedURLModel
from src.models.models import ShortedURLInfo as ShortedURLInfoModel
from src.schemas.blacklist import BlacklistedClientCreate
from src.schemas.shorted_url_info import ShortURLInfoCreate
from src.schemas.shorted_url import ShortedURLCreate, ShortedURLUpdate

from .base import RepositoryDB


class RepositoryShortedURL(
    RepositoryDB[ShortedURLModel, ShortURLInfoCreate, ShortedURLUpdate]
):
    pass


short_url_service = RepositoryShortedURL(ShortedURLModel)


class RepositoryShortedURLInfo(
    RepositoryDB[ShortedURLInfoModel, ShortedURLCreate, None]
):
    pass


url_info_service = RepositoryShortedURLInfo(ShortedURLInfoModel)


class RepositoryBlacklist(
    RepositoryDB[BlacklistedClientModel, BlacklistedClientCreate, None]
):
    pass


blacklist_service = RepositoryBlacklist(BlacklistedClientModel)