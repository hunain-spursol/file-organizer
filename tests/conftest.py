"""Pytest fixtures and configuration for test suite."""
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """Create a set of sample files for testing."""
    files = {
        'document.pdf': b'PDF content here',
        'image.jpg': b'\xff\xd8\xff\xe0' + b'JPEG data' * 100,
        'video.mp4': b'MP4 video content' * 1000,
        'script.py': b'print("Hello, World!")',
        'data.json': b'{"key": "value"}',
        'archive.zip': b'PK\x03\x04' + b'ZIP data' * 50,
        'no_extension': b'File without extension',
        'empty.txt': b'',
        '.hidden': b'Hidden file content',
        'multi.tar.gz': b'Compressed archive',
    }

    created_files = []
    for filename, content in files.items():
        file_path = temp_dir / filename
        file_path.write_bytes(content)
        created_files.append(file_path)

    return created_files


@pytest.fixture
def sample_files_with_dates(temp_dir):
    """Create files with specific modification dates."""
    now = datetime.now()
    files_with_dates = {
        'old_file.txt': now - timedelta(days=400),
        'last_year.doc': now - timedelta(days=200),
        'last_month.pdf': now - timedelta(days=35),
        'this_month.jpg': now - timedelta(days=10),
        'today.py': now,
        'future.txt': now + timedelta(days=5),
    }

    created_files = []
    for filename, mod_time in files_with_dates.items():
        file_path = temp_dir / filename
        file_path.write_text(f'Content of {filename}')

        # Set modification time
        timestamp = mod_time.timestamp()
        os.utime(file_path, (timestamp, timestamp))
        created_files.append((file_path, mod_time))

    return created_files


@pytest.fixture
def sample_files_by_size(temp_dir):
    """Create files of different sizes."""
    size_files = {
        'tiny.txt': 100,           # 100 bytes
        'small.dat': 50 * 1024,    # 50 KB
        'medium.bin': 5 * 1024 * 1024,  # 5 MB
        'large.iso': 500 * 1024 * 1024,  # 500 MB (simulated)
    }

    created_files = []
    for filename, size in size_files.items():
        file_path = temp_dir / filename
        # For very large files, we'll create sparse files or just track the size
        if size > 10 * 1024 * 1024:  # > 10 MB
            # Write a smaller file for testing purposes
            file_path.write_bytes(b'X' * (1024 * 1024))  # 1 MB placeholder
        else:
            file_path.write_bytes(b'X' * size)
        created_files.append((file_path, size))

    return created_files


@pytest.fixture
def duplicate_files(temp_dir):
    """Create duplicate files with same content but different names."""
    content1 = b'This is duplicate content A' * 100
    content2 = b'This is duplicate content B' * 100
    content3 = b'Unique content'

    files = {
        'dup1_a.txt': content1,
        'dup1_b.txt': content1,
        'dup1_c.txt': content1,
        'dup2_a.dat': content2,
        'dup2_b.dat': content2,
        'unique.txt': content3,
    }

    created_files = []
    for filename, content in files.items():
        file_path = temp_dir / filename
        file_path.write_bytes(content)
        created_files.append(file_path)

    return created_files


@pytest.fixture
def nested_directory(temp_dir):
    """Create a nested directory structure."""
    structure = {
        'folder1': ['file1.txt', 'file2.jpg'],
        'folder2': ['file3.pdf', 'file4.py'],
        'folder1/subfolder': ['nested.doc'],
    }

    created_structure = {}
    for folder, files in structure.items():
        folder_path = temp_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        created_structure[folder] = []

        for filename in files:
            file_path = folder_path / filename
            file_path.write_text(f'Content of {filename}')
            created_structure[folder].append(file_path)

    return created_structure


@pytest.fixture
def mock_file_with_metadata(temp_dir):
    """Create a file with specific metadata for testing."""
    file_path = temp_dir / 'metadata_test.txt'
    content = b'Test content for metadata'
    file_path.write_bytes(content)

    # Set specific times
    now = datetime.now()
    timestamp = now.timestamp()
    os.utime(file_path, (timestamp, timestamp))

    return {
        'path': file_path,
        'size': len(content),
        'modified': now,
        'content': content,
    }


@pytest.fixture
def empty_directory(temp_dir):
    """Create an empty directory for testing."""
    empty_path = temp_dir / 'empty_folder'
    empty_path.mkdir()
    return empty_path


@pytest.fixture
def special_characters_files(temp_dir):
    """Create files with special characters in names."""
    special_names = [
        'file with spaces.txt',
        'file_with_underscores.txt',
        'file-with-dashes.txt',
        'file.multiple.dots.txt',
        'UPPERCASE.TXT',
        'MixedCase.TxT',
    ]

    created_files = []
    for filename in special_names:
        file_path = temp_dir / filename
        file_path.write_text(f'Content of {filename}')
        created_files.append(file_path)

    return created_files


@pytest.fixture
def large_directory(temp_dir):
    """Create a directory with many files for performance testing."""
    files = []
    for i in range(100):
        file_path = temp_dir / f'file_{i:03d}.txt'
        file_path.write_text(f'Content {i}')
        files.append(file_path)

    return files
