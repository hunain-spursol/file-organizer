"""User prompts and input handling."""


def confirm_action(message):
    """
    Ask user for yes/no confirmation.

    Args:
        message: Message to display

    Returns:
        bool: True if user confirmed, False otherwise
    """
    response = input(f"{message} (y/n): ").strip().lower()
    return response == 'y'


def get_dry_run_preference():
    """
    Ask if user wants to do a dry run first.

    Returns:
        bool: True if dry run requested
    """
    return confirm_action("Dry run first?")


def confirm_dry_run_proceed():
    """
    Ask if user wants to proceed after dry run.

    Returns:
        bool: True if user wants to proceed
    """
    return confirm_action("\nProceed with actual organization?")


def confirm_delete():
    """
    Get confirmation for destructive delete operation.

    Returns:
        bool: True if user confirmed deletion
    """
    print("\n⚠️  WARNING: This will DELETE duplicate files permanently!")
    return input("Are you sure? (type 'DELETE' to confirm): ").strip() == 'DELETE'


def get_menu_choice():
    """
    Get menu choice from user.

    Returns:
        str: User's choice
    """
    return input("\nSelect option (1-10): ").strip()


def get_input(prompt):
    """
    Get input from user.

    Args:
        prompt: Prompt to display

    Returns:
        str: User input (stripped)
    """
    return input(f"{prompt}: ").strip()


def wait_for_continue():
    """Wait for user to press Enter."""
    input("\nPress Enter to continue...")
