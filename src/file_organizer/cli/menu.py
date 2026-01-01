"""Menu system for CLI interface."""

import os
from ..utils.formatter import print_header
from . import prompts


def print_banner():
    """Print application banner."""
    print_header("📁 FILE ORGANIZER - Clean up your messy directories")


def print_main_menu():
    """Print main menu options."""
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


def manage_custom_rules_menu(organizer):
    """
    Manage custom rules submenu.

    Args:
        organizer: FileOrganizer instance
    """
    while True:
        print_header("CUSTOM RULES")

        rules = organizer.get_custom_rules()
        if rules:
            print("\nCurrent rules:")
            for category, extensions in rules.items():
                print(f"  {category}: {', '.join(extensions)}")
        else:
            print("\nNo custom rules defined")

        print("\nOptions:")
        print("  1. Add new rule")
        print("  2. Remove rule")
        print("  3. Back to main menu")

        choice = prompts.get_input("\nSelect option").strip()

        if choice == '1':
            add_custom_rule(organizer)
        elif choice == '2':
            remove_custom_rule(organizer)
        elif choice == '3':
            break


def add_custom_rule(organizer):
    """Add a custom categorization rule."""
    category = prompts.get_input("\nEnter category name (e.g., 'Work Docs')")
    if not category:
        print("❌ Category name required")
        return

    extensions = prompts.get_input("Enter extensions (comma-separated, e.g., .xlsx,.pptx)")
    ext_list = [
        ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}'
        for ext in extensions.split(',') if ext.strip()
    ]

    if ext_list:
        organizer.add_custom_rule(category, ext_list)
        print(f"✓ Added rule: {category} → {', '.join(ext_list)}")
    else:
        print("❌ No valid extensions provided")


def remove_custom_rule(organizer):
    """Remove a custom categorization rule."""
    rules = organizer.get_custom_rules()
    if not rules:
        print("❌ No rules to remove")
        return

    category = prompts.get_input("\nEnter category name to remove")
    if organizer.remove_custom_rule(category):
        print(f"✓ Removed rule: {category}")
    else:
        print(f"❌ Rule '{category}' not found")


def get_directory():
    """
    Get directory from user.

    Returns:
        str: Directory path or None if invalid
    """
    print("\nEnter directory path (or press Enter for current directory):")
    directory = prompts.get_input("> ") or os.getcwd()

    if not os.path.isdir(directory):
        print(f"❌ Error: '{directory}' is not a valid directory")
        return None

    return directory
