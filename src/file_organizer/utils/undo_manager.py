"""Undo operation management."""

import json
from datetime import datetime
from pathlib import Path
from ..config.settings import UNDO_LOG_FILE


class UndoManager:
    """Manages undo operations for file movements."""

    def __init__(self, log_file=None):
        self.log_file = log_file or UNDO_LOG_FILE
        self.operations = []

    def log_operation(self, operation_type, source, destination):
        """
        Log an operation for potential undo.

        Args:
            operation_type: Type of operation ('move', 'delete', etc.)
            source: Source path
            destination: Destination path
        """
        self.operations.append({
            'type': operation_type,
            'source': str(source),
            'destination': str(destination),
            'timestamp': datetime.now().isoformat()
        })

    def save(self):
        """Save undo log to file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.operations, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save undo log: {e}")

    def load(self):
        """
        Load undo log from file.

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    self.operations = json.load(f)
                return True
            except Exception:
                return False
        return False

    def undo_all(self):
        """
        Undo all logged operations.

        Returns:
            tuple: (undone_count, error_count)
        """
        if not self.load() or not self.operations:
            print("\n❌ No operations to undo")
            return 0, 0

        print(f"\n🔄 Found {len(self.operations)} operations in last session")
        print(f"Last operation: {self.operations[-1]['timestamp']}")

        if input("\nUndo all operations from last session? (y/n): ").lower() != 'y':
            return 0, 0

        from .formatter import print_separator
        print()
        print_separator()

        undone = 0
        errors = 0

        for op in reversed(self.operations):
            try:
                source = Path(op['source'])
                dest = Path(op['destination'])

                if dest.exists():
                    dest.rename(source)
                    print(f"✓ Restored: {dest.name} → {source.parent}/")
                    undone += 1
                else:
                    print(f"⚠ File not found: {dest.name}")
                    errors += 1
            except Exception as e:
                print(f"✗ Error undoing {dest.name}: {e}")
                errors += 1

        print_separator()
        print(f"\n✓ Undone: {undone} operations")
        if errors:
            print(f"⚠ Errors: {errors}")

        self.clear()
        return undone, errors

    def clear(self):
        """Clear operations and save empty log."""
        self.operations = []
        self.save()
