"""File type definitions and categorizations."""

FILE_TYPES = {
    'Images': [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
        '.webp', '.ico', '.heic', '.heif'
    ],
    'Videos': [
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'
    ],
    'Audio': [
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'
    ],
    'Documents': [
        '.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf',
        '.tex', '.md', '.markdown'
    ],
    'Spreadsheets': [
        '.xls', '.xlsx', '.csv', '.ods'
    ],
    'Presentations': [
        '.ppt', '.pptx', '.odp'
    ],
    'Archives': [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'
    ],
    'Code': [
        '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs',
        '.html', '.css', '.php', '.rb', '.go', '.rs', '.sql'
    ],
    'Config': [
        '.yml', '.yaml', '.json', '.xml', '.toml', '.ini', '.env'
    ],
    'Executables': [
        '.exe', '.msi', '.app', '.deb', '.rpm'
    ],
    'Other': []
}

SIZE_CATEGORIES = {
    'Tiny (< 1MB)': (0, 1024 * 1024),
    'Small (1-10MB)': (1024 * 1024, 10 * 1024 * 1024),
    'Medium (10-100MB)': (10 * 1024 * 1024, 100 * 1024 * 1024),
    'Large (100MB-1GB)': (100 * 1024 * 1024, 1024 * 1024 * 1024),
    'Huge (> 1GB)': (1024 * 1024 * 1024, float('inf'))
}
