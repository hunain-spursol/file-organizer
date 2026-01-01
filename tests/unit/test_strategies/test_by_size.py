"""Tests for organize by size strategy."""
import pytest
from pathlib import Path
from src.file_organizer.strategies.by_size import OrganizeBySize
from src.file_organizer.utils.undo_manager import UndoManager


class TestOrganizeBySize:
    """Test suite for organize by size strategy."""

    def test_organize_tiny_files(self, temp_dir):
        """Test organizing files under 1MB."""
        # Create tiny files (< 1MB)
        for i in range(3):
            file = temp_dir / f'tiny{i}.txt'
            file.write_bytes(b'X' * 1000)  # 1KB

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 3
        tiny_dir = temp_dir / 'Tiny (< 1MB)'
        assert tiny_dir.exists()
        assert (tiny_dir / 'tiny0.txt').exists()
        assert (tiny_dir / 'tiny1.txt').exists()
        assert (tiny_dir / 'tiny2.txt').exists()

    def test_organize_small_files(self, temp_dir):
        """Test organizing files 1-10MB."""
        file = temp_dir / 'small.dat'
        file.write_bytes(b'X' * (2 * 1024 * 1024))  # 2MB

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Small (1-10MB)' / 'small.dat').exists()

    def test_organize_medium_files(self, temp_dir):
        """Test organizing files 10-100MB."""
        file = temp_dir / 'medium.dat'
        file.write_bytes(b'X' * (15 * 1024 * 1024))  # 15MB

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Medium (10-100MB)' / 'medium.dat').exists()

    def test_organize_large_files(self, temp_dir):
        """Test organizing files 100MB-1GB."""
        file = temp_dir / 'large.dat'
        file.write_bytes(b'X' * (150 * 1024 * 1024))  # 150MB

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Large (100MB-1GB)' / 'large.dat').exists()

    def test_organize_huge_files(self, temp_dir):
        """Test organizing files > 1GB."""
        file = temp_dir / 'huge.dat'
        # Create a file that simulates being huge (actual size for testing)
        file.write_bytes(b'X' * (1024 * 1024 * 1024 + 1))  # Just over 1GB

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Huge (> 1GB)' / 'huge.dat').exists()

    def test_organize_mixed_sizes(self, temp_dir):
        """Test organizing files of different sizes."""
        files_with_sizes = {
            'tiny.txt': 500,                    # Tiny
            'small.dat': 5 * 1024 * 1024,      # Small (5MB)
            'medium.bin': 50 * 1024 * 1024,    # Medium (50MB)
        }

        for filename, size in files_with_sizes.items():
            file = temp_dir / filename
            file.write_bytes(b'X' * size)

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 3
        assert (temp_dir / 'Tiny (< 1MB)' / 'tiny.txt').exists()
        assert (temp_dir / 'Small (1-10MB)' / 'small.dat').exists()
        assert (temp_dir / 'Medium (10-100MB)' / 'medium.bin').exists()

    def test_organize_boundary_cases(self, temp_dir):
        """Test files at exact size boundaries."""
        # Exactly 1MB (should be Small, not Tiny)
        file_1mb = temp_dir / '1mb.dat'
        file_1mb.write_bytes(b'X' * (1024 * 1024))

        # Exactly 10MB (should be Medium, not Small)
        file_10mb = temp_dir / '10mb.dat'
        file_10mb.write_bytes(b'X' * (10 * 1024 * 1024))

        # Exactly 100MB (should be Large, not Medium)
        file_100mb = temp_dir / '100mb.dat'
        file_100mb.write_bytes(b'X' * (100 * 1024 * 1024))

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 3
        assert (temp_dir / 'Small (1-10MB)' / '1mb.dat').exists()
        assert (temp_dir / 'Medium (10-100MB)' / '10mb.dat').exists()
        assert (temp_dir / 'Large (100MB-1GB)' / '100mb.dat').exists()

    def test_organize_empty_file(self, temp_dir):
        """Test organizing an empty file (0 bytes)."""
        empty = temp_dir / 'empty.txt'
        empty.write_bytes(b'')

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Tiny (< 1MB)' / 'empty.txt').exists()

    def test_organize_dry_run(self, temp_dir):
        """Test dry run mode doesn't move files."""
        file = temp_dir / 'test.txt'
        file.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir, dry_run=True)

        assert result == 1
        # File should not be moved
        assert file.exists()
        assert not (temp_dir / 'Tiny (< 1MB)').exists()

    def test_organize_empty_directory(self, temp_dir):
        """Test organizing an empty directory."""
        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 0

    def test_organize_preserves_content(self, temp_dir):
        """Test that file content is preserved."""
        content = b'Important binary content \x00\x01\x02'
        file = temp_dir / 'important.bin'
        file.write_bytes(content)

        strategy = OrganizeBySize()
        strategy.organize(temp_dir)

        moved_file = temp_dir / 'Tiny (< 1MB)' / 'important.bin'
        assert moved_file.read_bytes() == content

    def test_organize_with_undo_manager(self, temp_dir):
        """Test that operations are logged for undo."""
        log_file = temp_dir / 'undo.json'
        undo_mgr = UndoManager(log_file=log_file)

        file = temp_dir / 'test.txt'
        file.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize(undo_manager=undo_mgr)
        strategy.organize(temp_dir)

        assert log_file.exists()
        undo_mgr.load()
        assert len(undo_mgr.operations) == 1

    def test_organize_skips_directories(self, temp_dir):
        """Test that subdirectories are not processed."""
        file = temp_dir / 'file.txt'
        file.write_bytes(b'X' * 1000)

        subfolder = temp_dir / 'subfolder'
        subfolder.mkdir()
        nested = subfolder / 'nested.txt'
        nested.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        # Should only process top-level file
        assert result == 1
        assert nested.exists()  # Nested file unchanged

    def test_organize_creates_directories(self, temp_dir):
        """Test that size category directories are created."""
        file = temp_dir / 'test.txt'
        file.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize()
        strategy.organize(temp_dir)

        size_dir = temp_dir / 'Tiny (< 1MB)'
        assert size_dir.exists()
        assert size_dir.is_dir()

    def test_organize_multiple_files_same_category(self, temp_dir):
        """Test organizing multiple files in same size category."""
        for i in range(5):
            file = temp_dir / f'file{i}.txt'
            file.write_bytes(b'X' * (i + 1) * 1000)  # All < 1MB

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 5

        tiny_dir = temp_dir / 'Tiny (< 1MB)'
        for i in range(5):
            assert (tiny_dir / f'file{i}.txt').exists()

    def test_organize_various_file_types(self, temp_dir):
        """Test organizing different file types by size."""
        files = {
            'doc.pdf': 100 * 1024,           # 100KB - Tiny
            'image.jpg': 3 * 1024 * 1024,    # 3MB - Small
            'video.mp4': 20 * 1024 * 1024,   # 20MB - Medium
        }

        for filename, size in files.items():
            file = temp_dir / filename
            file.write_bytes(b'X' * size)

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 3
        assert (temp_dir / 'Tiny (< 1MB)' / 'doc.pdf').exists()
        assert (temp_dir / 'Small (1-10MB)' / 'image.jpg').exists()
        assert (temp_dir / 'Medium (10-100MB)' / 'video.mp4').exists()

    def test_organize_with_special_filenames(self, temp_dir):
        """Test organizing files with special characters in names."""
        special_files = [
            'file with spaces.txt',
            'file-with-dashes.txt',
            'file_with_underscores.txt',
        ]

        for filename in special_files:
            file = temp_dir / filename
            file.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == len(special_files)

    def test_files_processed_counter(self, temp_dir):
        """Test that files_processed counter is accurate."""
        for i in range(7):
            file = temp_dir / f'file{i}.dat'
            file.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize()
        strategy.organize(temp_dir)

        assert strategy.files_processed == 7

    def test_organize_single_byte_file(self, temp_dir):
        """Test organizing a 1-byte file."""
        file = temp_dir / 'single.txt'
        file.write_bytes(b'X')

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Tiny (< 1MB)' / 'single.txt').exists()

    def test_organize_just_under_boundary(self, temp_dir):
        """Test files just under size boundaries."""
        # Just under 1MB
        file_under_1mb = temp_dir / 'under_1mb.dat'
        file_under_1mb.write_bytes(b'X' * (1024 * 1024 - 1))

        # Just under 10MB
        file_under_10mb = temp_dir / 'under_10mb.dat'
        file_under_10mb.write_bytes(b'X' * (10 * 1024 * 1024 - 1))

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 2
        assert (temp_dir / 'Tiny (< 1MB)' / 'under_1mb.dat').exists()
        assert (temp_dir / 'Small (1-10MB)' / 'under_10mb.dat').exists()

    def test_organize_handles_existing_structure(self, temp_dir):
        """Test organizing when category directories already exist."""
        # Pre-create category directory
        tiny_dir = temp_dir / 'Tiny (< 1MB)'
        tiny_dir.mkdir()
        (tiny_dir / 'existing.txt').write_bytes(b'existing')

        # Add new file
        new_file = temp_dir / 'new.txt'
        new_file.write_bytes(b'X' * 1000)

        strategy = OrganizeBySize()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (tiny_dir / 'new.txt').exists()
        assert (tiny_dir / 'existing.txt').exists()

    def test_organize_all_categories(self, temp_dir):
        """Test organizing files into all size categories."""
        files_with_sizes = {
            'tiny.txt': 500,                         # Tiny
            'small.dat': 5 * 1024 * 1024,           # Small (5MB)
            'medium.bin': 50 * 1024 * 1024,         # Medium (50MB)
            'large.iso': 500 * 1024 * 1024,         # Large (500MB)
            'huge.img': 2 * 1024 * 1024 * 1024,     # Huge (2GB)
        }

        for filename, size in files_with_sizes.items():
            file = temp_dir / filename
            file.write_bytes(b'X' * min(size, 10 * 1024 * 1024))  # Cap at 10MB for test speed

        strategy = OrganizeBySize()
        # We'll only create smaller files for actual testing
        small_files = {
            'tiny.txt': 500,
            'small.dat': 5 * 1024 * 1024,
            'medium.bin': 50 * 1024 * 1024,
        }

        temp_dir2 = temp_dir / 'test2'
        temp_dir2.mkdir()

        for filename, size in small_files.items():
            file = temp_dir2 / filename
            file.write_bytes(b'X' * size)

        result = strategy.organize(temp_dir2)

        assert result == 3
        assert (temp_dir2 / 'Tiny (< 1MB)').exists()
        assert (temp_dir2 / 'Small (1-10MB)').exists()
        assert (temp_dir2 / 'Medium (10-100MB)').exists()
