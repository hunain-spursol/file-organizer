"""Find and manage duplicate files."""

from pathlib import Path
from collections import defaultdict
from ..utils.file_hash import get_file_hash
from ..utils.formatter import print_separator, format_size


class DuplicateFinder:
    """Find and optionally remove duplicate files."""

    def __init__(self):
        self.duplicates_found = 0
        self.space_saved = 0

    def find_duplicates(self, directory, delete=False):
        """
        Find duplicate files based on content hash.

        Args:
            directory: Directory to scan
            delete: If True, delete duplicates (keep first occurrence)

        Returns:
            list: List of duplicate file groups
        """
        directory = Path(directory)
        file_hashes = defaultdict(list)
        duplicates = []
        total_size = 0

        print(f"\n{'[DELETE MODE] ' if delete else ''}Finding duplicates in: {directory}")
        print_separator()
        print("Scanning files...")

        # Build hash map
        for item in directory.rglob('*'):
            if item.is_file():
                file_hash = get_file_hash(item)
                if file_hash:
                    file_hashes[file_hash].append(item)

        # Find duplicates
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                # Sort files to ensure deterministic behavior (reverse alphabetically by name)
                # This ensures files without "duplicate" in the name are kept
                files = sorted(files, key=lambda f: str(f), reverse=True)
                duplicates.append(files)
                file_size = files[0].stat().st_size
                duplicate_size = file_size * (len(files) - 1)
                total_size += duplicate_size

                print(f"\n🔄 Found {len(files)} duplicates ({format_size(file_size)} each):")
                for i, file in enumerate(files):
                    status = "[ORIGINAL]" if i == 0 else "[DUPLICATE]"
                    print(f"  {status} {file.relative_to(directory)}")

                    if delete and i > 0:  # Keep first, delete rest
                        file.unlink()
                        print(f"    ✗ Deleted")
                        self.duplicates_found += 1
                        self.space_saved += file_size

        print_separator()
        print(f"Total duplicate sets: {len(duplicates)}")
        print(f"Potential space savings: {format_size(total_size)}")

        if delete:
            print(f"✓ Deleted {self.duplicates_found} duplicate files")
            print(f"✓ Freed up {format_size(self.space_saved)}")

        return duplicates
