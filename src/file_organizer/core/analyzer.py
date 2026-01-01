"""Directory analysis functionality."""

from pathlib import Path
from collections import defaultdict
from ..utils.formatter import format_size, print_separator


class DirectoryAnalyzer:
    """Analyze directory contents and provide statistics."""

    def __init__(self, get_category_func):
        """
        Initialize analyzer.

        Args:
            get_category_func: Function to categorize files by extension
        """
        self.get_category = get_category_func

    def analyze(self, directory):
        """
        Analyze directory and show statistics.

        Args:
            directory: Directory to analyze
        """
        directory = Path(directory)
        category_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        total_size = 0
        total_files = 0

        print(f"\n📊 Analyzing: {directory}")
        print_separator()

        for item in directory.rglob('*'):
            if item.is_file():
                size = item.stat().st_size
                category = self.get_category(item.suffix)

                category_stats[category]['count'] += 1
                category_stats[category]['size'] += size
                total_size += size
                total_files += 1

        print(f"\nTotal Files: {total_files}")
        print(f"Total Size: {format_size(total_size)}\n")

        print(f"{'Category':<20} {'Files':<10} {'Size':<15} {'%'}")
        print_separator()

        sorted_categories = sorted(
            category_stats.keys(),
            key=lambda x: category_stats[x]['size'],
            reverse=True
        )

        for category in sorted_categories:
            stats = category_stats[category]
            percentage = (stats['size'] / total_size * 100) if total_size > 0 else 0
            print(
                f"{category:<20} "
                f"{stats['count']:<10} "
                f"{format_size(stats['size']):<15} "
                f"{percentage:>5.1f}%"
            )


def clean_empty_folders(directory, dry_run=False):
    """
    Remove empty folders.

    Args:
        directory: Directory to clean
        dry_run: If True, don't actually delete

    Returns:
        int: Number of folders removed
    """
    directory = Path(directory)
    removed = 0

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Cleaning empty folders in: {directory}")
    print_separator()

    for item in directory.rglob('*'):
        if item.is_dir() and not any(item.iterdir()):
            print(f"{'[WOULD DELETE]' if dry_run else '[DELETED]'} {item.relative_to(directory)}/")
            if not dry_run:
                item.rmdir()
            removed += 1

    print(f"\n✓ {'Would remove' if dry_run else 'Removed'} {removed} empty folders")
    return removed
