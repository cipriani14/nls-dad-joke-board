“””
Dad Jokes Board Plugin

Displays random dad jokes from icanhazdadjoke.com API.
Fetches a new joke every hour and displays it on the LED matrix.
“””
import json
from pathlib import Path

# Load plugin metadata from plugin.json

_plugin_dir = Path(**file**).parent
with open(_plugin_dir / “plugin.json”) as f:
_metadata = json.load(f)

# Expose metadata as module variables (backward compatibility)

**plugin_id** = _metadata[“name”]
**version** = _metadata[“version”]
**description** = _metadata[“description”]
**board_name** = _metadata[“description”]
**author** = _metadata.get(“author”, “”)
**requirements** = _metadata.get(“requirements”, {}).get(“python_dependencies”, [])
**min_app_version** = _metadata.get(“requirements”, {}).get(“app_version”, “”)
**preserve_files** = _metadata.get(“preserve_files”, [])
