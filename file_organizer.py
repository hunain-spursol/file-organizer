import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

class FileOrganizer:
    def __init__(self):
        self.file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.heic', '.heif'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.tex', '.md', '.markdown'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentations': ['.ppt', '.pptx', '.odp'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.html', '.css', '.php', '.rb', '.go', '.rs', '.sql'],
            'Config': ['.yml', '.yaml', '.json', '.xml', '.toml', '.ini', '.env'],
            'Executables': ['.exe', '.msi', '.app', '.deb', '.rpm'],
            'Other': []
        }
        
        self.custom_rules = {}  # User-defined categories
        self.undo_log = []  # Track operations for undo
        self.undo_log_file = Path.home() / '.file_organizer_undo.json'
        
        self.stats = {
            'files_moved': 0,
            'duplicates_found': 0,
            'space_saved': 0,
            'categories': defaultdict(int)
        }
    
    def get_file_hash(self, filepath):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def log_operation(self, operation_type, source, destination):
        """Log an operation for undo"""
        self.undo_log.append({
            'type': operation_type,
            'source': str(source),
            'destination': str(destination),
            'timestamp': datetime.now().isoformat()
        })
    
    def save_undo_log(self):
        """Save undo log to file"""
        try:
            with open(self.undo_log_file, 'w') as f:
                json.dump(self.undo_log, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save undo log: {e}")
    
    def load_undo_log(self):
        """Load undo log from file"""
        if self.undo_log_file.exists():
            try:
                with open(self.undo_log_file, 'r') as f:
                    self.undo_log = json.load(f)
                return True
            except:
                return False
        return False
    
    def undo_last_operation(self):
        """Undo the last batch of operations"""
        if not self.load_undo_log() or not self.undo_log:
            print("\n❌ No operations to undo")
            return
        
        print(f"\n🔄 Found {len(self.undo_log)} operations in last session")
        print(f"Last operation: {self.undo_log[-1]['timestamp']}")
        
        if input("\nUndo all operations from last session? (y/n): ").lower() != 'y':
            return
        
        print("\n" + "─" * 70)
        undone = 0
        errors = 0
        
        # Reverse the operations
        for op in reversed(self.undo_log):
            try:
                source = Path(op['source'])
                dest = Path(op['destination'])
                
                if dest.exists():
                    dest.rename(source)
                    print(f"✓ Restored: {dest.name} → {source.parent}/")
                    undone += 1
                else:
                    print(f"⚠ File not found: {dest.name}")
                    errors += 1
            except Exception as e:
                print(f"✗ Error undoing {dest.name}: {e}")
                errors += 1
        
        print("─" * 70)
        print(f"\n✓ Undone: {undone} operations")
        if errors:
            print(f"⚠ Errors: {errors}")
        
        # Clear the log after successful undo
        self.undo_log = []
        self.save_undo_log()
    
    def get_category(self, extension):
        """Get category for file extension"""
        extension = extension.lower()
        
        # Check custom rules first
        for category, extensions in self.custom_rules.items():
            if extension in extensions:
                return category
        
        # Handle special compound extensions
        if 'postman_collection' in extension:
            return 'Config'
        
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
        return 'Other'
    
    def organize_by_type(self, directory, dry_run=False):
        """Organize files into folders by type"""
        directory = Path(directory)
        files_processed = 0
        
        if not dry_run:
            self.undo_log = []  # Clear log for new session
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by type in: {directory}")
        print("─" * 70)
        
        for item in directory.iterdir():
            if item.is_file():
                category = self.get_category(item.suffix)
                target_dir = directory / category
                
                if not dry_run:
                    target_dir.mkdir(exist_ok=True)
                    target_file = target_dir / item.name
                    
                    # Handle duplicates
                    counter = 1
                    while target_file.exists():
                        target_file = target_dir / f"{item.stem}_{counter}{item.suffix}"
                        counter += 1
                    
                    shutil.move(str(item), str(target_file))
                    self.log_operation('move', item, target_file)
                    self.stats['files_moved'] += 1
                    self.stats['categories'][category] += 1
                
                files_processed += 1
                print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} → {category}/")
        
        if not dry_run:
            self.save_undo_log()
        
        print(f"\n✓ Processed {files_processed} files")
        return files_processed
    
    def organize_by_date(self, directory, dry_run=False):
        """Organize files into YYYY/MM folders by modification date"""
        directory = Path(directory)
        files_processed = 0
        
        if not dry_run:
            self.undo_log = []  # Clear log for new session
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by date in: {directory}")
        print("─" * 70)
        
        for item in directory.iterdir():
            if item.is_file():
                mod_time = datetime.fromtimestamp(item.stat().st_mtime)
                year_folder = directory / str(mod_time.year)
                month_folder = year_folder / f"{mod_time.month:02d}-{mod_time.strftime('%B')}"
                
                if not dry_run:
                    month_folder.mkdir(parents=True, exist_ok=True)
                    target_file = month_folder / item.name
                    
                    # Handle duplicates
                    counter = 1
                    while target_file.exists():
                        target_file = month_folder / f"{item.stem}_{counter}{item.suffix}"
                        counter += 1
                    
                    shutil.move(str(item), str(target_file))
                    self.log_operation('move', item, target_file)
                    self.stats['files_moved'] += 1
                
                files_processed += 1
                print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} → {mod_time.year}/{mod_time.month:02d}/")
        
        if not dry_run:
            self.save_undo_log()
        
        print(f"\n✓ Processed {files_processed} files")
        return files_processed
    
    def find_duplicates(self, directory, delete=False):
        """Find duplicate files based on content hash"""
        directory = Path(directory)
        file_hashes = defaultdict(list)
        duplicates = []
        total_size = 0
        
        print(f"\n{'[DELETE MODE] ' if delete else ''}Finding duplicates in: {directory}")
        print("─" * 70)
        print("Scanning files...")
        
        # Build hash map
        for item in directory.rglob('*'):
            if item.is_file():
                file_hash = self.get_file_hash(item)
                if file_hash:
                    file_hashes[file_hash].append(item)
        
        # Find duplicates
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                duplicates.append(files)
                file_size = files[0].stat().st_size
                duplicate_size = file_size * (len(files) - 1)
                total_size += duplicate_size
                
                print(f"\n🔄 Found {len(files)} duplicates ({self.format_size(file_size)} each):")
                for i, file in enumerate(files):
                    status = "[ORIGINAL]" if i == 0 else "[DUPLICATE]"
                    print(f"  {status} {file.relative_to(directory)}")
                    
                    if delete and i > 0:  # Keep first, delete rest
                        file.unlink()
                        print(f"    ✗ Deleted")
                        self.stats['duplicates_found'] += 1
                        self.stats['space_saved'] += file_size
        
        print(f"\n{'─' * 70}")
        print(f"Total duplicate sets: {len(duplicates)}")
        print(f"Potential space savings: {self.format_size(total_size)}")
        
        if delete:
            print(f"✓ Deleted {self.stats['duplicates_found']} duplicate files")
            print(f"✓ Freed up {self.format_size(self.stats['space_saved'])}")
        
        return duplicates
    
    def organize_by_size(self, directory, dry_run=False):
        """Organize files into size categories"""
        directory = Path(directory)
        files_processed = 0
        
        if not dry_run:
            self.undo_log = []
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by size in: {directory}")
        print("─" * 70)
        
        # Size thresholds
        size_categories = {
            'Tiny (< 1MB)': (0, 1024 * 1024),
            'Small (1-10MB)': (1024 * 1024, 10 * 1024 * 1024),
            'Medium (10-100MB)': (10 * 1024 * 1024, 100 * 1024 * 1024),
            'Large (100MB-1GB)': (100 * 1024 * 1024, 1024 * 1024 * 1024),
            'Huge (> 1GB)': (1024 * 1024 * 1024, float('inf'))
        }
        
        for item in directory.iterdir():
            if item.is_file():
                size = item.stat().st_size
                
                # Determine category
                category = None
                for cat_name, (min_size, max_size) in size_categories.items():
                    if min_size <= size < max_size:
                        category = cat_name
                        break
                
                if category:
                    target_dir = directory / category
                    
                    if not dry_run:
                        target_dir.mkdir(exist_ok=True)
                        target_file = target_dir / item.name
                        
                        counter = 1
                        while target_file.exists():
                            target_file = target_dir / f"{item.stem}_{counter}{item.suffix}"
                            counter += 1
                        
                        shutil.move(str(item), str(target_file))
                        self.log_operation('move', item, target_file)
                        self.stats['files_moved'] += 1
                    
                    files_processed += 1
                    print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} ({self.format_size(size)}) → {category}/")
        
        if not dry_run:
            self.save_undo_log()
        
        print(f"\n✓ Processed {files_processed} files")
        return files_processed
    
    def manage_custom_rules(self):
        """Manage custom file categorization rules"""
        while True:
            print("\n" + "=" * 70)
            print("  CUSTOM RULES")
            print("=" * 70)
            
            if self.custom_rules:
                print("\nCurrent rules:")
                for category, extensions in self.custom_rules.items():
                    print(f"  {category}: {', '.join(extensions)}")
            else:
                print("\nNo custom rules defined")
            
            print("\nOptions:")
            print("  1. Add new rule")
            print("  2. Remove rule")
            print("  3. Back to main menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                category = input("\nEnter category name (e.g., 'Work Docs'): ").strip()
                if not category:
                    print("❌ Category name required")
                    continue
                
                extensions = input("Enter extensions (comma-separated, e.g., .xlsx,.pptx): ").strip()
                ext_list = [ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}' 
                           for ext in extensions.split(',') if ext.strip()]
                
                if ext_list:
                    self.custom_rules[category] = ext_list
                    print(f"✓ Added rule: {category} → {', '.join(ext_list)}")
                else:
                    print("❌ No valid extensions provided")
            
            elif choice == '2':
                if not self.custom_rules:
                    print("❌ No rules to remove")
                    continue
                
                category = input("\nEnter category name to remove: ").strip()
                if category in self.custom_rules:
                    del self.custom_rules[category]
                    print(f"✓ Removed rule: {category}")
                else:
                    print(f"❌ Rule '{category}' not found")
            
            elif choice == '3':
                break
    
    def analyze_directory(self, directory):
        """Analyze directory and show statistics"""
        directory = Path(directory)
        category_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        total_size = 0
        total_files = 0
        
        print(f"\n📊 Analyzing: {directory}")
        print("─" * 70)
        
        for item in directory.rglob('*'):
            if item.is_file():
                size = item.stat().st_size
                category = self.get_category(item.suffix)
                
                category_stats[category]['count'] += 1
                category_stats[category]['size'] += size
                total_size += size
                total_files += 1
        
        print(f"\nTotal Files: {total_files}")
        print(f"Total Size: {self.format_size(total_size)}\n")
        
        print(f"{'Category':<20} {'Files':<10} {'Size':<15} {'%'}")
        print("─" * 70)
        
        for category in sorted(category_stats.keys(), key=lambda x: category_stats[x]['size'], reverse=True):
            stats = category_stats[category]
            percentage = (stats['size'] / total_size * 100) if total_size > 0 else 0
            print(f"{category:<20} {stats['count']:<10} {self.format_size(stats['size']):<15} {percentage:>5.1f}%")
    
    def format_size(self, size):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def organize_by_size(self, directory, dry_run=False):
        """Organize files into size categories"""
        directory = Path(directory)
        files_processed = 0
        
        if not dry_run:
            self.undo_log = []
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by size in: {directory}")
        print("─" * 70)
        
        # Size thresholds
        size_categories = {
            'Tiny (< 1MB)': (0, 1024 * 1024),
            'Small (1-10MB)': (1024 * 1024, 10 * 1024 * 1024),
            'Medium (10-100MB)': (10 * 1024 * 1024, 100 * 1024 * 1024),
            'Large (100MB-1GB)': (100 * 1024 * 1024, 1024 * 1024 * 1024),
            'Huge (> 1GB)': (1024 * 1024 * 1024, float('inf'))
        }
        
        for item in directory.iterdir():
            if item.is_file():
                size = item.stat().st_size
                
                # Determine category
                category = None
                for cat_name, (min_size, max_size) in size_categories.items():
                    if min_size <= size < max_size:
                        category = cat_name
                        break
                
                if category:
                    target_dir = directory / category
                    
                    if not dry_run:
                        target_dir.mkdir(exist_ok=True)
                        target_file = target_dir / item.name
                        
                        counter = 1
                        while target_file.exists():
                            target_file = target_dir / f"{item.stem}_{counter}{item.suffix}"
                            counter += 1
                        
                        shutil.move(str(item), str(target_file))
                        self.log_operation('move', item, target_file)
                        self.stats['files_moved'] += 1
                    
                    files_processed += 1
                    print(f"{'[WOULD MOVE]' if dry_run else '[MOVED]'} {item.name} ({self.format_size(size)}) → {category}/")
        
        if not dry_run:
            self.save_undo_log()
        
        print(f"\n✓ Processed {files_processed} files")
        return files_processed
    
    def manage_custom_rules(self):
        """Manage custom file categorization rules"""
        while True:
            print("\n" + "=" * 70)
            print("  CUSTOM RULES")
            print("=" * 70)
            
            if self.custom_rules:
                print("\nCurrent rules:")
                for category, extensions in self.custom_rules.items():
                    print(f"  {category}: {', '.join(extensions)}")
            else:
                print("\nNo custom rules defined")
            
            print("\nOptions:")
            print("  1. Add new rule")
            print("  2. Remove rule")
            print("  3. Back to main menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                category = input("\nEnter category name (e.g., 'Work Docs'): ").strip()
                if not category:
                    print("❌ Category name required")
                    continue
                
                extensions = input("Enter extensions (comma-separated, e.g., .xlsx,.pptx): ").strip()
                ext_list = [ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}' 
                           for ext in extensions.split(',') if ext.strip()]
                
                if ext_list:
                    self.custom_rules[category] = ext_list
                    print(f"✓ Added rule: {category} → {', '.join(ext_list)}")
                else:
                    print("❌ No valid extensions provided")
            
            elif choice == '2':
                if not self.custom_rules:
                    print("❌ No rules to remove")
                    continue
                
                category = input("\nEnter category name to remove: ").strip()
                if category in self.custom_rules:
                    del self.custom_rules[category]
                    print(f"✓ Removed rule: {category}")
                else:
                    print(f"❌ Rule '{category}' not found")
            
            elif choice == '3':
                break
    
    def clean_empty_folders(self, directory, dry_run=False):
        """Remove empty folders"""
        directory = Path(directory)
        removed = 0
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Cleaning empty folders in: {directory}")
        print("─" * 70)
        
        for item in directory.rglob('*'):
            if item.is_dir() and not any(item.iterdir()):
                print(f"{'[WOULD DELETE]' if dry_run else '[DELETED]'} {item.relative_to(directory)}/")
                if not dry_run:
                    item.rmdir()
                removed += 1
        
        print(f"\n✓ {'Would remove' if dry_run else 'Removed'} {removed} empty folders")
        return removed

def print_banner():
    print("\n" + "=" * 70)
    print("  📁 FILE ORGANIZER - Clean up your messy directories")
    print("=" * 70)

def print_menu():
    print("\nOptions:")
    print("  1. Organize by file type")
    print("  2. Organize by date (Year/Month)")
    print("  3. Organize by size")
    print("  4. Find duplicates")
    print("  5. Find and DELETE duplicates")
    print("  6. Analyze directory")
    print("  7. Clean empty folders")
    print("  8. Manage custom rules")
    print("  9. Undo last operation")
    print("  10. Exit")

def main():
    print_banner()
    organizer = FileOrganizer()
    
    # Get directory
    print("\nEnter directory path (or press Enter for current directory):")
    directory = input("> ").strip() or os.getcwd()
    
    if not os.path.isdir(directory):
        print(f"❌ Error: '{directory}' is not a valid directory")
        return
    
    while True:
        print_menu()
        choice = input("\nSelect option (1-10): ").strip()
        
        if choice == '1':
            dry = input("Dry run first? (y/n): ").lower() == 'y'
            organizer.organize_by_type(directory, dry_run=dry)
            if dry:
                if input("\nProceed with actual organization? (y/n): ").lower() == 'y':
                    organizer.organize_by_type(directory, dry_run=False)
        
        elif choice == '2':
            dry = input("Dry run first? (y/n): ").lower() == 'y'
            organizer.organize_by_date(directory, dry_run=dry)
            if dry:
                if input("\nProceed with actual organization? (y/n): ").lower() == 'y':
                    organizer.organize_by_date(directory, dry_run=False)
        
        elif choice == '3':
            dry = input("Dry run first? (y/n): ").lower() == 'y'
            organizer.organize_by_size(directory, dry_run=dry)
            if dry:
                if input("\nProceed with actual organization? (y/n): ").lower() == 'y':
                    organizer.organize_by_size(directory, dry_run=False)
        
        elif choice == '4':
            organizer.find_duplicates(directory, delete=False)
        
        elif choice == '5':
            print("\n⚠️  WARNING: This will DELETE duplicate files permanently!")
            if input("Are you sure? (type 'DELETE' to confirm): ") == 'DELETE':
                organizer.find_duplicates(directory, delete=True)
        
        elif choice == '6':
            organizer.analyze_directory(directory)
        
        elif choice == '7':
            dry = input("Dry run first? (y/n): ").lower() == 'y'
            organizer.clean_empty_folders(directory, dry_run=dry)
            if dry:
                if input("\nProceed with actual cleanup? (y/n): ").lower() == 'y':
                    organizer.clean_empty_folders(directory, dry_run=False)
        
        elif choice == '8':
            organizer.manage_custom_rules()
        
        elif choice == '9':
            organizer.undo_last_operation()
        
        elif choice == '10':
            print("\n👋 Bye!")
            break
        
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()