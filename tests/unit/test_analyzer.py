"""Tests for directory analyzer."""
import pytest
from pathlib import Path
from src.file_organizer.core.analyzer import DirectoryAnalyzer, clean_empty_folders


class TestDirectoryAnalyzer:
    """Test suite for DirectoryAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization with category function."""
        def mock_category(ext):
            return 'Test'

        analyzer = DirectoryAnalyzer(mock_category)
        assert analyzer.get_category == mock_category

    def test_analyze_empty_directory(self, temp_dir, capsys):
        """Test analyzing an empty directory."""
        def get_category(ext):
            return 'Other'

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 0' in captured.out
        assert 'Total Size:' in captured.out

    def test_analyze_single_file(self, temp_dir, capsys):
        """Test analyzing a directory with one file."""
        (temp_dir / 'test.txt').write_bytes(b'X' * 100)

        def get_category(ext):
            return 'Documents' if ext == '.txt' else 'Other'

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 1' in captured.out
        assert 'Documents' in captured.out

    def test_analyze_multiple_files(self, temp_dir, capsys):
        """Test analyzing directory with multiple files."""
        (temp_dir / 'doc.pdf').write_bytes(b'X' * 200)
        (temp_dir / 'image.jpg').write_bytes(b'X' * 300)
        (temp_dir / 'code.py').write_bytes(b'X' * 400)

        category_map = {
            '.pdf': 'Documents',
            '.jpg': 'Images',
            '.py': 'Code'
        }

        def get_category(ext):
            return category_map.get(ext, 'Other')

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 3' in captured.out
        assert 'Documents' in captured.out
        assert 'Images' in captured.out
        assert 'Code' in captured.out

    def test_analyze_calculates_sizes(self, temp_dir, capsys):
        """Test that analyzer correctly calculates file sizes."""
        # Create files with specific sizes
        (temp_dir / 'small.txt').write_bytes(b'X' * 100)
        (temp_dir / 'large.txt').write_bytes(b'X' * 1000)

        def get_category(ext):
            return 'Documents'

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        # Total size should be 1100 bytes
        assert '1.07 KB' in captured.out or '1100' in captured.out.replace(',', '')

    def test_analyze_multiple_categories(self, temp_dir, capsys):
        """Test analyzing files of different categories."""
        # Create multiple files per category
        (temp_dir / 'doc1.pdf').write_bytes(b'X' * 100)
        (temp_dir / 'doc2.pdf').write_bytes(b'X' * 200)
        (temp_dir / 'img1.jpg').write_bytes(b'X' * 150)
        (temp_dir / 'img2.jpg').write_bytes(b'X' * 250)

        category_map = {
            '.pdf': 'Documents',
            '.jpg': 'Images'
        }

        def get_category(ext):
            return category_map.get(ext, 'Other')

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 4' in captured.out
        assert 'Documents' in captured.out
        assert 'Images' in captured.out

    def test_analyze_nested_directories(self, temp_dir, capsys):
        """Test analyzing nested directory structure."""
        # Create nested structure
        sub1 = temp_dir / 'subfolder1'
        sub1.mkdir()
        (sub1 / 'file1.txt').write_bytes(b'X' * 100)

        sub2 = temp_dir / 'subfolder2'
        sub2.mkdir()
        (sub2 / 'file2.txt').write_bytes(b'X' * 200)

        (temp_dir / 'root.txt').write_bytes(b'X' * 150)

        def get_category(ext):
            return 'Documents'

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        # Should find all 3 files recursively
        assert 'Total Files: 3' in captured.out

    def test_analyze_percentage_calculation(self, temp_dir, capsys):
        """Test that percentage calculations are correct."""
        # Create files where we can calculate percentages easily
        (temp_dir / 'file1.txt').write_bytes(b'X' * 500)  # 50% of total
        (temp_dir / 'file2.jpg').write_bytes(b'X' * 500)  # 50% of total

        category_map = {
            '.txt': 'Documents',
            '.jpg': 'Images'
        }

        def get_category(ext):
            return category_map.get(ext, 'Other')

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        # Both should show 50%
        assert '50.0%' in captured.out

    def test_analyze_sorts_by_size(self, temp_dir, capsys):
        """Test that categories are sorted by size (largest first)."""
        (temp_dir / 'small.txt').write_bytes(b'X' * 100)
        (temp_dir / 'large.jpg').write_bytes(b'X' * 1000)

        category_map = {
            '.txt': 'Documents',
            '.jpg': 'Images'
        }

        def get_category(ext):
            return category_map.get(ext, 'Other')

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        # Images should appear before Documents since it's larger
        output = captured.out
        images_pos = output.find('Images')
        docs_pos = output.find('Documents')
        assert images_pos < docs_pos

    def test_analyze_ignores_directories(self, temp_dir, capsys):
        """Test that analyzer counts files but not directories."""
        (temp_dir / 'file.txt').write_bytes(b'X' * 100)
        (temp_dir / 'folder').mkdir()

        def get_category(ext):
            return 'Documents'

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        # Should only count the file, not the folder
        assert 'Total Files: 1' in captured.out

    def test_analyze_with_zero_size_files(self, temp_dir, capsys):
        """Test analyzing directory with empty files."""
        (temp_dir / 'empty1.txt').write_bytes(b'')
        (temp_dir / 'empty2.txt').write_bytes(b'')

        def get_category(ext):
            return 'Documents'

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 2' in captured.out
        assert '0.00 B' in captured.out

    def test_analyze_various_file_sizes(self, temp_dir, capsys):
        """Test analyzing files of various sizes."""
        (temp_dir / 'tiny.txt').write_bytes(b'X' * 10)
        (temp_dir / 'small.dat').write_bytes(b'X' * 1024)  # 1KB
        (temp_dir / 'medium.bin').write_bytes(b'X' * (1024 * 1024))  # 1MB

        def get_category(ext):
            categories = {'.txt': 'Text', '.dat': 'Data', '.bin': 'Binary'}
            return categories.get(ext, 'Other')

        analyzer = DirectoryAnalyzer(get_category)
        analyzer.analyze(temp_dir)

        captured = capsys.readouterr()
        assert 'Total Files: 3' in captured.out
        # Should show human-readable sizes
        assert 'B' in captured.out or 'KB' in captured.out or 'MB' in captured.out


class TestCleanEmptyFolders:
    """Test suite for clean_empty_folders function."""

    def test_clean_single_empty_folder(self, temp_dir):
        """Test cleaning a single empty folder."""
        empty = temp_dir / 'empty'
        empty.mkdir()

        result = clean_empty_folders(temp_dir)

        assert result == 1
        assert not empty.exists()

    def test_clean_multiple_empty_folders(self, temp_dir):
        """Test cleaning multiple empty folders."""
        (temp_dir / 'empty1').mkdir()
        (temp_dir / 'empty2').mkdir()
        (temp_dir / 'empty3').mkdir()

        result = clean_empty_folders(temp_dir)

        assert result == 3
        assert not (temp_dir / 'empty1').exists()
        assert not (temp_dir / 'empty2').exists()
        assert not (temp_dir / 'empty3').exists()

    def test_clean_nested_empty_folders(self, temp_dir):
        """Test cleaning nested empty folders."""
        nested = temp_dir / 'parent' / 'child' / 'grandchild'
        nested.mkdir(parents=True)

        result = clean_empty_folders(temp_dir)

        # All three empty folders should be removed
        assert result == 3
        assert not (temp_dir / 'parent').exists()

    def test_clean_dry_run(self, temp_dir):
        """Test dry run mode doesn't delete folders."""
        empty = temp_dir / 'empty'
        empty.mkdir()

        result = clean_empty_folders(temp_dir, dry_run=True)

        assert result == 1
        assert empty.exists()  # Should still exist

    def test_clean_preserves_folders_with_files(self, temp_dir):
        """Test that folders with files are not removed."""
        folder = temp_dir / 'with_file'
        folder.mkdir()
        (folder / 'file.txt').write_text('content')

        result = clean_empty_folders(temp_dir)

        assert result == 0
        assert folder.exists()
        assert (folder / 'file.txt').exists()

    def test_clean_mixed_folders(self, temp_dir):
        """Test cleaning mix of empty and non-empty folders."""
        # Empty folder
        empty = temp_dir / 'empty'
        empty.mkdir()

        # Non-empty folder
        with_file = temp_dir / 'with_file'
        with_file.mkdir()
        (with_file / 'file.txt').write_text('content')

        result = clean_empty_folders(temp_dir)

        assert result == 1
        assert not empty.exists()
        assert with_file.exists()

    def test_clean_no_folders(self, temp_dir):
        """Test cleaning when there are no folders."""
        (temp_dir / 'file.txt').write_text('content')

        result = clean_empty_folders(temp_dir)

        assert result == 0

    def test_clean_empty_directory(self, temp_dir):
        """Test cleaning an empty directory."""
        result = clean_empty_folders(temp_dir)

        assert result == 0

    def test_clean_deeply_nested_empty(self, temp_dir):
        """Test cleaning deeply nested empty structure."""
        deep = temp_dir / 'a' / 'b' / 'c' / 'd' / 'e'
        deep.mkdir(parents=True)

        result = clean_empty_folders(temp_dir)

        assert result == 5  # All 5 levels
        assert not (temp_dir / 'a').exists()

    def test_clean_preserves_nested_with_file(self, temp_dir):
        """Test that nested structure with file is preserved."""
        nested = temp_dir / 'parent' / 'child'
        nested.mkdir(parents=True)
        (nested / 'file.txt').write_text('content')

        result = clean_empty_folders(temp_dir)

        assert result == 0
        assert nested.exists()
        assert (nested / 'file.txt').exists()

    def test_clean_partial_nested_structure(self, temp_dir):
        """Test cleaning partial nested structure (some empty, some not)."""
        # Create structure: parent/child/grandchild
        nested = temp_dir / 'parent' / 'child' / 'grandchild'
        nested.mkdir(parents=True)

        # Add file to child, making grandchild empty
        (temp_dir / 'parent' / 'child' / 'file.txt').write_text('content')

        result = clean_empty_folders(temp_dir)

        # Only grandchild should be removed
        assert result == 1
        assert not nested.exists()
        assert (temp_dir / 'parent' / 'child').exists()

    def test_clean_output_messages(self, temp_dir, capsys):
        """Test that clean_empty_folders produces correct output."""
        empty = temp_dir / 'empty'
        empty.mkdir()

        clean_empty_folders(temp_dir)

        captured = capsys.readouterr()
        assert '[DELETED]' in captured.out
        assert 'empty' in captured.out.lower()

    def test_clean_dry_run_output(self, temp_dir, capsys):
        """Test dry run output messages."""
        empty = temp_dir / 'empty'
        empty.mkdir()

        clean_empty_folders(temp_dir, dry_run=True)

        captured = capsys.readouterr()
        assert '[DRY RUN]' in captured.out
        assert '[WOULD DELETE]' in captured.out

    def test_clean_with_hidden_folders(self, temp_dir):
        """Test cleaning folders with hidden/dot names."""
        hidden = temp_dir / '.hidden'
        hidden.mkdir()

        result = clean_empty_folders(temp_dir)

        assert result == 1
        assert not hidden.exists()

    def test_clean_with_spaces_in_name(self, temp_dir):
        """Test cleaning folders with spaces in names."""
        spaced = temp_dir / 'folder with spaces'
        spaced.mkdir()

        result = clean_empty_folders(temp_dir)

        assert result == 1
        assert not spaced.exists()

    def test_clean_maintains_structure(self, temp_dir):
        """Test that cleaning maintains proper directory structure."""
        # Create: root/sub1(empty)/sub2(file)/sub3(empty)
        sub1 = temp_dir / 'sub1'
        sub1.mkdir()

        sub2 = temp_dir / 'sub2'
        sub2.mkdir()
        (sub2 / 'file.txt').write_text('content')

        sub3 = temp_dir / 'sub3'
        sub3.mkdir()

        result = clean_empty_folders(temp_dir)

        assert result == 2
        assert not sub1.exists()
        assert sub2.exists()
        assert not sub3.exists()
