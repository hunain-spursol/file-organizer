"""Configuration module."""

from .file_types import FILE_TYPES, SIZE_CATEGORIES
from .settings import UNDO_LOG_FILE, HASH_CHUNK_SIZE

__all__ = ['FILE_TYPES', 'SIZE_CATEGORIES', 'UNDO_LOG_FILE', 'HASH_CHUNK_SIZE']
