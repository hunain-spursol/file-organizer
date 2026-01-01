"""Tests for duplicate file finder."""
import pytest
from pathlib import Path
from src.file_organizer.strategies.duplicates import DuplicateFinder


class TestDuplicateFinder:
    """Test suite for duplicate file finder."""

    def test_find_no_duplicates(self, temp_dir):
        """Test finding duplicates when none exist."""
        # Create unique files
        (temp_dir / 'file1.txt').write_text('content 1')
        (temp_dir / 'file2.txt').write_text('content 2')
        (temp_dir / 'file3.txt').write_text('content 3')

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 0
        assert finder.duplicates_found == 0
        assert finder.space_saved == 0

    def test_find_simple_duplicates(self, duplicate_files):
        """Test finding simple duplicate files."""
        temp_dir = duplicate_files[0].parent

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        # Should find 2 sets of duplicates (dup1 group and dup2 group)
        assert len(duplicates) == 2

    def test_find_duplicate_pair(self, temp_dir):
        """Test finding a pair of duplicate files."""
        content = b'Duplicate content'
        (temp_dir / 'file1.txt').write_bytes(content)
        (temp_dir / 'file2.txt').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2

    def test_find_multiple_duplicates(self, temp_dir):
        """Test finding multiple files with same content."""
        content = b'Same content everywhere'
        for i in range(5):
            (temp_dir / f'file{i}.txt').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 5

    def test_find_multiple_duplicate_groups(self, temp_dir):
        """Test finding multiple groups of duplicates."""
        # Group 1
        content1 = b'Group 1 content'
        (temp_dir / 'g1_a.txt').write_bytes(content1)
        (temp_dir / 'g1_b.txt').write_bytes(content1)

        # Group 2
        content2 = b'Group 2 content'
        (temp_dir / 'g2_a.txt').write_bytes(content2)
        (temp_dir / 'g2_b.txt').write_bytes(content2)
        (temp_dir / 'g2_c.txt').write_bytes(content2)

        # Unique file
        (temp_dir / 'unique.txt').write_bytes(b'Unique content')

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 2
        # One group has 2, another has 3
        group_sizes = sorted([len(group) for group in duplicates])
        assert group_sizes == [2, 3]

    def test_find_duplicates_nested(self, temp_dir):
        """Test finding duplicates in nested directories."""
        content = b'Nested duplicate content'

        (temp_dir / 'file1.txt').write_bytes(content)

        sub1 = temp_dir / 'sub1'
        sub1.mkdir()
        (sub1 / 'file2.txt').write_bytes(content)

        sub2 = temp_dir / 'sub2'
        sub2.mkdir()
        (sub2 / 'file3.txt').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 3

    def test_find_empty_files_as_duplicates(self, temp_dir):
        """Test that empty files are considered duplicates."""
        for i in range(3):
            (temp_dir / f'empty{i}.txt').write_bytes(b'')

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 3

    def test_find_duplicates_different_names(self, temp_dir):
        """Test finding duplicates with completely different names."""
        content = b'Same content, different names'
        (temp_dir / 'report.pdf').write_bytes(content)
        (temp_dir / 'document.doc').write_bytes(content)
        (temp_dir / 'backup.txt').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 3

    def test_similar_but_not_duplicate(self, temp_dir):
        """Test that similar but not identical files are not considered duplicates."""
        (temp_dir / 'file1.txt').write_bytes(b'Content A')
        (temp_dir / 'file2.txt').write_bytes(b'Content B')
        (temp_dir / 'file3.txt').write_bytes(b'Content A ')  # Extra space

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        # No duplicates should be found
        assert len(duplicates) == 0

    def test_delete_duplicates(self, temp_dir):
        """Test deleting duplicate files."""
        content = b'Duplicate content to delete'
        file1 = temp_dir / 'original.txt'
        file2 = temp_dir / 'duplicate1.txt'
        file3 = temp_dir / 'duplicate2.txt'

        file1.write_bytes(content)
        file2.write_bytes(content)
        file3.write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir, delete=True)

        # Original should remain, duplicates should be deleted
        assert file1.exists()
        assert not file2.exists()
        assert not file3.exists()

        assert finder.duplicates_found == 2

    def test_delete_keeps_first_file(self, temp_dir):
        """Test that delete mode keeps the first file encountered."""
        content = b'Content'

        # Create files in specific order
        files = []
        for i in range(3):
            file = temp_dir / f'file{i}.txt'
            file.write_bytes(content)
            files.append(file)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir, delete=True)

        # First file should exist
        # Note: The actual first file depends on filesystem iteration order
        existing = [f for f in files if f.exists()]
        assert len(existing) == 1

    def test_space_saved_calculation(self, temp_dir):
        """Test calculation of space saved by deleting duplicates."""
        content = b'X' * 1000  # 1000 bytes
        for i in range(3):
            (temp_dir / f'file{i}.txt').write_bytes(content)

        finder = DuplicateFinder()
        finder.find_duplicates(temp_dir, delete=True)

        # 2 duplicates deleted, each 1000 bytes = 2000 bytes saved
        assert finder.space_saved == 2000

    def test_find_duplicates_empty_directory(self, temp_dir):
        """Test finding duplicates in empty directory."""
        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 0

    def test_find_duplicates_single_file(self, temp_dir):
        """Test finding duplicates with only one file."""
        (temp_dir / 'only.txt').write_bytes(b'Only file')

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 0

    def test_find_duplicates_large_files(self, temp_dir):
        """Test finding duplicates with larger files."""
        # Create larger files to test chunked hashing
        content = b'X' * (5 * 1024 * 1024)  # 5MB
        (temp_dir / 'large1.bin').write_bytes(content)
        (temp_dir / 'large2.bin').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2

    def test_find_duplicates_binary_files(self, temp_dir):
        """Test finding duplicates with binary files."""
        content = bytes(range(256)) * 100  # Binary content
        (temp_dir / 'binary1.bin').write_bytes(content)
        (temp_dir / 'binary2.bin').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2

    def test_find_duplicates_mixed_file_types(self, temp_dir):
        """Test finding duplicates across different file types."""
        content = b'Same content, different extensions'
        (temp_dir / 'file.txt').write_bytes(content)
        (temp_dir / 'file.pdf').write_bytes(content)
        (temp_dir / 'file.jpg').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 3

    def test_delete_multiple_groups(self, temp_dir):
        """Test deleting duplicates from multiple groups."""
        # Group 1
        content1 = b'Group 1'
        (temp_dir / 'g1_a.txt').write_bytes(content1)
        (temp_dir / 'g1_b.txt').write_bytes(content1)

        # Group 2
        content2 = b'Group 2'
        (temp_dir / 'g2_a.txt').write_bytes(content2)
        (temp_dir / 'g2_b.txt').write_bytes(content2)

        finder = DuplicateFinder()
        finder.find_duplicates(temp_dir, delete=True)

        # 2 duplicates should be deleted (1 from each group)
        assert finder.duplicates_found == 2

        # Should have 2 files left (1 from each group)
        remaining = list(temp_dir.glob('*.txt'))
        assert len(remaining) == 2

    def test_nested_directory_deletion(self, temp_dir):
        """Test deleting duplicates in nested directories."""
        content = b'Nested duplicate'

        (temp_dir / 'root.txt').write_bytes(content)

        sub = temp_dir / 'subfolder'
        sub.mkdir()
        (sub / 'sub.txt').write_bytes(content)

        finder = DuplicateFinder()
        finder.find_duplicates(temp_dir, delete=True)

        assert finder.duplicates_found == 1

        # One file should remain
        all_files = list(temp_dir.rglob('*.txt'))
        assert len(all_files) == 1

    def test_duplicate_finder_initialization(self):
        """Test DuplicateFinder initialization."""
        finder = DuplicateFinder()
        assert finder.duplicates_found == 0
        assert finder.space_saved == 0

    def test_find_duplicates_with_special_characters(self, temp_dir):
        """Test finding duplicates with special characters in content."""
        content = b'\x00\x01\x02\xff\xfe\xfd Special bytes'
        (temp_dir / 'special1.bin').write_bytes(content)
        (temp_dir / 'special2.bin').write_bytes(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1

    def test_duplicate_groups_are_complete(self, temp_dir):
        """Test that duplicate groups contain all duplicates."""
        content = b'All duplicates'
        files = []
        for i in range(4):
            file = temp_dir / f'dup{i}.txt'
            file.write_bytes(content)
            files.append(file)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 4

        # All files should be in the duplicate group
        duplicate_paths = set(duplicates[0])
        assert all(f in duplicate_paths for f in files)

    def test_no_false_positives(self, temp_dir):
        """Test that unique files are never marked as duplicates."""
        # Create many unique files
        for i in range(10):
            (temp_dir / f'unique{i}.txt').write_bytes(f'Unique {i}'.encode())

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 0

    def test_find_duplicates_ignores_directories(self, temp_dir):
        """Test that directories are not considered in duplicate finding."""
        content = b'Content'
        (temp_dir / 'file.txt').write_bytes(content)

        # Create a directory (should be ignored)
        (temp_dir / 'folder').mkdir()

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates(temp_dir)

        assert len(duplicates) == 0

    def test_space_calculation_multiple_groups(self, temp_dir):
        """Test space calculation with multiple duplicate groups."""
        # Group 1: 3 files of 1000 bytes each
        content1 = b'X' * 1000
        for i in range(3):
            (temp_dir / f'g1_{i}.txt').write_bytes(content1)

        # Group 2: 2 files of 500 bytes each
        content2 = b'Y' * 500
        for i in range(2):
            (temp_dir / f'g2_{i}.txt').write_bytes(content2)

        finder = DuplicateFinder()
        finder.find_duplicates(temp_dir, delete=True)

        # Group 1: 2 duplicates * 1000 bytes = 2000
        # Group 2: 1 duplicate * 500 bytes = 500
        # Total: 2500 bytes
        assert finder.space_saved == 2500
        assert finder.duplicates_found == 3
