"""Organize files by size strategy."""

from pathlib import Path
from .base import OrganizationStrategy
from ..config.file_types import SIZE_CATEGORIES
from ..utils.formatter import print_separator, format_size


class OrganizeBySize(OrganizationStrategy):
    """Strategy to organize files by their size."""

    def organize(self, directory, dry_run=False):
        """
        Organize files into size categories.

        Args:
            directory: Directory to organize
            dry_run: If True, don't actually move files

        Returns:
            int: Number of files processed
        """
        directory = Path(directory)
        self.files_processed = 0

        if not dry_run and self.undo_manager:
            self.undo_manager.clear()

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by size in: {directory}")
        print_separator()

        for item in directory.iterdir():
            if item.is_file():
                size = item.stat().st_size

                # Determine category
                category = None
                for cat_name, (min_size, max_size) in SIZE_CATEGORIES.items():
                    if min_size <= size < max_size:
                        category = cat_name
                        break

                if category:
                    target_dir = directory / category
                    target_file = target_dir / item.name

                    self.move_file(item, target_file, dry_run)
                    print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} ({format_size(size)}) → {category}/")

        if not dry_run and self.undo_manager:
            self.undo_manager.save()

        print(f"\n✓ Processed {self.files_processed} files")
        return self.files_processed
