"""
Configuration for pytest.
"""

import sys
import os

# Mock sys.argv to prevent argparse errors
sys.argv = ['pytest']

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
