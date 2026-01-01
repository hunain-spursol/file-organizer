"""Tests for formatting utilities."""
import pytest
from io import StringIO
import sys
from src.file_organizer.utils.formatter import format_size, print_separator, print_header


class TestFormatSize:
    """Test suite for format_size function."""

    def test_format_bytes(self):
        """Test formatting byte values."""
        assert format_size(0) == "0.00 B"
        assert format_size(1) == "1.00 B"
        assert format_size(100) == "100.00 B"
        assert format_size(1023) == "1023.00 B"

    def test_format_kilobytes(self):
        """Test formatting kilobyte values."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(1536) == "1.50 KB"
        assert format_size(10240) == "10.00 KB"
        assert format_size(1024 * 1023) == "1023.00 KB"

    def test_format_megabytes(self):
        """Test formatting megabyte values."""
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(1024 * 1024 * 5) == "5.00 MB"
        assert format_size(1024 * 1024 * 1.5) == "1.50 MB"

    def test_format_gigabytes(self):
        """Test formatting gigabyte values."""
        assert format_size(1024 ** 3) == "1.00 GB"
        assert format_size(1024 ** 3 * 2.5) == "2.50 GB"
        assert format_size(1024 ** 3 * 100) == "100.00 GB"

    def test_format_terabytes(self):
        """Test formatting terabyte values."""
        assert format_size(1024 ** 4) == "1.00 TB"
        assert format_size(1024 ** 4 * 5) == "5.00 TB"

    def test_format_petabytes(self):
        """Test formatting petabyte values."""
        assert format_size(1024 ** 5) == "1.00 PB"
        assert format_size(1024 ** 5 * 10) == "10.00 PB"

    def test_format_precision(self):
        """Test that formatting maintains 2 decimal places."""
        assert format_size(1536) == "1.50 KB"
        assert format_size(1024 * 1.234) == "1.23 KB"
        assert format_size(1024 * 1.999) == "2.00 KB"

    def test_format_edge_cases(self):
        """Test edge cases."""
        assert format_size(1024 - 1) == "1023.00 B"
        assert format_size(1024) == "1.00 KB"
        assert format_size(1024 + 1) == "1.00 KB"

    def test_format_very_large_numbers(self):
        """Test very large file sizes."""
        huge_size = 1024 ** 6  # Exabyte
        result = format_size(huge_size)
        assert result.endswith("PB")

    def test_format_fractional_bytes(self):
        """Test formatting with fractional byte input."""
        assert format_size(1.5) == "1.50 B"
        assert format_size(100.99) == "100.99 B"

    def test_format_common_file_sizes(self):
        """Test common real-world file sizes."""
        # Small text file
        assert format_size(4096) == "4.00 KB"

        # Large document
        assert format_size(2 * 1024 * 1024) == "2.00 MB"

        # Video file
        assert format_size(500 * 1024 * 1024) == "500.00 MB"

        # ISO image
        assert format_size(4.7 * 1024 ** 3) == "4.70 GB"


class TestPrintSeparator:
    """Test suite for print_separator function."""

    def test_default_separator(self, capsys):
        """Test printing separator with default parameters."""
        print_separator()
        captured = capsys.readouterr()
        assert captured.out == "─" * 70 + "\n"

    def test_custom_character(self, capsys):
        """Test separator with custom character."""
        print_separator(char='=')
        captured = capsys.readouterr()
        assert captured.out == "=" * 70 + "\n"

    def test_custom_length(self, capsys):
        """Test separator with custom length."""
        print_separator(length=50)
        captured = capsys.readouterr()
        assert captured.out == "─" * 50 + "\n"

    def test_custom_character_and_length(self, capsys):
        """Test separator with both custom character and length."""
        print_separator(char='*', length=30)
        captured = capsys.readouterr()
        assert captured.out == "*" * 30 + "\n"

    def test_empty_separator(self, capsys):
        """Test separator with zero length."""
        print_separator(length=0)
        captured = capsys.readouterr()
        assert captured.out == "\n"

    def test_single_character_separator(self, capsys):
        """Test separator with length 1."""
        print_separator(length=1)
        captured = capsys.readouterr()
        assert captured.out == "─\n"

    def test_unicode_separator(self, capsys):
        """Test separator with unicode characters."""
        print_separator(char='━')
        captured = capsys.readouterr()
        assert captured.out == "━" * 70 + "\n"


class TestPrintHeader:
    """Test suite for print_header function."""

    def test_default_header(self, capsys):
        """Test printing header with default character."""
        print_header("Test Header")
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "=" * 70
        assert lines[1] == "  Test Header"
        assert lines[2] == "=" * 70

    def test_custom_character_header(self, capsys):
        """Test header with custom character."""
        print_header("Custom Header", char='-')
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "-" * 70
        assert lines[1] == "  Custom Header"
        assert lines[2] == "-" * 70

    def test_empty_header(self, capsys):
        """Test header with empty text."""
        print_header("")
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        assert len(lines) == 3
        assert lines[1] == "  "

    def test_long_header_text(self, capsys):
        """Test header with very long text."""
        long_text = "A" * 100
        print_header(long_text)
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        assert len(lines) == 3
        assert lines[1] == f"  {long_text}"

    def test_header_with_special_characters(self, capsys):
        """Test header with special characters in text."""
        print_header("Header with symbols: !@#$%^&*()")
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        assert lines[1] == "  Header with symbols: !@#$%^&*()"

    def test_header_with_unicode(self, capsys):
        """Test header with unicode text."""
        print_header("Hëädér wïth ünïcödé")
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        assert "Hëädér wïth ünïcödé" in lines[1]

    def test_multiple_headers(self, capsys):
        """Test printing multiple headers in sequence."""
        print_header("First")
        print_header("Second")
        captured = capsys.readouterr()

        lines = captured.out.strip().split('\n')
        # Each header has 3 lines, plus blank lines between
        assert "  First" in captured.out
        assert "  Second" in captured.out
