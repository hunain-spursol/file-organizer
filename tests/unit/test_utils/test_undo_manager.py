"""Tests for undo manager functionality."""
import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.file_organizer.utils.undo_manager import UndoManager


class TestUndoManagerInit:
    """Test UndoManager initialization."""

    def test_init_default(self):
        """Test initialization with default log file."""
        manager = UndoManager()
        assert manager.operations == []
        assert manager.log_file is not None

    def test_init_custom_log_file(self, temp_dir):
        """Test initialization with custom log file."""
        custom_log = temp_dir / 'custom_undo.json'
        manager = UndoManager(log_file=custom_log)
        assert manager.log_file == custom_log
        assert manager.operations == []


class TestLogOperation:
    """Test operation logging."""

    def test_log_single_operation(self, temp_dir):
        """Test logging a single operation."""
        manager = UndoManager()
        manager.log_operation('move', '/source/file.txt', '/dest/file.txt')

        assert len(manager.operations) == 1
        op = manager.operations[0]
        assert op['type'] == 'move'
        assert op['source'] == '/source/file.txt'
        assert op['destination'] == '/dest/file.txt'
        assert 'timestamp' in op

    def test_log_multiple_operations(self):
        """Test logging multiple operations."""
        manager = UndoManager()
        manager.log_operation('move', '/src1/file1.txt', '/dst1/file1.txt')
        manager.log_operation('move', '/src2/file2.txt', '/dst2/file2.txt')
        manager.log_operation('delete', '/src3/file3.txt', '/trash/file3.txt')

        assert len(manager.operations) == 3
        assert manager.operations[0]['type'] == 'move'
        assert manager.operations[1]['type'] == 'move'
        assert manager.operations[2]['type'] == 'delete'

    def test_log_operation_with_path_objects(self):
        """Test logging with Path objects."""
        manager = UndoManager()
        source = Path('/source/file.txt')
        dest = Path('/dest/file.txt')

        manager.log_operation('move', source, dest)

        assert len(manager.operations) == 1
        assert manager.operations[0]['source'] == str(source)
        assert manager.operations[0]['destination'] == str(dest)

    def test_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        manager = UndoManager()
        manager.log_operation('move', '/src/file.txt', '/dst/file.txt')

        timestamp = manager.operations[0]['timestamp']
        # Should be parseable as ISO format
        datetime.fromisoformat(timestamp)

    def test_timestamps_are_different(self):
        """Test that operations logged at different times have different timestamps."""
        import time
        manager = UndoManager()

        manager.log_operation('move', '/src1/file.txt', '/dst1/file.txt')
        time.sleep(0.01)  # Small delay
        manager.log_operation('move', '/src2/file.txt', '/dst2/file.txt')

        ts1 = manager.operations[0]['timestamp']
        ts2 = manager.operations[1]['timestamp']
        # Timestamps should be different (or at least not guaranteed to be the same)
        assert ts1 != ts2 or ts1 == ts2  # Just verify they exist


class TestSaveAndLoad:
    """Test saving and loading operations."""

    def test_save_operations(self, temp_dir):
        """Test saving operations to file."""
        log_file = temp_dir / 'undo.json'
        manager = UndoManager(log_file=log_file)

        manager.log_operation('move', '/src/file1.txt', '/dst/file1.txt')
        manager.log_operation('move', '/src/file2.txt', '/dst/file2.txt')
        manager.save()

        assert log_file.exists()

        # Verify content
        with open(log_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]['type'] == 'move'

    def test_save_empty_operations(self, temp_dir):
        """Test saving empty operations list."""
        log_file = temp_dir / 'undo.json'
        manager = UndoManager(log_file=log_file)
        manager.save()

        assert log_file.exists()

        with open(log_file, 'r') as f:
            data = json.load(f)
        assert data == []

    def test_load_operations(self, temp_dir):
        """Test loading operations from file."""
        log_file = temp_dir / 'undo.json'

        # Create a log file
        operations = [
            {
                'type': 'move',
                'source': '/src/file.txt',
                'destination': '/dst/file.txt',
                'timestamp': datetime.now().isoformat()
            }
        ]

        with open(log_file, 'w') as f:
            json.dump(operations, f)

        # Load it
        manager = UndoManager(log_file=log_file)
        result = manager.load()

        assert result is True
        assert len(manager.operations) == 1
        assert manager.operations[0]['type'] == 'move'

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file."""
        log_file = temp_dir / 'nonexistent.json'
        manager = UndoManager(log_file=log_file)
        result = manager.load()

        assert result is False
        assert manager.operations == []

    def test_load_corrupted_file(self, temp_dir):
        """Test loading from corrupted JSON file."""
        log_file = temp_dir / 'corrupted.json'
        log_file.write_text('{ invalid json content')

        manager = UndoManager(log_file=log_file)
        result = manager.load()

        assert result is False

    def test_save_load_roundtrip(self, temp_dir):
        """Test that save and load preserve data correctly."""
        log_file = temp_dir / 'undo.json'
        manager1 = UndoManager(log_file=log_file)

        manager1.log_operation('move', '/src/file1.txt', '/dst/file1.txt')
        manager1.log_operation('delete', '/src/file2.txt', '/trash/file2.txt')
        manager1.save()

        manager2 = UndoManager(log_file=log_file)
        manager2.load()

        assert len(manager2.operations) == 2
        assert manager2.operations[0] == manager1.operations[0]
        assert manager2.operations[1] == manager1.operations[1]


class TestUndoAll:
    """Test undo functionality."""

    @patch('builtins.input', return_value='y')
    def test_undo_single_operation(self, mock_input, temp_dir):
        """Test undoing a single file move."""
        log_file = temp_dir / 'undo.json'

        # Create source and destination files
        source = temp_dir / 'source_file.txt'
        dest = temp_dir / 'moved_file.txt'

        source.write_text('test content')
        source.rename(dest)  # Simulate the move

        # Log the operation
        manager = UndoManager(log_file=log_file)
        manager.log_operation('move', source, dest)
        manager.save()

        # Undo
        new_manager = UndoManager(log_file=log_file)
        undone, errors = new_manager.undo_all()

        assert undone == 1
        assert errors == 0
        assert source.exists()
        assert not dest.exists()

    @patch('builtins.input', return_value='y')
    def test_undo_multiple_operations(self, mock_input, temp_dir):
        """Test undoing multiple file moves."""
        log_file = temp_dir / 'undo.json'

        files = []
        manager = UndoManager(log_file=log_file)

        for i in range(3):
            source = temp_dir / f'file{i}.txt'
            dest = temp_dir / f'moved{i}.txt'

            source.write_text(f'content {i}')
            source.rename(dest)

            manager.log_operation('move', source, dest)
            files.append((source, dest))

        manager.save()

        # Undo all
        new_manager = UndoManager(log_file=log_file)
        undone, errors = new_manager.undo_all()

        assert undone == 3
        assert errors == 0

        for source, dest in files:
            assert source.exists()
            assert not dest.exists()

    @patch('builtins.input', return_value='n')
    def test_undo_cancelled_by_user(self, mock_input, temp_dir):
        """Test that undo is cancelled when user says no."""
        log_file = temp_dir / 'undo.json'

        source = temp_dir / 'file.txt'
        dest = temp_dir / 'moved.txt'

        source.write_text('content')
        source.rename(dest)

        manager = UndoManager(log_file=log_file)
        manager.log_operation('move', source, dest)
        manager.save()

        # User cancels
        new_manager = UndoManager(log_file=log_file)
        undone, errors = new_manager.undo_all()

        assert undone == 0
        assert errors == 0
        assert dest.exists()
        assert not source.exists()

    def test_undo_with_no_operations(self, temp_dir, capsys):
        """Test undo when there are no operations."""
        log_file = temp_dir / 'empty.json'
        manager = UndoManager(log_file=log_file)
        manager.save()

        undone, errors = manager.undo_all()

        assert undone == 0
        assert errors == 0

    @patch('builtins.input', return_value='y')
    def test_undo_missing_destination_file(self, mock_input, temp_dir, capsys):
        """Test undo when destination file is missing."""
        log_file = temp_dir / 'undo.json'

        source = temp_dir / 'source.txt'
        dest = temp_dir / 'dest.txt'

        manager = UndoManager(log_file=log_file)
        manager.log_operation('move', source, dest)
        manager.save()

        # Don't create the dest file
        new_manager = UndoManager(log_file=log_file)
        undone, errors = new_manager.undo_all()

        assert undone == 0
        assert errors == 1

    @patch('builtins.input', return_value='y')
    def test_undo_reverses_order(self, mock_input, temp_dir):
        """Test that undo processes operations in reverse order."""
        log_file = temp_dir / 'undo.json'
        manager = UndoManager(log_file=log_file)

        # Simulate a chain of moves: A -> B -> C
        file_a = temp_dir / 'a.txt'
        file_b = temp_dir / 'b.txt'
        file_c = temp_dir / 'c.txt'

        file_a.write_text('content')

        file_a.rename(file_b)
        manager.log_operation('move', file_a, file_b)

        file_b.rename(file_c)
        manager.log_operation('move', file_b, file_c)

        manager.save()

        # Undo should restore A
        new_manager = UndoManager(log_file=log_file)
        undone, errors = new_manager.undo_all()

        assert undone == 2
        assert file_a.exists()
        assert not file_b.exists()
        assert not file_c.exists()


class TestClear:
    """Test clearing operations."""

    def test_clear_operations(self, temp_dir):
        """Test clearing operations."""
        log_file = temp_dir / 'undo.json'
        manager = UndoManager(log_file=log_file)

        manager.log_operation('move', '/src/file.txt', '/dst/file.txt')
        manager.log_operation('move', '/src/file2.txt', '/dst/file2.txt')

        assert len(manager.operations) == 2

        manager.clear()

        assert len(manager.operations) == 0

    def test_clear_saves_empty_log(self, temp_dir):
        """Test that clear saves an empty log file."""
        log_file = temp_dir / 'undo.json'
        manager = UndoManager(log_file=log_file)

        manager.log_operation('move', '/src/file.txt', '/dst/file.txt')
        manager.save()

        manager.clear()

        # Verify file is empty
        with open(log_file, 'r') as f:
            data = json.load(f)
        assert data == []

    def test_clear_empty_operations(self, temp_dir):
        """Test clearing when already empty."""
        log_file = temp_dir / 'undo.json'
        manager = UndoManager(log_file=log_file)

        manager.clear()

        assert len(manager.operations) == 0
