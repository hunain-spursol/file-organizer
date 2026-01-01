"""Output formatting utilities."""


def format_size(size):
    """
    Format bytes to human readable string.

    Args:
        size: Size in bytes

    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def print_separator(char='─', length=70):
    """Print a separator line."""
    print(char * length)


def print_header(text, char='='):
    """Print a formatted header."""
    print(f"\n{char * 70}")
    print(f"  {text}")
    print(f"{char * 70}")
