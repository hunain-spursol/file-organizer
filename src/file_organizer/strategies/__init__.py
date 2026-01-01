"""Organization strategies."""

from .base import OrganizationStrategy
from .by_type import OrganizeByType
from .by_date import OrganizeByDate
from .by_size import OrganizeBySize
from .duplicates import DuplicateFinder

__all__ = [
    'OrganizationStrategy',
    'OrganizeByType',
    'OrganizeByDate',
    'OrganizeBySize',
    'DuplicateFinder'
]
