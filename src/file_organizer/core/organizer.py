"""Main FileOrganizer class."""

from collections import defaultdict
from ..utils.undo_manager import UndoManager
from ..strategies.by_type import OrganizeByType
from ..strategies.by_date import OrganizeByDate
from ..strategies.by_size import OrganizeBySize
from ..strategies.duplicates import DuplicateFinder
from .analyzer import DirectoryAnalyzer, clean_empty_folders


class FileOrganizer:
    """Main file organizer controller."""

    def __init__(self):
        self.custom_rules = {}
        self.undo_manager = UndoManager()
        self.stats = {
            'files_moved': 0,
            'duplicates_found': 0,
            'space_saved': 0,
            'categories': defaultdict(int)
        }

    def get_category(self, extension):
        """
        Get category for file extension.

        Args:
            extension: File extension

        Returns:
            str: Category name
        """
        from ..strategies.by_type import OrganizeByType
        strategy = OrganizeByType(custom_rules=self.custom_rules)
        return strategy.get_category(extension)

    def organize_by_type(self, directory, dry_run=False):
        """Organize files by type."""
        strategy = OrganizeByType(self.undo_manager, self.custom_rules)
        return strategy.organize(directory, dry_run)

    def organize_by_date(self, directory, dry_run=False):
        """Organize files by date."""
        strategy = OrganizeByDate(self.undo_manager)
        return strategy.organize(directory, dry_run)

    def organize_by_size(self, directory, dry_run=False):
        """Organize files by size."""
        strategy = OrganizeBySize(self.undo_manager)
        return strategy.organize(directory, dry_run)

    def find_duplicates(self, directory, delete=False):
        """Find and optionally delete duplicate files."""
        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(directory, delete)
        self.stats['duplicates_found'] = finder.duplicates_found
        self.stats['space_saved'] = finder.space_saved
        return duplicates

    def analyze_directory(self, directory):
        """Analyze directory and show statistics."""
        analyzer = DirectoryAnalyzer(self.get_category)
        analyzer.analyze(directory)

    def clean_empty_folders(self, directory, dry_run=False):
        """Remove empty folders."""
        return clean_empty_folders(directory, dry_run)

    def undo_last_operation(self):
        """Undo the last batch of operations."""
        self.undo_manager.undo_all()

    def add_custom_rule(self, category, extensions):
        """
        Add a custom categorization rule.

        Args:
            category: Category name
            extensions: List of file extensions
        """
        self.custom_rules[category] = extensions

    def remove_custom_rule(self, category):
        """
        Remove a custom categorization rule.

        Args:
            category: Category name

        Returns:
            bool: True if removed, False if not found
        """
        if category in self.custom_rules:
            del self.custom_rules[category]
            return True
        return False

    def get_custom_rules(self):
        """Get all custom rules."""
        return self.custom_rules.copy()
