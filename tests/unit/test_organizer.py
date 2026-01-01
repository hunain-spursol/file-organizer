"""Tests for FileOrganizer core class."""
import pytest
from pathlib import Path
from src.file_organizer.core.organizer import FileOrganizer


class TestFileOrganizerInit:
    """Test FileOrganizer initialization."""

    def test_initialization(self):
        """Test that FileOrganizer initializes correctly."""
        organizer = FileOrganizer()
        assert organizer.custom_rules == {}
        assert organizer.undo_manager is not None
        assert organizer.stats['files_moved'] == 0
        assert organizer.stats['duplicates_found'] == 0
        assert organizer.stats['space_saved'] == 0


class TestGetCategory:
    """Test file categorization."""

    def test_get_category_basic(self):
        """Test basic category detection."""
        organizer = FileOrganizer()
        assert organizer.get_category('.jpg') == 'Images'
        assert organizer.get_category('.pdf') == 'Documents'
        assert organizer.get_category('.py') == 'Code'

    def test_get_category_case_insensitive(self):
        """Test case-insensitive category detection."""
        organizer = FileOrganizer()
        assert organizer.get_category('.JPG') == 'Images'
        assert organizer.get_category('.Pdf') == 'Documents'

    def test_get_category_unknown(self):
        """Test unknown extension categorization."""
        organizer = FileOrganizer()
        assert organizer.get_category('.xyz') == 'Other'


class TestCustomRules:
    """Test custom categorization rules."""

    def test_add_custom_rule(self):
        """Test adding a custom rule."""
        organizer = FileOrganizer()
        organizer.add_custom_rule('MyCategory', ['.custom', '.special'])

        assert 'MyCategory' in organizer.custom_rules
        assert organizer.custom_rules['MyCategory'] == ['.custom', '.special']

    def test_custom_rule_affects_categorization(self):
        """Test that custom rules affect file categorization."""
        organizer = FileOrganizer()
        organizer.add_custom_rule('MyImages', ['.jpg'])

        # Custom rule should override default
        assert organizer.get_category('.jpg') == 'MyImages'

    def test_add_multiple_custom_rules(self):
        """Test adding multiple custom rules."""
        organizer = FileOrganizer()
        organizer.add_custom_rule('Category1', ['.ext1'])
        organizer.add_custom_rule('Category2', ['.ext2'])

        assert len(organizer.custom_rules) == 2
        assert organizer.get_category('.ext1') == 'Category1'
        assert organizer.get_category('.ext2') == 'Category2'

    def test_remove_custom_rule(self):
        """Test removing a custom rule."""
        organizer = FileOrganizer()
        organizer.add_custom_rule('MyCategory', ['.custom'])

        result = organizer.remove_custom_rule('MyCategory')

        assert result is True
        assert 'MyCategory' not in organizer.custom_rules

    def test_remove_nonexistent_rule(self):
        """Test removing a rule that doesn't exist."""
        organizer = FileOrganizer()
        result = organizer.remove_custom_rule('NonExistent')

        assert result is False

    def test_get_custom_rules(self):
        """Test getting all custom rules."""
        organizer = FileOrganizer()
        organizer.add_custom_rule('Cat1', ['.ext1'])
        organizer.add_custom_rule('Cat2', ['.ext2'])

        rules = organizer.get_custom_rules()

        assert len(rules) == 2
        assert 'Cat1' in rules
        assert 'Cat2' in rules

    def test_get_custom_rules_returns_copy(self):
        """Test that get_custom_rules returns a copy."""
        organizer = FileOrganizer()
        organizer.add_custom_rule('Cat1', ['.ext1'])

        rules = organizer.get_custom_rules()
        rules['Cat2'] = ['.ext2']

        # Original should not be modified
        assert 'Cat2' not in organizer.custom_rules


class TestOrganizeByType:
    """Test organize by type functionality."""

    def test_organize_by_type_basic(self, temp_dir):
        """Test basic file organization by type."""
        (temp_dir / 'image.jpg').write_text('img')
        (temp_dir / 'doc.pdf').write_text('doc')

        organizer = FileOrganizer()
        result = organizer.organize_by_type(temp_dir)

        assert result == 2
        assert (temp_dir / 'Images' / 'image.jpg').exists()
        assert (temp_dir / 'Documents' / 'doc.pdf').exists()

    def test_organize_by_type_dry_run(self, temp_dir):
        """Test dry run mode for organize by type."""
        (temp_dir / 'file.txt').write_text('content')

        organizer = FileOrganizer()
        result = organizer.organize_by_type(temp_dir, dry_run=True)

        assert result == 1
        assert (temp_dir / 'file.txt').exists()
        assert not (temp_dir / 'Documents').exists()

    def test_organize_by_type_with_custom_rules(self, temp_dir):
        """Test organize by type with custom rules."""
        (temp_dir / 'file.custom').write_text('content')

        organizer = FileOrganizer()
        organizer.add_custom_rule('CustomCat', ['.custom'])
        result = organizer.organize_by_type(temp_dir)

        assert result == 1
        assert (temp_dir / 'CustomCat' / 'file.custom').exists()

    def test_organize_by_type_empty_directory(self, temp_dir):
        """Test organizing empty directory by type."""
        organizer = FileOrganizer()
        result = organizer.organize_by_type(temp_dir)

        assert result == 0


class TestOrganizeByDate:
    """Test organize by date functionality."""

    def test_organize_by_date_basic(self, temp_dir):
        """Test basic file organization by date."""
        from datetime import datetime

        (temp_dir / 'file.txt').write_text('content')

        organizer = FileOrganizer()
        result = organizer.organize_by_date(temp_dir)

        assert result == 1

        # Should be organized into year/month structure
        now = datetime.now()
        year_folder = temp_dir / str(now.year)
        assert year_folder.exists()

    def test_organize_by_date_dry_run(self, temp_dir):
        """Test dry run mode for organize by date."""
        (temp_dir / 'file.txt').write_text('content')

        organizer = FileOrganizer()
        result = organizer.organize_by_date(temp_dir, dry_run=True)

        assert result == 1
        assert (temp_dir / 'file.txt').exists()

    def test_organize_by_date_empty_directory(self, temp_dir):
        """Test organizing empty directory by date."""
        organizer = FileOrganizer()
        result = organizer.organize_by_date(temp_dir)

        assert result == 0


class TestOrganizeBySize:
    """Test organize by size functionality."""

    def test_organize_by_size_basic(self, temp_dir):
        """Test basic file organization by size."""
        (temp_dir / 'tiny.txt').write_bytes(b'X' * 100)
        (temp_dir / 'small.dat').write_bytes(b'X' * (2 * 1024 * 1024))

        organizer = FileOrganizer()
        result = organizer.organize_by_size(temp_dir)

        assert result == 2
        assert (temp_dir / 'Tiny (< 1MB)' / 'tiny.txt').exists()
        assert (temp_dir / 'Small (1-10MB)' / 'small.dat').exists()

    def test_organize_by_size_dry_run(self, temp_dir):
        """Test dry run mode for organize by size."""
        (temp_dir / 'file.txt').write_bytes(b'X' * 100)

        organizer = FileOrganizer()
        result = organizer.organize_by_size(temp_dir, dry_run=True)

        assert result == 1
        assert (temp_dir / 'file.txt').exists()

    def test_organize_by_size_empty_directory(self, temp_dir):
        """Test organizing empty directory by size."""
        organizer = FileOrganizer()
        result = organizer.organize_by_size(temp_dir)

        assert result == 0


class TestFindDuplicates:
    """Test duplicate finding functionality."""

    def test_find_duplicates_basic(self, temp_dir):
        """Test finding duplicate files."""
        content = b'Duplicate content'
        (temp_dir / 'file1.txt').write_bytes(content)
        (temp_dir / 'file2.txt').write_bytes(content)

        organizer = FileOrganizer()
        duplicates = organizer.find_duplicates(temp_dir)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2

    def test_find_duplicates_updates_stats(self, temp_dir):
        """Test that finding duplicates updates statistics."""
        content = b'X' * 1000
        (temp_dir / 'file1.txt').write_bytes(content)
        (temp_dir / 'file2.txt').write_bytes(content)

        organizer = FileOrganizer()
        organizer.find_duplicates(temp_dir, delete=True)

        assert organizer.stats['duplicates_found'] == 1
        assert organizer.stats['space_saved'] == 1000

    def test_find_duplicates_no_duplicates(self, temp_dir):
        """Test finding duplicates when none exist."""
        (temp_dir / 'file1.txt').write_bytes(b'Content 1')
        (temp_dir / 'file2.txt').write_bytes(b'Content 2')

        organizer = FileOrganizer()
        duplicates = organizer.find_duplicates(temp_dir)

        assert len(duplicates) == 0
        assert organizer.stats['duplicates_found'] == 0

    def test_find_duplicates_delete_mode(self, temp_dir):
        """Test deleting duplicates."""
        content = b'Duplicate'
        file1 = temp_dir / 'file1.txt'
        file2 = temp_dir / 'file2.txt'

        file1.write_bytes(content)
        file2.write_bytes(content)

        organizer = FileOrganizer()
        organizer.find_duplicates(temp_dir, delete=True)

        # One file should remain
        remaining = list(temp_dir.glob('*.txt'))
        assert len(remaining) == 1


class TestAnalyzeDirectory:
    """Test directory analysis functionality."""

    def test_analyze_directory_basic(self, temp_dir, capsys):
        """Test basic directory analysis."""
        (temp_dir / 'image.jpg').write_bytes(b'X' * 100)
        (temp_dir / 'doc.pdf').write_bytes(b'X' * 200)

        organizer = FileOrganizer()
        organizer.analyze_directory(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 2' in captured.out
        assert 'Images' in captured.out
        assert 'Documents' in captured.out

    def test_analyze_empty_directory(self, temp_dir, capsys):
        """Test analyzing an empty directory."""
        organizer = FileOrganizer()
        organizer.analyze_directory(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 0' in captured.out


class TestCleanEmptyFolders:
    """Test cleaning empty folders functionality."""

    def test_clean_empty_folders_basic(self, temp_dir):
        """Test removing empty folders."""
        empty_folder = temp_dir / 'empty'
        empty_folder.mkdir()

        organizer = FileOrganizer()
        result = organizer.clean_empty_folders(temp_dir)

        assert result == 1
        assert not empty_folder.exists()

    def test_clean_empty_folders_dry_run(self, temp_dir):
        """Test dry run for cleaning empty folders."""
        empty_folder = temp_dir / 'empty'
        empty_folder.mkdir()

        organizer = FileOrganizer()
        result = organizer.clean_empty_folders(temp_dir, dry_run=True)

        assert result == 1
        assert empty_folder.exists()  # Should not be deleted

    def test_clean_empty_folders_nested(self, temp_dir):
        """Test removing nested empty folders."""
        nested = temp_dir / 'parent' / 'child'
        nested.mkdir(parents=True)

        organizer = FileOrganizer()
        result = organizer.clean_empty_folders(temp_dir)

        # Both folders should be removed
        assert result >= 1

    def test_clean_empty_folders_with_files(self, temp_dir):
        """Test that folders with files are not removed."""
        folder = temp_dir / 'with_file'
        folder.mkdir()
        (folder / 'file.txt').write_text('content')

        organizer = FileOrganizer()
        result = organizer.clean_empty_folders(temp_dir)

        assert result == 0
        assert folder.exists()


class TestUndoOperation:
    """Test undo functionality."""

    def test_undo_last_operation(self, temp_dir):
        """Test undoing the last operation."""
        source = temp_dir / 'file.txt'
        source.write_text('content')

        organizer = FileOrganizer()
        organizer.organize_by_type(temp_dir)

        # File should be moved
        moved_file = temp_dir / 'Documents' / 'file.txt'
        assert moved_file.exists()
        assert not source.exists()

        # Mock user input to confirm undo
        from unittest.mock import patch
        with patch('builtins.input', return_value='y'):
            organizer.undo_last_operation()

        # File should be back in original location
        assert source.exists()
        assert not moved_file.exists()


class TestIntegration:
    """Integration tests for FileOrganizer."""

    def test_full_workflow(self, temp_dir):
        """Test a complete workflow with multiple operations."""
        # Create test files
        (temp_dir / 'image.jpg').write_text('img')
        (temp_dir / 'doc.pdf').write_text('doc')
        (temp_dir / 'script.py').write_text('code')

        organizer = FileOrganizer()

        # Analyze first
        organizer.analyze_directory(temp_dir)

        # Organize by type
        result = organizer.organize_by_type(temp_dir)
        assert result == 3

        # Clean empty folders (should be none since files were moved)
        organizer.clean_empty_folders(temp_dir)

        # Verify structure
        assert (temp_dir / 'Images' / 'image.jpg').exists()
        assert (temp_dir / 'Documents' / 'doc.pdf').exists()
        assert (temp_dir / 'Code' / 'script.py').exists()

    def test_multiple_strategies_sequential(self, temp_dir):
        """Test using multiple organization strategies sequentially."""
        (temp_dir / 'file1.txt').write_text('content1')
        (temp_dir / 'file2.txt').write_text('content2')

        organizer = FileOrganizer()

        # First organize by type
        organizer.organize_by_type(temp_dir)

        # Files should be in Documents folder
        docs_folder = temp_dir / 'Documents'
        assert (docs_folder / 'file1.txt').exists()
        assert (docs_folder / 'file2.txt').exists()

        # Then organize Documents folder by date
        from datetime import datetime
        organizer.organize_by_date(docs_folder)

        # Files should now be in year/month structure
        now = datetime.now()
        month_folder = docs_folder / str(now.year) / f"{now.month:02d}-{now.strftime('%B')}"
        assert (month_folder / 'file1.txt').exists()
        assert (month_folder / 'file2.txt').exists()
