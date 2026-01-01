# File Organizer

A powerful command-line utility to organize and clean up messy directories.

## Features

- **Organize by File Type** - Sort files into categories (Images, Videos, Documents, Code, etc.)
- **Organize by Date** - Arrange files into YYYY/MM folder structure
- **Organize by Size** - Group files by size categories
- **Find Duplicates** - Identify and remove duplicate files using MD5 hashing
- **Directory Analysis** - View statistics about file types and sizes
- **Custom Rules** - Define your own file categorization rules
- **Undo Support** - Reverse operations with built-in undo functionality
- **Dry Run Mode** - Preview changes before applying them

## Supported File Types

73+ file extensions across 10 categories:
- Images (jpg, png, gif, svg, etc.)
- Videos (mp4, avi, mkv, etc.)
- Audio (mp3, wav, flac, etc.)
- Documents (pdf, docx, txt, md, etc.)
- Code (py, js, java, cpp, etc.)
- And more...

## Usage

```bash
python file_organizer.py
```

Follow the interactive menu to:
1. Select your directory
2. Choose an organization method
3. Preview with dry-run mode
4. Apply changes

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/file-organizer.git
cd file-organizer
python file_organizer.py
```

## Safety Features

- Dry-run mode for previewing changes
- Automatic duplicate filename handling
- Undo log stored in `~/.file_organizer_undo.json`
- Confirmation prompts for destructive operations

## License

MIT License - Feel free to use and modify
