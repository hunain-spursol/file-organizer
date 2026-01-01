"""End-to-end integration tests for file organizer."""
import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch
from src.file_organizer.core.organizer import FileOrganizer


class TestCompleteWorkflows:
    """Test complete workflows from start to finish."""

    def test_organize_and_undo_workflow(self, temp_dir):
        """Test organizing files and then undoing the operation."""
        # Setup: Create test files
        files = {
            'photo.jpg': b'photo data',
            'document.pdf': b'pdf data',
            'script.py': b'python code',
        }

        for filename, content in files.items():
            (temp_dir / filename).write_bytes(content)

        organizer = FileOrganizer()

        # Step 1: Organize by type
        result = organizer.organize_by_type(temp_dir)
        assert result == 3

        # Verify files moved
        assert (temp_dir / 'Images' / 'photo.jpg').exists()
        assert (temp_dir / 'Documents' / 'document.pdf').exists()
        assert (temp_dir / 'Code' / 'script.py').exists()

        # Step 2: Undo
        with patch('builtins.input', return_value='y'):
            organizer.undo_last_operation()

        # Verify files restored
        assert (temp_dir / 'photo.jpg').exists()
        assert (temp_dir / 'document.pdf').exists()
        assert (temp_dir / 'script.py').exists()

    def test_dry_run_then_actual_organize(self, temp_dir):
        """Test dry run followed by actual organization."""
        (temp_dir / 'test.txt').write_text('content')

        organizer = FileOrganizer()

        # Step 1: Dry run
        result1 = organizer.organize_by_type(temp_dir, dry_run=True)
        assert result1 == 1
        # File should still be in original location
        assert (temp_dir / 'test.txt').exists()
        assert not (temp_dir / 'Documents').exists()

        # Step 2: Actual organize
        result2 = organizer.organize_by_type(temp_dir, dry_run=False)
        assert result2 == 1
        # File should now be moved
        assert not (temp_dir / 'test.txt').exists()
        assert (temp_dir / 'Documents' / 'test.txt').exists()

    def test_analyze_organize_clean_workflow(self, temp_dir):
        """Test analyze, organize, and clean workflow."""
        # Create files
        (temp_dir / 'image.jpg').write_bytes(b'X' * 1000)
        (temp_dir / 'doc.pdf').write_bytes(b'X' * 2000)

        organizer = FileOrganizer()

        # Step 1: Analyze
        organizer.analyze_directory(temp_dir)

        # Step 2: Organize
        organizer.organize_by_type(temp_dir)

        # Step 3: Clean empty folders
        # This should create category folders, so no empty folders to clean
        result = organizer.clean_empty_folders(temp_dir)
        assert result == 0  # No empty folders

    def test_find_duplicates_then_organize(self, temp_dir):
        """Test finding duplicates then organizing remaining files."""
        # Create duplicates
        content = b'duplicate content'
        (temp_dir / 'file1.txt').write_bytes(content)
        (temp_dir / 'file2.txt').write_bytes(content)
        (temp_dir / 'unique.jpg').write_bytes(b'unique image')

        organizer = FileOrganizer()

        # Step 1: Find and delete duplicates
        duplicates = organizer.find_duplicates(temp_dir, delete=True)
        assert len(duplicates) == 1
        assert organizer.stats['duplicates_found'] == 1

        # Step 2: Organize remaining files
        result = organizer.organize_by_type(temp_dir)
        # Should have 2 files remaining (1 duplicate deleted)
        assert result == 2

    def test_organize_with_custom_rules_workflow(self, temp_dir):
        """Test complete workflow with custom categorization rules."""
        (temp_dir / 'data.custom').write_bytes(b'custom data')
        (temp_dir / 'image.jpg').write_bytes(b'image data')

        organizer = FileOrganizer()

        # Step 1: Add custom rule
        organizer.add_custom_rule('MyData', ['.custom'])

        # Step 2: Organize
        result = organizer.organize_by_type(temp_dir)
        assert result == 2

        # Verify custom category used
        assert (temp_dir / 'MyData' / 'data.custom').exists()
        assert (temp_dir / 'Images' / 'image.jpg').exists()

        # Step 3: Remove custom rule and verify
        removed = organizer.remove_custom_rule('MyData')
        assert removed is True

        # Verify rule is gone
        rules = organizer.get_custom_rules()
        assert 'MyData' not in rules

    def test_multiple_organization_strategies(self, temp_dir):
        """Test using multiple organization strategies sequentially."""
        # Create files with different dates
        file1 = temp_dir / 'old.txt'
        file1.write_text('old file')

        file2 = temp_dir / 'new.txt'
        file2.write_text('new file')

        # Set different dates
        old_date = datetime.now() - timedelta(days=100)
        timestamp = old_date.timestamp()
        os.utime(file1, (timestamp, timestamp))

        organizer = FileOrganizer()

        # Step 1: Organize by type
        organizer.organize_by_type(temp_dir)

        docs_folder = temp_dir / 'Documents'
        assert (docs_folder / 'old.txt').exists()
        assert (docs_folder / 'new.txt').exists()

        # Step 2: Organize Documents by date
        organizer.organize_by_date(docs_folder)

        # Files should now be in different month folders
        now = datetime.now()
        new_month = docs_folder / str(now.year) / f"{now.month:02d}-{now.strftime('%B')}"
        old_month = docs_folder / str(old_date.year) / f"{old_date.month:02d}-{old_date.strftime('%B')}"

        assert (new_month / 'new.txt').exists()
        assert (old_month / 'old.txt').exists()

    def test_large_directory_organization(self, temp_dir):
        """Test organizing a directory with many files."""
        # Create 100 files of various types
        file_types = ['.txt', '.jpg', '.pdf', '.py', '.mp3']
        for i in range(100):
            ext = file_types[i % len(file_types)]
            (temp_dir / f'file{i}{ext}').write_bytes(b'X' * 100)

        organizer = FileOrganizer()

        # Analyze first
        organizer.analyze_directory(temp_dir)

        # Organize
        result = organizer.organize_by_type(temp_dir)
        assert result == 100

        # Verify categories created
        assert (temp_dir / 'Documents').exists()
        assert (temp_dir / 'Images').exists()
        assert (temp_dir / 'Code').exists()
        assert (temp_dir / 'Audio').exists()

    def test_nested_directory_handling(self, temp_dir):
        """Test handling of nested directory structures."""
        # Create nested structure
        sub1 = temp_dir / 'subfolder1'
        sub1.mkdir()
        (sub1 / 'nested1.txt').write_text('nested 1')

        sub2 = temp_dir / 'subfolder2'
        sub2.mkdir()
        (sub2 / 'nested2.jpg').write_text('nested 2')

        (temp_dir / 'root.pdf').write_text('root file')

        organizer = FileOrganizer()

        # Organize top level only
        result = organizer.organize_by_type(temp_dir)

        # Only root file should be organized
        assert result == 1
        assert (temp_dir / 'Documents' / 'root.pdf').exists()

        # Nested files should remain in place
        assert (sub1 / 'nested1.txt').exists()
        assert (sub2 / 'nested2.jpg').exists()

    def test_organize_by_size_workflow(self, temp_dir):
        """Test complete workflow organizing by size."""
        # Create files of different sizes
        (temp_dir / 'tiny.txt').write_bytes(b'X' * 100)
        (temp_dir / 'small.dat').write_bytes(b'X' * (2 * 1024 * 1024))
        (temp_dir / 'medium.bin').write_bytes(b'X' * (15 * 1024 * 1024))

        organizer = FileOrganizer()

        # Step 1: Analyze
        organizer.analyze_directory(temp_dir)

        # Step 2: Organize by size
        result = organizer.organize_by_size(temp_dir)
        assert result == 3

        # Verify size categories
        assert (temp_dir / 'Tiny (under 1MB)' / 'tiny.txt').exists()
        assert (temp_dir / 'Small (1-10MB)' / 'small.dat').exists()
        assert (temp_dir / 'Medium (10-100MB)' / 'medium.bin').exists()

    def test_organize_preserves_file_content(self, temp_dir):
        """Test that file content is preserved through organization."""
        content = "This is important content that must not be corrupted"
        test_file = temp_dir / 'important.txt'
        test_file.write_text(content)

        organizer = FileOrganizer()

        # Organize by type
        organizer.organize_by_type(temp_dir)

        # Organize by date
        docs_folder = temp_dir / 'Documents'
        organizer.organize_by_date(docs_folder)

        # Find the file in its new location
        moved_files = list((temp_dir / 'Documents').rglob('important.txt'))
        assert len(moved_files) == 1

        # Verify content preserved
        assert moved_files[0].read_text() == content

    def test_error_recovery_workflow(self, temp_dir):
        """Test that the system handles errors gracefully."""
        (temp_dir / 'file.txt').write_text('content')

        organizer = FileOrganizer()

        # Organize successfully
        result1 = organizer.organize_by_type(temp_dir)
        assert result1 == 1

        # Try to organize again (files already moved)
        result2 = organizer.organize_by_type(temp_dir)
        # Should handle gracefully (no files to organize)
        assert result2 == 0

    def test_mixed_file_types_and_duplicates(self, temp_dir):
        """Test workflow with both unique files and duplicates."""
        # Create unique files
        (temp_dir / 'image.jpg').write_bytes(b'unique image')
        (temp_dir / 'doc.pdf').write_bytes(b'unique doc')

        # Create duplicates
        dup_content = b'duplicate'
        (temp_dir / 'dup1.txt').write_bytes(dup_content)
        (temp_dir / 'dup2.txt').write_bytes(dup_content)

        organizer = FileOrganizer()

        # Step 1: Find duplicates
        duplicates = organizer.find_duplicates(temp_dir, delete=True)
        assert len(duplicates) == 1

        # Step 2: Organize remaining files
        result = organizer.organize_by_type(temp_dir)
        assert result == 3  # 2 unique + 1 remaining duplicate

    def test_full_cleanup_workflow(self, temp_dir):
        """Test complete cleanup workflow."""
        # Create files
        (temp_dir / 'file1.txt').write_text('content1')
        (temp_dir / 'file2.jpg').write_text('content2')

        # Create empty folder
        empty = temp_dir / 'empty_folder'
        empty.mkdir()

        organizer = FileOrganizer()

        # Step 1: Organize
        organizer.organize_by_type(temp_dir)

        # Step 2: Clean empty folders
        result = organizer.clean_empty_folders(temp_dir)

        # The manually created empty folder should be removed
        assert not empty.exists()

    def test_organize_with_special_characters(self, temp_dir):
        """Test organizing files with special characters in names."""
        special_files = [
            'file with spaces.txt',
            'file-with-dashes.jpg',
            'file_with_underscores.pdf',
            'file.multiple.dots.py',
        ]

        for filename in special_files:
            (temp_dir / filename).write_bytes(b'content')

        organizer = FileOrganizer()
        result = organizer.organize_by_type(temp_dir)

        assert result == 4

        # Verify all files moved correctly
        assert (temp_dir / 'Documents' / 'file with spaces.txt').exists()
        assert (temp_dir / 'Images' / 'file-with-dashes.jpg').exists()
        assert (temp_dir / 'Documents' / 'file_with_underscores.pdf').exists()
        assert (temp_dir / 'Code' / 'file.multiple.dots.py').exists()

    def test_concurrent_operations_workflow(self, temp_dir):
        """Test that operations work correctly when performed in sequence."""
        # Create diverse set of files
        (temp_dir / 'image.jpg').write_bytes(b'X' * 100)
        (temp_dir / 'doc.pdf').write_bytes(b'X' * 200)
        (temp_dir / 'code.py').write_bytes(b'X' * 150)

        organizer = FileOrganizer()

        # Perform multiple operations
        organizer.analyze_directory(temp_dir)
        result1 = organizer.organize_by_type(temp_dir)
        assert result1 == 3

        # Analyze again
        organizer.analyze_directory(temp_dir)

        # Clean
        organizer.clean_empty_folders(temp_dir)

        # Verify final state
        assert (temp_dir / 'Images' / 'image.jpg').exists()
        assert (temp_dir / 'Documents' / 'doc.pdf').exists()
        assert (temp_dir / 'Code' / 'code.py').exists()

    def test_reorg_after_undo(self, temp_dir):
        """Test reorganizing after undoing an operation."""
        (temp_dir / 'file.txt').write_text('content')

        organizer = FileOrganizer()

        # Organize
        organizer.organize_by_type(temp_dir)
        assert (temp_dir / 'Documents' / 'file.txt').exists()

        # Undo
        with patch('builtins.input', return_value='y'):
            organizer.undo_last_operation()
        assert (temp_dir / 'file.txt').exists()

        # Reorganize using different strategy
        organizer.organize_by_size(temp_dir)
        assert (temp_dir / 'Tiny (under 1MB)' / 'file.txt').exists()

    def test_empty_and_non_empty_directories(self, temp_dir):
        """Test handling mix of empty and non-empty directories."""
        # Create structure
        filled = temp_dir / 'filled'
        filled.mkdir()
        (filled / 'file.txt').write_text('content')

        empty = temp_dir / 'empty'
        empty.mkdir()

        organizer = FileOrganizer()

        # Clean empty folders
        result = organizer.clean_empty_folders(temp_dir)
        assert result == 1
        assert filled.exists()
        assert not empty.exists()

        # Organize files
        organizer.organize_by_type(temp_dir)

    def test_stats_tracking(self, temp_dir):
        """Test that statistics are tracked correctly."""
        # Create duplicates
        dup_content = b'X' * 1000
        (temp_dir / 'dup1.txt').write_bytes(dup_content)
        (temp_dir / 'dup2.txt').write_bytes(dup_content)

        organizer = FileOrganizer()

        # Find and delete duplicates
        organizer.find_duplicates(temp_dir, delete=True)

        # Verify stats updated
        assert organizer.stats['duplicates_found'] == 1
        assert organizer.stats['space_saved'] == 1000

    def test_organize_already_organized_directory(self, temp_dir):
        """Test organizing a directory that's already organized."""
        # Pre-create organized structure
        images = temp_dir / 'Images'
        images.mkdir()
        (images / 'photo.jpg').write_bytes(b'photo')

        docs = temp_dir / 'Documents'
        docs.mkdir()
        (docs / 'doc.pdf').write_bytes(b'doc')

        organizer = FileOrganizer()

        # Try to organize
        result = organizer.organize_by_type(temp_dir)

        # Should handle gracefully (no files in root to organize)
        assert result == 0
