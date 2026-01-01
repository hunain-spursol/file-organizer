# Test Suite Documentation

This directory contains comprehensive tests for the File Organizer application.

## Test Organization

### Unit Tests (`tests/unit/`)

Unit tests verify individual components in isolation.

#### Utilities Tests (`test_utils/`)
- **test_file_hash.py**: Tests for file hashing functionality
  - Hash calculation accuracy
  - Different hash algorithms (MD5, SHA256, etc.)
  - Handling of large files (chunked reading)
  - Edge cases (empty files, special characters)

- **test_formatter.py**: Tests for output formatting
  - Human-readable size formatting
  - Separator and header printing
  - Edge cases and precision

- **test_undo_manager.py**: Tests for undo functionality
  - Operation logging
  - Save/load operations
  - Undo execution and reversal
  - Error handling

#### Strategy Tests (`test_strategies/`)
- **test_by_type.py**: Tests for organizing files by type
  - Category detection (images, documents, code, etc.)
  - File movement and organization
  - Custom categorization rules
  - Edge cases (unknown types, no extension)

- **test_by_date.py**: Tests for organizing files by date
  - Date-based folder structure (YYYY/MM)
  - Handling different date ranges
  - Preservation of file metadata
  - Edge cases (future dates, old files)

- **test_by_size.py**: Tests for organizing files by size
  - Size category detection (Tiny, Small, Medium, Large, Huge)
  - Boundary conditions (exact size thresholds)
  - File size calculations

- **test_duplicates.py**: Tests for duplicate file detection
  - Finding duplicate files by content hash
  - Deletion of duplicates
  - Space savings calculation
  - Nested directory handling

#### Core Tests
- **test_organizer.py**: Tests for main FileOrganizer class
  - Initialization and configuration
  - Custom rules management
  - Strategy invocation
  - Statistics tracking

- **test_analyzer.py**: Tests for directory analysis
  - File counting and size calculation
  - Category statistics
  - Percentage calculations
  - Empty folder cleanup

### Integration Tests (`tests/integration/`)

Integration tests verify complete workflows and component interactions.

- **test_end_to_end.py**: End-to-end workflow tests
  - Complete organization workflows
  - Dry run → actual execution
  - Organize → undo → reorganize
  - Multiple strategies in sequence
  - Error recovery scenarios
  - Statistics and tracking

## Test Fixtures

The `conftest.py` file provides shared test fixtures:

- **temp_dir**: Temporary directory for test file operations
- **sample_files**: Set of common test files
- **sample_files_with_dates**: Files with specific modification dates
- **sample_files_by_size**: Files of different sizes
- **duplicate_files**: Files with duplicate content
- **nested_directory**: Nested directory structure
- **special_characters_files**: Files with special characters

## Running Tests

### Quick Start
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_organizer.py

# Run specific test class
pytest tests/unit/test_organizer.py::TestFileOrganizerInit

# Run specific test method
pytest tests/unit/test_organizer.py::TestFileOrganizerInit::test_initialization
```

### Coverage
```bash
# Run with coverage report
pytest --cov=src/file_organizer

# Generate HTML coverage report
pytest --cov=src/file_organizer --cov-report=html

# Open coverage report
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### Test Categories
```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run fast tests (exclude slow tests)
pytest -m "not slow"
```

### Using the Test Runner
```bash
# Run all tests
python run_tests.py all

# Run unit tests only
python run_tests.py unit

# Run integration tests only
python run_tests.py integration

# Run with coverage
python run_tests.py coverage

# Run specific test file
python run_tests.py specific tests/unit/test_organizer.py
```

## Test Coverage Goals

The test suite aims for:
- **Line Coverage**: > 90%
- **Branch Coverage**: > 85%
- **Critical Path Coverage**: 100%

Current coverage can be viewed by running:
```bash
pytest --cov=src/file_organizer --cov-report=term-missing
```

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
import pytest
from src.file_organizer.core.organizer import FileOrganizer

class TestFeatureName:
    """Test suite for feature description."""

    def test_basic_functionality(self, temp_dir):
        """Test basic feature behavior."""
        # Arrange
        organizer = FileOrganizer()

        # Act
        result = organizer.some_method()

        # Assert
        assert result == expected_value

    def test_edge_case(self, temp_dir):
        """Test edge case handling."""
        # Test implementation
        pass
```

### Best Practices
1. **Arrange-Act-Assert**: Structure tests clearly
2. **One concept per test**: Test one thing at a time
3. **Descriptive names**: Test names should describe what they test
4. **Use fixtures**: Leverage pytest fixtures for setup
5. **Test edge cases**: Don't just test happy paths
6. **Mock external dependencies**: Use mocks for file system operations when needed

## Continuous Integration

Tests are designed to run in CI/CD environments:
- No external dependencies required (uses temp directories)
- Fast execution (< 30 seconds for full suite)
- Isolated tests (no shared state between tests)
- Cross-platform compatible (Windows, Linux, macOS)

## Debugging Tests

### Run with debugging
```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Very verbose output
pytest -vv
```

### Common Issues
- **Path issues**: Use `Path` objects from `pathlib`
- **Temp directory cleanup**: Fixtures handle cleanup automatically
- **File permissions**: Tests handle permission errors gracefully
- **Platform differences**: Tests are cross-platform compatible

## Test Metrics

Track these metrics for test quality:
- **Test count**: Number of test cases
- **Coverage**: Percentage of code covered
- **Execution time**: Time to run full suite
- **Flakiness**: Tests that fail intermittently
- **Maintenance burden**: Time to update tests when code changes
