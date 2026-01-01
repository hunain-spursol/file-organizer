"""Application settings and configuration."""

from pathlib import Path

# Undo log file location
UNDO_LOG_FILE = Path.home() / '.file_organizer_undo.json'

# Hash algorithm settings
HASH_CHUNK_SIZE = 4096
