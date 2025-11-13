"""
Dad Jokes Board Plugin

Displays random dad jokes from icanhazdadjoke.com API.
Fetches a new joke every hour and displays it on the LED matrix.
"""
import json
from pathlib import Path

# Load plugin metadata from plugin.json
_plugin_dir = Path(__file__).parent
with open(_plugin_dir / "plugin.json") as f:
    _metadata = json.load(f)

# Expose metadata as module variables (backward compatibility)
__plugin_id__ = _metadata["name"]
__version__ = _metadata["version"]
__description__ = _metadata["description"]
# FIX: __board_name__ should be the "name" (ID), not the "description"
__board_name__ = _metadata["name"]
__author__ = _metadata.get("author", "")
__requirements__ = _metadata.get("requirements", {}).get("python_dependencies", [])
__min_app_version__ = _metadata.get("requirements", {}).get("app_version", "")
__preserve_files__ = _metadata.get("preserve_files", [])