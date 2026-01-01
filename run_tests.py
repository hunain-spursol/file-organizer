#!/usr/bin/env python3
"""
Test runner script for File Organizer.

This script provides convenient commands to run different test suites.
"""
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print(f"{'=' * 70}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    print(f"\n✓ {description} completed successfully")
    return True


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [command]")
        print("\nAvailable commands:")
        print("  all              - Run all tests")
        print("  unit             - Run unit tests only")
        print("  integration      - Run integration tests only")
        print("  coverage         - Run tests with coverage report")
        print("  fast             - Run tests without slow tests")
        print("  watch            - Run tests in watch mode")
        print("  specific <path>  - Run specific test file or directory")
        sys.exit(1)

    command = sys.argv[1]

    if command == "all":
        success = run_command("pytest tests/", "Running all tests")

    elif command == "unit":
        success = run_command("pytest tests/unit/", "Running unit tests")

    elif command == "integration":
        success = run_command("pytest tests/integration/", "Running integration tests")

    elif command == "coverage":
        success = run_command(
            "pytest tests/ --cov=src/file_organizer --cov-report=html --cov-report=term",
            "Running tests with coverage"
        )
        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")

    elif command == "fast":
        success = run_command('pytest tests/ -m "not slow"', "Running fast tests")

    elif command == "watch":
        try:
            success = run_command(
                "pytest-watch tests/",
                "Running tests in watch mode"
            )
        except KeyboardInterrupt:
            print("\n\nWatch mode stopped.")
            success = True

    elif command == "specific":
        if len(sys.argv) < 3:
            print("Error: Please specify a test path")
            print("Example: python run_tests.py specific tests/unit/test_organizer.py")
            sys.exit(1)
        test_path = sys.argv[2]
        success = run_command(f"pytest {test_path}", f"Running tests in {test_path}")

    else:
        print(f"Unknown command: {command}")
        print("Run 'python run_tests.py' for usage information")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
