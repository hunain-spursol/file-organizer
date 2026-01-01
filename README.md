# File Organizer

A powerful Python application to organize and manage your files efficiently.

## Features

- **Organize by Type**: Sort files into folders based on their type (Images, Documents, Videos, etc.)
- **Organize by Date**: Arrange files into Year/Month folder structure based on modification date
- **Organize by Size**: Group files by size categories (Tiny, Small, Medium, Large, Huge)
- **Find Duplicates**: Detect duplicate files using content hashing
- **Directory Analysis**: Get detailed statistics about your directory contents
- **Custom Rules**: Define your own file categorization rules
- **Undo Support**: Undo the last batch of operations
- **Dry Run Mode**: Preview changes before applying them

## Project Structure

```
file-organizer/
├── src/
│   └── file_organizer/
│       ├── __init__.py
│       ├── core/                   # Core business logic
│       │   ├── organizer.py        # Main FileOrganizer class
│       │   └── analyzer.py         # Directory analysis
│       ├── strategies/             # Organization strategies
│       │   ├── base.py             # Base strategy class
│       │   ├── by_type.py          # Organize by file type
│       │   ├── by_date.py          # Organize by date
│       │   ├── by_size.py          # Organize by size
│       │   └── duplicates.py       # Duplicate detection
│       ├── config/                 # Configuration
│       │   ├── file_types.py       # File type definitions
│       │   └── settings.py         # App settings
│       ├── utils/                  # Utilities
│       │   ├── file_hash.py        # Hashing utilities
│       │   ├── formatter.py        # Output formatting
│       │   └── undo_manager.py     # Undo functionality
│       └── cli/                    # CLI interface
│           ├── menu.py             # Menu system
│           └── prompts.py          # User prompts
├── main.py                         # Entry point
├── requirements.txt
└── README.md
```

## Installation

### For Users

1. Clone or download this repository
2. No external dependencies required (uses only Python standard library)

```bash
python main.py
```

### For Developers

1. Clone the repository
2. Set up the development environment with virtual environment:

**Windows:**
```bash
setup_dev.bat
```

**Linux/Mac:**
```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

**Or manually:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt
```

## Usage

Run the application:

```bash
python main.py
```

Follow the interactive menu to:
1. Select a directory to organize
2. Choose an organization method
3. Preview changes with dry run
4. Apply changes or undo if needed

## Testing

The project includes comprehensive tests covering all functionality.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/file_organizer --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_organizer.py

# Use the test runner script
python run_tests.py all          # Run all tests
python run_tests.py unit         # Unit tests only
python run_tests.py integration  # Integration tests only
python run_tests.py coverage     # With coverage report
```

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/                       # Unit tests
│   ├── test_organizer.py       # Core organizer tests
│   ├── test_analyzer.py        # Analyzer tests
│   ├── test_strategies/        # Strategy tests
│   │   ├── test_by_type.py
│   │   ├── test_by_date.py
│   │   ├── test_by_size.py
│   │   └── test_duplicates.py
│   └── test_utils/             # Utility tests
│       ├── test_file_hash.py
│       ├── test_formatter.py
│       └── test_undo_manager.py
└── integration/                # Integration tests
    └── test_end_to_end.py      # End-to-end workflows
```

## Architecture

### Strategy Pattern
The application uses the Strategy pattern for different organization methods:
- `OrganizeByType`: Categorizes files by extension
- `OrganizeByDate`: Groups files by modification date
- `OrganizeBySize`: Sorts files by size ranges
- `DuplicateFinder`: Identifies duplicate files using MD5 hashing

### Separation of Concerns
- **Core**: Business logic and coordination
- **Strategies**: Individual organization algorithms
- **Config**: Centralized configuration and constants
- **Utils**: Reusable utilities (hashing, formatting, undo)
- **CLI**: User interface and interaction

### Key Design Principles
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Easy to add new organization strategies
- **Dependency Inversion**: Core depends on abstractions (base strategy)
- **DRY**: Common functionality extracted into utilities

## Extending the Application

### Adding a New Organization Strategy

1. Create a new file in `src/file_organizer/strategies/`
2. Inherit from `OrganizationStrategy`
3. Implement the `organize()` method
4. Add it to the organizer in `core/organizer.py`
5. Add menu option in `cli/menu.py`

Example:

```python
from .base import OrganizationStrategy

class OrganizeByExtension(OrganizationStrategy):
    def organize(self, directory, dry_run=False):
        # Your implementation here
        pass
```

### Adding New File Types

Edit `src/file_organizer/config/file_types.py`:

```python
FILE_TYPES = {
    'MyCategory': ['.ext1', '.ext2'],
    # ...
}
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
