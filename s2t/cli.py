#!/usr/bin/env python3
"""
Command-line interface entry points for S2T.

This module provides wrapper functions for all the command-line entry points
that check for required system dependencies before importing modules that need them.
"""

import sys
import subprocess
import importlib
import argparse


def check_system_dependencies():
    """Check if required system dependencies are installed."""
    missing_deps = []
    
    # Check for libgirepository (for GUI mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gobject-introspection-1.0"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgirepository1.0-dev")
    
    # Check for GTK4 (for popup mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gtk4"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgtk-4-dev")
    
    # Check for wtype (for typing)
    try:
        subprocess.run(["which", "wtype"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("wtype")
    
    return missing_deps


def print_dependency_warning(missing_deps):
    """Print a warning about missing dependencies."""
    print("\n⚠️  Missing system dependencies detected! ⚠️")
    print("The following system packages are required but not found:")
    for dep in missing_deps:
        print(f"  - {dep}")
    print("\nOn Ubuntu/Debian, install them with:")
    print(f"  sudo apt-get install {' '.join(missing_deps)}")
    print("\nCannot continue without these dependencies.\n")


def run_popup():
    """Run the popup recorder."""
    missing_deps = check_system_dependencies()
    if missing_deps:
        print_dependency_warning(missing_deps)
        sys.exit(1)
    
    try:
        from s2t.popup_recorder import main
        main()
    except ImportError as e:
        print(f"Error: Missing Python modules: {e}")
        print("Try installing with: pip install s2t[gui]")
        sys.exit(1)


def run_silent():
    """Run the silent recorder."""
    missing_deps = check_system_dependencies()
    if missing_deps:
        print_dependency_warning(missing_deps)
        sys.exit(1)
        
    try:
        from s2t.truly_silent import main
        main()
    except ImportError as e:
        print(f"Error: Missing Python modules: {e}")
        print("Try installing with: pip install s2t[full]")
        sys.exit(1)


def run_immediate():
    """Run the immediate popup recorder."""
    missing_deps = check_system_dependencies()
    if missing_deps:
        print_dependency_warning(missing_deps)
        sys.exit(1)
        
    try:
        from s2t.immediate_popup import main
        main()
    except ImportError as e:
        print(f"Error: Missing Python modules: {e}")
        print("Try installing with: pip install s2t[full]")
        sys.exit(1)


def run_headless():
    """Run the headless recorder."""
    missing_deps = check_system_dependencies()
    if missing_deps:
        print_dependency_warning(missing_deps)
        sys.exit(1)
        
    try:
        from s2t.headless_recorder import main
        main()
    except ImportError as e:
        print(f"Error: Missing Python modules: {e}")
        print("Try installing with: pip install s2t[full]")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="S2T CLI utility")
    parser.add_argument("command", choices=["popup", "silent", "immediate", "headless"], 
                        help="The S2T recorder to run")
    
    # Parse only the command and leave the rest for the underlying module
    args, remaining = parser.parse_known_args()
    
    # Restore the command-line arguments for the underlying module
    if remaining:
        sys.argv = [sys.argv[0]] + remaining
    
    if args.command == "popup":
        run_popup()
    elif args.command == "silent":
        run_silent()
    elif args.command == "immediate":
        run_immediate()
    elif args.command == "headless":
        run_headless()
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1) 