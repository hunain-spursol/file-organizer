"""Tests for organize by type strategy."""
import pytest
from pathlib import Path
from src.file_organizer.strategies.by_type import OrganizeByType
from src.file_organizer.utils.undo_manager import UndoManager


class TestGetCategory:
    """Test category detection."""

    def test_image_extensions(self):
        """Test image file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.jpg') == 'Images'
        assert strategy.get_category('.png') == 'Images'
        assert strategy.get_category('.gif') == 'Images'
        assert strategy.get_category('.svg') == 'Images'

    def test_video_extensions(self):
        """Test video file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.mp4') == 'Videos'
        assert strategy.get_category('.avi') == 'Videos'
        assert strategy.get_category('.mkv') == 'Videos'

    def test_audio_extensions(self):
        """Test audio file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.mp3') == 'Audio'
        assert strategy.get_category('.wav') == 'Audio'
        assert strategy.get_category('.flac') == 'Audio'

    def test_document_extensions(self):
        """Test document file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.pdf') == 'Documents'
        assert strategy.get_category('.doc') == 'Documents'
        assert strategy.get_category('.docx') == 'Documents'
        assert strategy.get_category('.txt') == 'Documents'

    def test_code_extensions(self):
        """Test code file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.py') == 'Code'
        assert strategy.get_category('.js') == 'Code'
        assert strategy.get_category('.java') == 'Code'
        assert strategy.get_category('.cpp') == 'Code'

    def test_archive_extensions(self):
        """Test archive file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.zip') == 'Archives'
        assert strategy.get_category('.tar') == 'Archives'
        assert strategy.get_category('.gz') == 'Archives'

    def test_config_extensions(self):
        """Test config file categorization."""
        strategy = OrganizeByType()
        assert strategy.get_category('.json') == 'Config'
        assert strategy.get_category('.yml') == 'Config'
        assert strategy.get_category('.xml') == 'Config'

    def test_case_insensitive(self):
        """Test that categorization is case-insensitive."""
        strategy = OrganizeByType()
        assert strategy.get_category('.JPG') == 'Images'
        assert strategy.get_category('.Jpg') == 'Images'
        assert strategy.get_category('.PDF') == 'Documents'
        assert strategy.get_category('.PY') == 'Code'

    def test_unknown_extension(self):
        """Test categorization of unknown extensions."""
        strategy = OrganizeByType()
        assert strategy.get_category('.unknown') == 'Other'
        assert strategy.get_category('.xyz') == 'Other'
        assert strategy.get_category('.fake') == 'Other'

    def test_no_extension(self):
        """Test categorization of files without extension."""
        strategy = OrganizeByType()
        assert strategy.get_category('') == 'Other'

    def test_custom_rules(self):
        """Test custom categorization rules."""
        custom_rules = {
            'MyCategory': ['.custom', '.special']
        }
        strategy = OrganizeByType(custom_rules=custom_rules)

        assert strategy.get_category('.custom') == 'MyCategory'
        assert strategy.get_category('.special') == 'MyCategory'

    def test_custom_rules_override_builtin(self):
        """Test that custom rules take precedence."""
        custom_rules = {
            'MyImages': ['.jpg', '.png']
        }
        strategy = OrganizeByType(custom_rules=custom_rules)

        assert strategy.get_category('.jpg') == 'MyImages'
        assert strategy.get_category('.png') == 'MyImages'

    def test_compound_extension(self):
        """Test handling of compound extensions."""
        strategy = OrganizeByType()
        # The strategy only looks at the final extension
        assert strategy.get_category('.gz') == 'Archives'

    def test_postman_collection(self):
        """Test special handling of postman collection files."""
        strategy = OrganizeByType()
        assert strategy.get_category('.postman_collection.json') == 'Config'


class TestOrganize:
    """Test file organization."""

    def test_organize_basic_files(self, temp_dir):
        """Test basic file organization."""
        # Create test files
        (temp_dir / 'image.jpg').write_text('image')
        (temp_dir / 'document.pdf').write_text('doc')
        (temp_dir / 'script.py').write_text('code')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == 3
        assert (temp_dir / 'Images' / 'image.jpg').exists()
        assert (temp_dir / 'Documents' / 'document.pdf').exists()
        assert (temp_dir / 'Code' / 'script.py').exists()

    def test_organize_dry_run(self, temp_dir):
        """Test dry run mode doesn't move files."""
        (temp_dir / 'image.jpg').write_text('image')
        (temp_dir / 'document.pdf').write_text('doc')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir, dry_run=True)

        assert result == 2
        # Files should NOT be moved
        assert (temp_dir / 'image.jpg').exists()
        assert (temp_dir / 'document.pdf').exists()
        assert not (temp_dir / 'Images').exists()
        assert not (temp_dir / 'Documents').exists()

    def test_organize_empty_directory(self, temp_dir):
        """Test organizing an empty directory."""
        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == 0

    def test_organize_single_file(self, temp_dir):
        """Test organizing a directory with one file."""
        (temp_dir / 'single.txt').write_text('content')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Documents' / 'single.txt').exists()

    def test_organize_multiple_same_category(self, temp_dir):
        """Test organizing multiple files of the same category."""
        (temp_dir / 'image1.jpg').write_text('img1')
        (temp_dir / 'image2.png').write_text('img2')
        (temp_dir / 'image3.gif').write_text('img3')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == 3
        assert (temp_dir / 'Images' / 'image1.jpg').exists()
        assert (temp_dir / 'Images' / 'image2.png').exists()
        assert (temp_dir / 'Images' / 'image3.gif').exists()

    def test_organize_mixed_categories(self, temp_dir):
        """Test organizing files of different categories."""
        files = {
            'photo.jpg': 'Images',
            'video.mp4': 'Videos',
            'song.mp3': 'Audio',
            'doc.pdf': 'Documents',
            'data.csv': 'Spreadsheets',
            'archive.zip': 'Archives',
            'script.py': 'Code',
        }

        for filename in files:
            (temp_dir / filename).write_text('content')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == len(files)
        for filename, category in files.items():
            assert (temp_dir / category / filename).exists()

    def test_organize_unknown_type(self, temp_dir):
        """Test organizing files with unknown extensions."""
        (temp_dir / 'unknown.xyz').write_text('content')
        (temp_dir / 'noext').write_text('content')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == 2
        assert (temp_dir / 'Other' / 'unknown.xyz').exists()
        assert (temp_dir / 'Other' / 'noext').exists()

    def test_organize_creates_directories(self, temp_dir):
        """Test that organize creates category directories as needed."""
        (temp_dir / 'file.jpg').write_text('content')

        strategy = OrganizeByType()
        strategy.organize(temp_dir)

        assert (temp_dir / 'Images').exists()
        assert (temp_dir / 'Images').is_dir()

    def test_organize_with_undo_manager(self, temp_dir):
        """Test that operations are logged for undo."""
        log_file = temp_dir / 'undo.json'
        undo_mgr = UndoManager(log_file=log_file)

        (temp_dir / 'file.txt').write_text('content')

        strategy = OrganizeByType(undo_manager=undo_mgr)
        strategy.organize(temp_dir)

        assert log_file.exists()
        undo_mgr.load()
        assert len(undo_mgr.operations) == 1

    def test_organize_clears_previous_undo_log(self, temp_dir):
        """Test that organize clears previous undo operations."""
        log_file = temp_dir / 'undo.json'
        undo_mgr = UndoManager(log_file=log_file)

        # Log some old operations
        undo_mgr.log_operation('old', '/src/old.txt', '/dst/old.txt')
        undo_mgr.save()

        (temp_dir / 'file.txt').write_text('content')

        strategy = OrganizeByType(undo_manager=undo_mgr)
        strategy.organize(temp_dir)

        undo_mgr2 = UndoManager(log_file=log_file)
        undo_mgr2.load()
        # Should only have the new operation
        assert len(undo_mgr2.operations) == 1
        assert undo_mgr2.operations[0]['type'] == 'move'

    def test_organize_with_special_filenames(self, temp_dir):
        """Test organizing files with special characters in names."""
        special_files = [
            'file with spaces.txt',
            'file_with_underscores.pdf',
            'file-with-dashes.jpg',
            'file.multiple.dots.py',
        ]

        for filename in special_files:
            (temp_dir / filename).write_text('content')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == len(special_files)

    def test_organize_skips_directories(self, temp_dir):
        """Test that organize skips subdirectories."""
        (temp_dir / 'file.txt').write_text('content')
        (temp_dir / 'subfolder').mkdir()
        (temp_dir / 'subfolder' / 'nested.txt').write_text('nested')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        # Should only process the top-level file
        assert result == 1
        assert (temp_dir / 'Documents' / 'file.txt').exists()
        # Nested file should not be moved
        assert (temp_dir / 'subfolder' / 'nested.txt').exists()

    def test_organize_preserves_file_content(self, temp_dir):
        """Test that file content is preserved after moving."""
        content = "Important file content"
        (temp_dir / 'file.txt').write_text(content)

        strategy = OrganizeByType()
        strategy.organize(temp_dir)

        assert (temp_dir / 'Documents' / 'file.txt').read_text() == content

    def test_organize_with_custom_rules(self, temp_dir):
        """Test organizing with custom categorization rules."""
        (temp_dir / 'file.custom').write_text('content')

        custom_rules = {'CustomCategory': ['.custom']}
        strategy = OrganizeByType(custom_rules=custom_rules)
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'CustomCategory' / 'file.custom').exists()

    def test_organize_handles_existing_target_directory(self, temp_dir):
        """Test organizing when target directory already exists."""
        images_dir = temp_dir / 'Images'
        images_dir.mkdir()
        (images_dir / 'existing.png').write_text('existing')

        (temp_dir / 'new.jpg').write_text('new')

        strategy = OrganizeByType()
        result = strategy.organize(temp_dir)

        assert result == 1
        assert (temp_dir / 'Images' / 'new.jpg').exists()
        assert (temp_dir / 'Images' / 'existing.png').exists()

    def test_files_processed_counter(self, temp_dir):
        """Test that files_processed counter is accurate."""
        for i in range(5):
            (temp_dir / f'file{i}.txt').write_text('content')

        strategy = OrganizeByType()
        strategy.organize(temp_dir)

        assert strategy.files_processed == 5
