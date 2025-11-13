#!/usr/bin/env python3
"""
Test script for Dad Jokes Board Plugin

This script tests the plugin functionality without requiring the full scoreboard setup.
Run this to validate your plugin before deploying to the actual hardware.

Usage:
python3 test_dad_jokes.py
"""

import json
import sys
import types
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import requests

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, message=""):
    """Print test result with color coding."""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} | {name}")
    if message:
        print(f"       {message}")

def test_plugin_metadata():
    """Test that plugin.json is valid and complete."""
    print(f"\n{Colors.BOLD}Testing Plugin Metadata...{Colors.END}")
    
    try:
        plugin_file = Path("plugin.json")
        if not plugin_file.exists():
            print_test("plugin.json exists", False, "File not found")
            return False
        
        with open(plugin_file) as f:
            metadata = json.load(f)
        
        # Check required fields
        required_fields = ["name", "version", "description", "boards"]
        for field in required_fields:
            if field not in metadata:
                print_test(f"Required field '{field}'", False, "Field missing")
                return False
        
        print_test("plugin.json structure", True, f"Plugin: {metadata['name']} v{metadata['version']}")
        
        # Check boards definition
        if not metadata.get("boards"):
            print_test("Boards definition", False, "No boards defined")
            return False
        
        board = metadata["boards"][0]
        if "id" not in board or "class_name" not in board or "module" not in board:
            print_test("Board definition", False, "Missing required board fields")
            return False
        
        print_test("Board definition", True, f"Board ID: {board['id']}, Class: {board['class_name']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print_test("plugin.json parsing", False, f"Invalid JSON: {e}")
        return False
    except Exception as e:
        print_test("plugin.json validation", False, str(e))
        return False

def test_config_files():
    """Test configuration files."""
    print(f"\n{Colors.BOLD}Testing Configuration Files...{Colors.END}")
    
    try:
        config_sample = Path("config.sample.json")
        if not config_sample.exists():
            print_test("config.sample.json exists", False)
            return False
        
        with open(config_sample) as f:
            config = json.load(f)
        
        print_test("config.sample.json", True, f"Found {len(config)} configuration options")
        
        # Check for recommended config options
        recommended = ["text_color", "display_seconds", "enabled"]
        for opt in recommended:
            if opt in config:
                print_test(f"Config option '{opt}'", True, f"Value: {config[opt]}")
        
        return True
        
    except Exception as e:
        print_test("Configuration files", False, str(e))
        return False

def test_layout_files():
    """Test layout files."""
    print(f"\n{Colors.BOLD}Testing Layout Files...{Colors.END}")
    
    layouts = ["layout_64x32.json", "layout_128x64.json"]
    all_valid = True
    
    for layout_file in layouts:
        try:
            path = Path(layout_file)
            if not path.exists():
                print_test(f"{layout_file}", False, "File not found (optional)")
                continue
            
            with open(path) as f:
                layout = json.load(f)
            
            if "dad_jokes" in layout:
                print_test(f"{layout_file}", True, f"Has dad_jokes layout definition")
            else:
                print_test(f"{layout_file}", True, f"Valid JSON (no dad_jokes section)")
                
        except Exception as e:
            print_test(f"{layout_file}", False, str(e))
            all_valid = False
            
    return all_valid

def test_api_connection():
    """Test connection to icanhazdadjoke.com API."""
    print(f"\n{Colors.BOLD}Testing API Connection...{Colors.END}")
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'NHL LED Scoreboard Dad Jokes Plugin Test'
        }
        
        response = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        joke = data.get('joke', '')
        
        if joke:
            print_test("API connection", True, f"Successfully fetched joke")
            print(f"       {Colors.BLUE}Sample: {joke[:60]}...{Colors.END}")
            return True
        else:
            print_test("API connection", False, "No joke in response")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test("API connection", False, str(e))
        return False

def test_board_class():
    """Test that the board class can be instantiated."""
    print(f"\n{Colors.BOLD}Testing Board Class...{Colors.END}")
    
    try:
        # 1. Setup Environment Mocks
        # We must mock the 'boards' module BEFORE attempting to import/load board.py
        # This fixes the "Import error: No module named 'boards'"
        mock_boards = MagicMock()
        mock_base_board_module = MagicMock()
        
        # Define a mock BoardBase class that behaves like the real one
        class MockBoardBase:
            def __init__(self, data, matrix, sleepEvent):
                self.board_config = {
                    "text_color": "yellow",
                    "display_seconds": 10,
                    "scroll_speed": 0.05,
                    "refresh_interval_hours": 1,
                    "show_header": True
                }
                self.display_width = 64
                self.display_height = 32
                self.data = data
                self.matrix = matrix
                self.sleepEvent = sleepEvent
            
            def get_board_layout(self, name):
                return None
                
            def log_message(self, msg):
                pass

        mock_base_board_module.BoardBase = MockBoardBase
        mock_boards.base_board = mock_base_board_module
        sys.modules['boards'] = mock_boards
        sys.modules['boards.base_board'] = mock_base_board_module

        # 2. Load __init__.py to get metadata
        # We need this to inject into the board module to fix relative imports
        sys.path.insert(0, str(Path.cwd()))
        import __init__ as init_module

        # 3. Manually load board.py to bypass relative import issues
        # The line 'from . import ...' in board.py will fail in a standalone test script.
        # We load the source, remove that line, and inject the variables manually.
        with open('board.py', 'r') as f:
            source = f.read()
        
        # Comment out the relative import line to prevent failure
        source = source.replace('from . import', '# from . import')
        
        # Create a new module for board
        board_module = types.ModuleType('board')
        
        # Inject the metadata variables that would have been imported
        board_module.__version__ = init_module.__version__
        board_module.__description__ = init_module.__description__
        board_module.__board_name__ = init_module.__board_name__
        board_module.__file__ = str(Path.cwd() / 'board.py') # Needed for path resolution
        
        # Execute the modified source code in this new module context
        exec(source, board_module.__dict__)
        
        # 4. Instantiate the class
        DadJokesBoard = board_module.DadJokesBoard
        
        # Mock arguments
        mock_data = Mock()
        mock_data.config.layout.font = Mock()
        mock_data.config.layout.font.getlength = lambda x: len(x) * 6
        
        mock_matrix = Mock()
        mock_matrix.clear = Mock()
        
        mock_sleep = Mock()
        mock_sleep.is_set = Mock(return_value=False)
        
        board = DadJokesBoard(mock_data, mock_matrix, mock_sleep)
        
        print_test("Board instantiation", True, f"Class: {board.__class__.__name__}")
        print_test("Board metadata", True, f"Version: {board.board_version}")
        
        # Test configuration loading
        if hasattr(board, 'text_color'):
            print_test("Configuration loading", True, f"text_color: {board.text_color}")
        
        # Test API methods exist
        if hasattr(board, '_fetch_joke'):
            print_test("API methods", True)
            
        return True
        
    except ImportError as e:
        print_test("Board class import", False, f"Import error: {e}")
        return False
    except Exception as e:
        print_test("Board class", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functionality():
    """Test joke caching functionality."""
    print(f"\n{Colors.BOLD}Testing Cache Functionality...{Colors.END}")
    
    try:
        cache_file = Path("jokes_cache.json")
        
        # Create test cache
        test_cache = {
            "joke": "This is a test joke!",
            "last_fetch": datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(test_cache, f)
        
        print_test("Cache file creation", True)
        
        # Read it back
        with open(cache_file, 'r') as f:
            loaded = json.load(f)
        
        if loaded.get('joke') == test_cache['joke']:
            print_test("Cache read/write", True)
        else:
            print_test("Cache read/write", False, "Data mismatch")
        
        # Clean up test cache
        if cache_file.exists():
            cache_file.unlink()
        
        return True
        
    except Exception as e:
        print_test("Cache functionality", False, str(e))
        return False

def run_all_tests():
    """Run all tests and report results."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Dad Jokes Plugin Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    tests = [
        ("Plugin Metadata", test_plugin_metadata),
        ("Configuration Files", test_config_files),
        ("Layout Files", test_layout_files),
        ("API Connection", test_api_connection),
        ("Board Class", test_board_class),
        ("Cache Functionality", test_cache_functionality),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n{Colors.RED}Unexpected error in {name}: {e}{Colors.END}")
            results.append((name, False))
            
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {status} - {name}")
        
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All tests passed! Plugin is ready to deploy.{Colors.END}\n")
        return True
    else:
        print(f"{Colors.YELLOW}⚠ Some tests failed. Review and fix issues before deploying.{Colors.END}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
