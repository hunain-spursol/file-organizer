"""Base class for organization strategies."""

from abc import ABC, abstractmethod
from pathlib import Path


class OrganizationStrategy(ABC):
    """Abstract base class for file organization strategies."""

    def __init__(self, undo_manager=None):
        self.undo_manager = undo_manager
        self.files_processed = 0

    @abstractmethod
    def organize(self, directory, dry_run=False):
        """
        Organize files in the given directory.

        Args:
            directory: Directory to organize
            dry_run: If True, don't actually move files

        Returns:
            int: Number of files processed
        """
        pass

    def move_file(self, source, destination, dry_run=False):
        """
        Move a file and log the operation.

        Args:
            source: Source path
            destination: Destination path
            dry_run: If True, don't actually move

        Returns:
            Path: Final destination path
        """
        import shutil

        if dry_run:
            return destination

        destination.parent.mkdir(parents=True, exist_ok=True)

        # Handle duplicates
        counter = 1
        final_dest = destination
        while final_dest.exists():
            final_dest = destination.parent / f"{destination.stem}_{counter}{destination.suffix}"
            counter += 1

        shutil.move(str(source), str(final_dest))

        if self.undo_manager:
            self.undo_manager.log_operation('move', source, final_dest)

        self.files_processed += 1
        return final_dest
