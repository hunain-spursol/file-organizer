"""File hashing utilities."""

import hashlib
from ..config.settings import HASH_CHUNK_SIZE


def get_file_hash(filepath, algorithm='md5'):
    """
    Calculate hash of a file.

    Args:
        filepath: Path to the file
        algorithm: Hash algorithm to use (md5, sha256, etc.)

    Returns:
        str: Hex digest of the file hash, or None if error
    """
    hash_obj = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None
