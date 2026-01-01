"""Organize files by type strategy."""

from pathlib import Path
from .base import OrganizationStrategy
from ..config.file_types import FILE_TYPES
from ..utils.formatter import print_separator


class OrganizeByType(OrganizationStrategy):
    """Strategy to organize files by their type/extension."""

    def __init__(self, undo_manager=None, custom_rules=None):
        super().__init__(undo_manager)
        self.custom_rules = custom_rules or {}

    def get_category(self, extension):
        """
        Get category for file extension.

        Args:
            extension: File extension (e.g., '.jpg')

        Returns:
            str: Category name
        """
        extension = extension.lower()

        # Check custom rules first
        for category, extensions in self.custom_rules.items():
            if extension in extensions:
                return category

        # Handle special compound extensions
        if 'postman_collection' in extension:
            return 'Config'

        # Check built-in file types
        for category, extensions in FILE_TYPES.items():
            if extension in extensions:
                return category

        return 'Other'

    def organize(self, directory, dry_run=False):
        """
        Organize files into folders by type.

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

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by type in: {directory}")
        print_separator()

        # Get the undo log file path to skip it during organization
        undo_log_path = Path(self.undo_manager.log_file) if self.undo_manager else None

        for item in directory.iterdir():
            if item.is_file():
                # Skip the undo log file itself
                if undo_log_path and item.resolve() == undo_log_path.resolve():
                    continue

                category = self.get_category(item.suffix)
                target_dir = directory / category
                target_file = target_dir / item.name

                self.move_file(item, target_file, dry_run)
                print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} → {category}/")

        if not dry_run and self.undo_manager:
            self.undo_manager.save()

        print(f"\n✓ Processed {self.files_processed} files")
        return self.files_processed
