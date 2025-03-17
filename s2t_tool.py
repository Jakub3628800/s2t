#!/usr/bin/env python3
"""
S2T Tool - A simplified wrapper for the S2T speech recognition tool.

This tool script provides a way to run s2t using UV's tool interface.
It wraps the main s2t.py script and forwards arguments to it.

Usage:
  uvx s2t_tool [options]

Options:
  Same options as s2t.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_system_dependencies():
    """Check if required system dependencies are installed."""
    missing_deps = []
    
    # Check for libgirepository (for GUI mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gobject-introspection-1.0"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgirepository1.0-dev")
    
    # Check for GTK4 (for popup mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gtk4"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgtk-4-dev")
    
    # Check for wtype (for typing)
    try:
        subprocess.run(["which", "wtype"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("wtype")
    
    return missing_deps

def main():
    """Main function for the UV tool wrapper."""
    # Get the directory where this script is located
    current_dir = Path(__file__).parent.absolute()
    
    # Path to the main s2t.py script
    s2t_script = current_dir / "s2t.py"
    
    # Make sure the script exists
    if not s2t_script.exists():
        print(f"Error: Could not find s2t.py at {s2t_script}")
        sys.exit(1)
    
    # Check for required system dependencies
    missing_deps = check_system_dependencies()
    if missing_deps:
        print("\n⚠️  Missing system dependencies detected! ⚠️")
        print("The following system packages are required but not found:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nOn Ubuntu/Debian, install them with:")
        print(f"  sudo apt-get install {' '.join(missing_deps)}")
        print("\nContinuing anyway, but the script may fail...\n")
    
    # Get all command-line arguments (excluding the script name)
    args = sys.argv[1:]
    
    # Prepare the command to run s2t.py with the same arguments
    cmd = [sys.executable, str(s2t_script)] + args
    
    # Run the command
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running s2t.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
