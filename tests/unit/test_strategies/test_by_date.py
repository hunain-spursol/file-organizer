"""Tests for organize by date strategy."""
import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from src.file_organizer.strategies.by_date import OrganizeByDate
from src.file_organizer.utils.undo_manager import UndoManager


class TestOrganizeByDate:
    """Test suite for organize by date strategy."""

    def test_organize_single_file(self, temp_dir):
        """Test organizing a single file by date."""
        test_file = temp_dir / 'test.txt'
        test_file.write_text('content')

        # Get the modification time
        mod_time = datetime.fromtimestamp(test_file.stat().st_mtime)

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 1

        expected_path = (temp_dir / str(mod_time.year) /
                        f"{mod_time.month:02d}-{mod_time.strftime('%B')}" /
                        'test.txt')
        assert expected_path.exists()

    def test_organize_multiple_files_same_month(self, temp_dir):
        """Test organizing multiple files from the same month."""
        now = datetime.now()

        for i in range(3):
            file = temp_dir / f'file{i}.txt'
            file.write_text(f'content {i}')

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 3

        year_month = temp_dir / str(now.year) / f"{now.month:02d}-{now.strftime('%B')}"
        assert (year_month / 'file0.txt').exists()
        assert (year_month / 'file1.txt').exists()
        assert (year_month / 'file2.txt').exists()

    def test_organize_files_different_months(self, temp_dir):
        """Test organizing files from different months."""
        files_with_dates = [
            ('old.txt', datetime.now() - timedelta(days=100)),
            ('recent.txt', datetime.now() - timedelta(days=10)),
            ('today.txt', datetime.now()),
        ]

        for filename, mod_time in files_with_dates:
            file_path = temp_dir / filename
            file_path.write_text('content')

            # Set modification time
            timestamp = mod_time.timestamp()
            os.utime(file_path, (timestamp, timestamp))

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 3

        # Verify each file is in correct year/month folder
        for filename, mod_time in files_with_dates:
            expected_path = (temp_dir / str(mod_time.year) /
                           f"{mod_time.month:02d}-{mod_time.strftime('%B')}" /
                           filename)
            assert expected_path.exists()

    def test_organize_files_different_years(self, temp_dir):
        """Test organizing files from different years."""
        files_with_dates = [
            ('2020.txt', datetime(2020, 6, 15)),
            ('2021.txt', datetime(2021, 3, 20)),
            ('2022.txt', datetime(2022, 12, 25)),
        ]

        for filename, mod_time in files_with_dates:
            file_path = temp_dir / filename
            file_path.write_text('content')
            timestamp = mod_time.timestamp()
            os.utime(file_path, (timestamp, timestamp))

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 3

        assert (temp_dir / '2020' / '06-June' / '2020.txt').exists()
        assert (temp_dir / '2021' / '03-March' / '2021.txt').exists()
        assert (temp_dir / '2022' / '12-December' / '2022.txt').exists()

    def test_organize_dry_run(self, temp_dir):
        """Test dry run mode doesn't move files."""
        test_file = temp_dir / 'test.txt'
        test_file.write_text('content')

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir, dry_run=True)

        assert result == 1
        # File should still be in original location
        assert test_file.exists()
        # No year folders should be created
        year_folders = [d for d in temp_dir.iterdir() if d.is_dir()]
        assert len(year_folders) == 0

    def test_organize_empty_directory(self, temp_dir):
        """Test organizing an empty directory."""
        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 0

    def test_month_folder_format(self, temp_dir):
        """Test that month folders are formatted correctly."""
        test_file = temp_dir / 'test.txt'
        test_file.write_text('content')

        # Set to a specific date
        specific_date = datetime(2023, 1, 15)
        timestamp = specific_date.timestamp()
        os.utime(test_file, (timestamp, timestamp))

        strategy = OrganizeByDate()
        strategy.organize(temp_dir)

        # Should be '01-January'
        month_folder = temp_dir / '2023' / '01-January'
        assert month_folder.exists()
        assert (month_folder / 'test.txt').exists()

    def test_organize_preserves_content(self, temp_dir):
        """Test that file content is preserved."""
        content = "Important content that must be preserved"
        test_file = temp_dir / 'important.txt'
        test_file.write_text(content)

        mod_time = datetime.fromtimestamp(test_file.stat().st_mtime)

        strategy = OrganizeByDate()
        strategy.organize(temp_dir)

        moved_file = (temp_dir / str(mod_time.year) /
                     f"{mod_time.month:02d}-{mod_time.strftime('%B')}" /
                     'important.txt')
        assert moved_file.read_text() == content

    def test_organize_with_undo_manager(self, temp_dir):
        """Test that operations are logged for undo."""
        log_file = temp_dir / 'undo.json'
        undo_mgr = UndoManager(log_file=log_file)

        test_file = temp_dir / 'test.txt'
        test_file.write_text('content')

        strategy = OrganizeByDate(undo_manager=undo_mgr)
        strategy.organize(temp_dir)

        assert log_file.exists()
        undo_mgr.load()
        assert len(undo_mgr.operations) == 1
        assert undo_mgr.operations[0]['type'] == 'move'

    def test_organize_skips_directories(self, temp_dir):
        """Test that subdirectories are not processed."""
        test_file = temp_dir / 'file.txt'
        test_file.write_text('content')

        subfolder = temp_dir / 'subfolder'
        subfolder.mkdir()
        nested_file = subfolder / 'nested.txt'
        nested_file.write_text('nested content')

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        # Should only process top-level file
        assert result == 1
        # Nested file should remain in place
        assert nested_file.exists()

    def test_organize_various_file_types(self, temp_dir):
        """Test organizing different file types by date."""
        files = ['doc.pdf', 'image.jpg', 'video.mp4', 'code.py']

        for filename in files:
            (temp_dir / filename).write_text('content')

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == len(files)

        # All should be in the same year/month folder
        now = datetime.now()
        year_month = temp_dir / str(now.year) / f"{now.month:02d}-{now.strftime('%B')}"

        for filename in files:
            assert (year_month / filename).exists()

    def test_organize_files_with_special_names(self, temp_dir):
        """Test organizing files with special characters in names."""
        special_files = [
            'file with spaces.txt',
            'file-with-dashes.txt',
            'file_with_underscores.txt',
            'file.multiple.dots.txt',
        ]

        for filename in special_files:
            (temp_dir / filename).write_text('content')

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == len(special_files)

    def test_organize_handles_future_dates(self, temp_dir):
        """Test organizing files with future modification dates."""
        test_file = temp_dir / 'future.txt'
        test_file.write_text('content')

        # Set to future date
        future_date = datetime.now() + timedelta(days=365)
        timestamp = future_date.timestamp()
        os.utime(test_file, (timestamp, timestamp))

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 1

        expected_path = (temp_dir / str(future_date.year) /
                        f"{future_date.month:02d}-{future_date.strftime('%B')}" /
                        'future.txt')
        assert expected_path.exists()

    def test_organize_creates_nested_directories(self, temp_dir):
        """Test that year and month directories are created."""
        test_file = temp_dir / 'test.txt'
        test_file.write_text('content')

        mod_time = datetime.fromtimestamp(test_file.stat().st_mtime)

        strategy = OrganizeByDate()
        strategy.organize(temp_dir)

        year_dir = temp_dir / str(mod_time.year)
        month_dir = year_dir / f"{mod_time.month:02d}-{mod_time.strftime('%B')}"

        assert year_dir.exists()
        assert year_dir.is_dir()
        assert month_dir.exists()
        assert month_dir.is_dir()

    def test_files_processed_counter(self, temp_dir):
        """Test that files_processed counter is accurate."""
        for i in range(5):
            (temp_dir / f'file{i}.txt').write_text('content')

        strategy = OrganizeByDate()
        strategy.organize(temp_dir)

        assert strategy.files_processed == 5

    def test_organize_all_months(self, temp_dir):
        """Test organizing files from all 12 months."""
        year = 2023
        for month in range(1, 13):
            filename = f'month_{month:02d}.txt'
            file_path = temp_dir / filename
            file_path.write_text(f'Month {month}')

            mod_time = datetime(year, month, 15)
            timestamp = mod_time.timestamp()
            os.utime(file_path, (timestamp, timestamp))

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 12

        # Verify each month folder exists
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']

        for month, month_name in enumerate(month_names, 1):
            folder = temp_dir / str(year) / f"{month:02d}-{month_name}"
            assert folder.exists()
            assert (folder / f'month_{month:02d}.txt').exists()

    def test_organize_existing_structure(self, temp_dir):
        """Test organizing when year/month structure already exists."""
        # Pre-create year/month structure
        year_month = temp_dir / '2023' / '06-June'
        year_month.mkdir(parents=True)
        (year_month / 'existing.txt').write_text('existing')

        # Add new file
        new_file = temp_dir / 'new.txt'
        new_file.write_text('new')

        mod_time = datetime(2023, 6, 15)
        timestamp = mod_time.timestamp()
        os.utime(new_file, (timestamp, timestamp))

        strategy = OrganizeByDate()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (year_month / 'new.txt').exists()
        assert (year_month / 'existing.txt').exists()
