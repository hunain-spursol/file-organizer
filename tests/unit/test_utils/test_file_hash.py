"""Tests for file hashing utilities."""
import pytest
import hashlib
from pathlib import Path
from src.file_organizer.utils.file_hash import get_file_hash


class TestGetFileHash:
    """Test suite for get_file_hash function."""

    def test_hash_small_file(self, temp_dir):
        """Test hashing a small file."""
        test_file = temp_dir / 'test.txt'
        content = b'Hello, World!'
        test_file.write_bytes(content)

        expected_hash = hashlib.md5(content).hexdigest()
        result = get_file_hash(test_file)

        assert result == expected_hash

    def test_hash_empty_file(self, temp_dir):
        """Test hashing an empty file."""
        test_file = temp_dir / 'empty.txt'
        test_file.write_bytes(b'')

        expected_hash = hashlib.md5(b'').hexdigest()
        result = get_file_hash(test_file)

        assert result == expected_hash

    def test_hash_large_file(self, temp_dir):
        """Test hashing a large file (tests chunked reading)."""
        test_file = temp_dir / 'large.bin'
        # Create a file larger than typical chunk size
        content = b'X' * (10 * 1024 * 1024)  # 10 MB
        test_file.write_bytes(content)

        expected_hash = hashlib.md5(content).hexdigest()
        result = get_file_hash(test_file)

        assert result == expected_hash

    def test_hash_binary_file(self, temp_dir):
        """Test hashing a binary file."""
        test_file = temp_dir / 'binary.dat'
        content = bytes(range(256))  # All possible byte values
        test_file.write_bytes(content)

        expected_hash = hashlib.md5(content).hexdigest()
        result = get_file_hash(test_file)

        assert result == expected_hash

    def test_hash_with_different_algorithms(self, temp_dir):
        """Test hashing with different algorithms."""
        test_file = temp_dir / 'test.txt'
        content = b'Test content for hashing'
        test_file.write_bytes(content)

        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        for algo in algorithms:
            expected = hashlib.new(algo, content).hexdigest()
            result = get_file_hash(test_file, algorithm=algo)
            assert result == expected, f"Failed for algorithm: {algo}"

    def test_same_content_same_hash(self, temp_dir):
        """Test that files with same content produce same hash."""
        content = b'Duplicate content'

        file1 = temp_dir / 'file1.txt'
        file2 = temp_dir / 'file2.txt'

        file1.write_bytes(content)
        file2.write_bytes(content)

        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)

        assert hash1 == hash2

    def test_different_content_different_hash(self, temp_dir):
        """Test that files with different content produce different hashes."""
        file1 = temp_dir / 'file1.txt'
        file2 = temp_dir / 'file2.txt'

        file1.write_bytes(b'Content A')
        file2.write_bytes(b'Content B')

        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)

        assert hash1 != hash2

    def test_hash_nonexistent_file(self, temp_dir):
        """Test hashing a file that doesn't exist."""
        nonexistent = temp_dir / 'nonexistent.txt'
        result = get_file_hash(nonexistent)

        assert result is None

    def test_hash_with_unicode_filename(self, temp_dir):
        """Test hashing a file with unicode characters in name."""
        test_file = temp_dir / 'tëst_fïlé.txt'
        content = b'Unicode filename test'
        test_file.write_bytes(content)

        expected_hash = hashlib.md5(content).hexdigest()
        result = get_file_hash(test_file)

        assert result == expected_hash

    def test_hash_deterministic(self, temp_dir):
        """Test that hashing is deterministic (same hash on multiple calls)."""
        test_file = temp_dir / 'test.txt'
        test_file.write_bytes(b'Deterministic test')

        hash1 = get_file_hash(test_file)
        hash2 = get_file_hash(test_file)
        hash3 = get_file_hash(test_file)

        assert hash1 == hash2 == hash3

    def test_hash_sensitive_to_changes(self, temp_dir):
        """Test that hash changes when file content changes."""
        test_file = temp_dir / 'test.txt'
        test_file.write_bytes(b'Original content')

        hash1 = get_file_hash(test_file)

        # Modify file
        test_file.write_bytes(b'Modified content')

        hash2 = get_file_hash(test_file)

        assert hash1 != hash2

    def test_hash_with_special_characters(self, temp_dir):
        """Test hashing file with special characters in content."""
        test_file = temp_dir / 'special.txt'
        content = b'\x00\x01\x02\xff\xfe\xfd'  # Special bytes
        test_file.write_bytes(content)

        expected_hash = hashlib.md5(content).hexdigest()
        result = get_file_hash(test_file)

        assert result == expected_hash

    def test_invalid_algorithm(self, temp_dir):
        """Test with invalid hash algorithm."""
        test_file = temp_dir / 'test.txt'
        test_file.write_bytes(b'Test')

        with pytest.raises(ValueError):
            get_file_hash(test_file, algorithm='invalid_algo')
