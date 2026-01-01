"""Organize files by date strategy."""

from pathlib import Path
from datetime import datetime
from .base import OrganizationStrategy
from ..utils.formatter import print_separator


class OrganizeByDate(OrganizationStrategy):
    """Strategy to organize files by their modification date."""

    def organize(self, directory, dry_run=False):
        """
        Organize files into YYYY/MM folders by modification date.

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

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by date in: {directory}")
        print_separator()

        # Get the undo log file path to skip it during organization
        undo_log_path = Path(self.undo_manager.log_file) if self.undo_manager else None

        for item in directory.iterdir():
            if item.is_file():
                # Skip the undo log file itself
                if undo_log_path and item.resolve() == undo_log_path.resolve():
                    continue
                mod_time = datetime.fromtimestamp(item.stat().st_mtime)
                year_folder = directory / str(mod_time.year)
                month_folder = year_folder / f"{mod_time.month:02d}-{mod_time.strftime('%B')}"
                target_file = month_folder / item.name

                self.move_file(item, target_file, dry_run)
                print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} → {mod_time.year}/{mod_time.month:02d}/")

        if not dry_run and self.undo_manager:
            self.undo_manager.save()

        print(f"\n✓ Processed {self.files_processed} files")
        return self.files_processed
