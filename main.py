"""File Organizer - Main entry point."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from file_organizer import FileOrganizer
from file_organizer.cli import (
    print_banner,
    print_main_menu,
    manage_custom_rules_menu,
    get_directory,
    get_dry_run_preference,
    confirm_dry_run_proceed,
    confirm_delete,
    get_menu_choice,
    wait_for_continue
)


def handle_organize_operation(organizer, directory, operation_func, operation_name):
    """
    Handle an organize operation with optional dry run.

    Args:
        organizer: FileOrganizer instance
        directory: Directory to organize
        operation_func: Function to call for organization
        operation_name: Name of the operation for display
    """
    dry_run = get_dry_run_preference()
    operation_func(directory, dry_run=dry_run)

    if dry_run and confirm_dry_run_proceed():
        operation_func(directory, dry_run=False)


def main():
    """Main application loop."""
    print_banner()
    organizer = FileOrganizer()

    # Get directory
    directory = get_directory()
    if not directory:
        return

    while True:
        print_main_menu()
        choice = get_menu_choice()

        if choice == '1':
            handle_organize_operation(
                organizer, directory,
                organizer.organize_by_type,
                "Organize by type"
            )

        elif choice == '2':
            handle_organize_operation(
                organizer, directory,
                organizer.organize_by_date,
                "Organize by date"
            )

        elif choice == '3':
            handle_organize_operation(
                organizer, directory,
                organizer.organize_by_size,
                "Organize by size"
            )

        elif choice == '4':
            organizer.find_duplicates(directory, delete=False)

        elif choice == '5':
            if confirm_delete():
                organizer.find_duplicates(directory, delete=True)

        elif choice == '6':
            organizer.analyze_directory(directory)

        elif choice == '7':
            dry_run = get_dry_run_preference()
            organizer.clean_empty_folders(directory, dry_run=dry_run)
            if dry_run and confirm_dry_run_proceed():
                organizer.clean_empty_folders(directory, dry_run=False)

        elif choice == '8':
            manage_custom_rules_menu(organizer)

        elif choice == '9':
            organizer.undo_last_operation()

        elif choice == '10':
            print("\n👋 Bye!")
            break

        else:
            print("❌ Invalid option")

        wait_for_continue()


if __name__ == "__main__":
    main()
