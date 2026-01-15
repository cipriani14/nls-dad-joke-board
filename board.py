“””
Dad Jokes Board implementation.
Two-screen presentation: setup then punchline.
“””
from boards.base_board import BoardBase
from rgbmatrix import graphics
import logging
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

debug = logging.getLogger(“scoreboard”)

class DadJokesBoard(BoardBase):
“””
Displays dad jokes from icanhazdadjoke.com API.
Shows setup on first screen, punchline on second screen.
Filters jokes by length to ensure they fit the display.
“””

```
def __init__(self, data, matrix, sleepEvent):
    super().__init__(data, matrix, sleepEvent)

    # Configuration with defaults
    self.text_color = self.board_config.get("text_color", "yellow")
    self.punchline_color = self.board_config.get("punchline_color", "cyan")
    self.setup_display_seconds = self.board_config.get("setup_display_seconds", 4)
    self.punchline_display_seconds = self.board_config.get("punchline_display_seconds", 6)
    self.transition_pause = self.board_config.get("transition_pause", 1)
    self.refresh_interval_hours = self.board_config.get("refresh_interval_hours", 1)
    self.max_joke_length = self.board_config.get("max_joke_length", 120)
    self.show_ellipsis = self.board_config.get("show_ellipsis", True)
    
    # API configuration
    self.api_url = "https://icanhazdadjoke.com/"
    self.cache_file = Path(__file__).parent / "jokes_cache.json"
    
    # Initialize joke data
    self.current_setup = None
    self.current_punchline = None
    self.last_fetch_time = None
    
    # Fallback jokes (short and clean)
    self.fallback_jokes = [
        ("Why don't scientists trust atoms?", "Because they make up everything!"),
        ("What do you call a fake noodle?", "An impasta!"),
        ("Why did the scarecrow win an award?", "Outstanding in his field!"),
        ("What do you call cheese that isn't yours?", "Nacho cheese!"),
        ("Why don't eggs tell jokes?", "They'd crack each other up!"),
    ]
    
    # Load cached joke if available
    self._load_cache()
    
    debug.info(f"Dad Jokes Board initialized (max length: {self.max_joke_length} chars)")

def _load_cache(self):
    """Load cached joke from file."""
    try:
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                self.current_setup = cache.get('setup')
                self.current_punchline = cache.get('punchline')
                last_fetch_str = cache.get('last_fetch')
                if last_fetch_str:
                    self.last_fetch_time = datetime.fromisoformat(last_fetch_str)
                debug.debug("Loaded cached joke")
    except Exception as e:
        debug.error(f"Error loading joke cache: {e}")
        self.current_setup = None
        self.current_punchline = None
        self.last_fetch_time = None

def _save_cache(self):
    """Save current joke to cache file."""
    try:
        cache = {
            'setup': self.current_setup,
            'punchline': self.current_punchline,
            'last_fetch': self.last_fetch_time.isoformat() if self.last_fetch_time else None
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        debug.debug("Saved joke to cache")
    except Exception as e:
        debug.error(f"Error saving joke cache: {e}")

def _should_fetch_new_joke(self):
    """Check if we should fetch a new joke based on time interval."""
    if not self.current_setup or not self.current_punchline or not self.last_fetch_time:
        return True
    
    time_since_last_fetch = datetime.now() - self.last_fetch_time
    return time_since_last_fetch >= timedelta(hours=self.refresh_interval_hours)

def _split_joke(self, joke_text):
    """
    Split a joke into setup and punchline.
    Returns (setup, punchline) tuple or None if can't split well.
    """
    # Common separators that indicate punchline
    separators = ['?', '!']
    
    for sep in separators:
        if sep in joke_text:
            parts = joke_text.split(sep, 1)
            if len(parts) == 2:
                setup = parts[0].strip() + sep
                punchline = parts[1].strip()
                
                # Validate the split makes sense
                # Setup should be at least 10 chars, punchline at least 5
                if len(setup) >= 10 and len(punchline) >= 5:
                    return (setup, punchline)
    
    return None

def _fetch_joke(self):
    """
    Fetch a new joke from the API.
    Keeps trying until we get one that fits our criteria.
    """
    try:
        debug.info("Fetching new dad joke from API...")
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'NHL LED Scoreboard Dad Jokes Plugin'
        }
        
        # Try up to 10 times to get a suitable joke
        for attempt in range(10):
            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            joke_text = data.get('joke', '')
            
            # Check length first
            if len(joke_text) > self.max_joke_length:
                debug.debug(f"Joke too long ({len(joke_text)} chars), fetching another...")
                continue
            
            # Try to split the joke
            result = self._split_joke(joke_text)
            if result:
                self.current_setup, self.current_punchline = result
                self.last_fetch_time = datetime.now()
                self._save_cache()
                
                debug.info(f"Successfully fetched joke (attempt {attempt + 1})")
                debug.debug(f"Setup: {self.current_setup}")
                debug.debug(f"Punchline: {self.current_punchline}")
                return True
            else:
                debug.debug(f"Couldn't split joke well, fetching another...")
                continue
        
        # If we exhausted attempts, use fallback
        debug.warning("Couldn't find suitable joke after 10 attempts, using fallback")
        self._use_fallback_joke()
        return False
        
    except requests.exceptions.RequestException as e:
        debug.error(f"Failed to fetch joke from API: {e}")
        self._use_fallback_joke()
        return False
    except Exception as e:
        debug.error(f"Unexpected error fetching joke: {e}")
        self._use_fallback_joke()
        return False

def _use_fallback_joke(self):
    """Use a random fallback joke."""
    import random
    setup, punchline = random.choice(self.fallback_jokes)
    self.current_setup = setup
    self.current_punchline = punchline
    self.last_fetch_time = datetime.now()
    self._save_cache()
    debug.info("Using fallback joke")

def _wrap_text(self, text, max_chars_per_line):
    """
    Wrap text to fit within max characters per line.
    Returns list of lines.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        # Account for space between words
        space_needed = 1 if current_line else 0
        
        if current_length + space_needed + word_length <= max_chars_per_line:
            current_line.append(word)
            current_length += space_needed + word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def _draw_centered_multiline(self, lines, start_y, font, color):
    """Draw multiple lines of text centered on the display."""
    line_height = 8  # Adjust based on your font size
    current_y = start_y
    
    for line in lines:
        # Use the matrix's built-in text centering if available
        try:
            self.matrix.draw_text_centered(current_y, line, font, color)
        except:
            # Fallback: manual centering with better calculation
            text_width = len(line) * 5  # Adjusted from 6 to 5 for better centering
            x = (self.display_width - text_width) // 2
            self.matrix.draw_text((x, current_y), line, font, color)
        
        current_y += line_height

def render(self):
    """
    Render the dad joke as a two-screen presentation.
    Screen 1: Setup
    Screen 2: Punchline
    """
    # Check if we need a new joke
    if self._should_fetch_new_joke():
        self._fetch_joke()
    
    # Ensure we have a joke
    if not self.current_setup or not self.current_punchline:
        self._fetch_joke()
    
    if not self.current_setup or not self.current_punchline:
        debug.error("No joke available to display")
        return
    
    # Get font
    font = self.data.config.layout.font_small if hasattr(self.data.config.layout, 'font_small') else self.data.config.layout.font
    
    # Determine characters per line based on display width
    # Rough estimate: 6 pixels per character
    max_chars_per_line = self.display_width // 6
    
    # Wrap setup and punchline
    setup_lines = self._wrap_text(self.current_setup, max_chars_per_line)
    punchline_lines = self._wrap_text(self.current_punchline, max_chars_per_line)
    
    # Calculate vertical centering
    setup_line_count = len(setup_lines)
    punchline_line_count = len(punchline_lines)
    line_height = 8
    
    # Add padding to prevent text from going off top of screen
    setup_start_y = max(8, (self.display_height - (setup_line_count * line_height)) // 2)
    punchline_start_y = max(8, (self.display_height - (punchline_line_count * line_height)) // 2)
    
    # SCREEN 1: Show setup
    self.matrix.clear()
    self._draw_centered_multiline(setup_lines, setup_start_y, font, self.text_color)
    self.matrix.render()
    self.sleepEvent.wait(self.setup_display_seconds)
    
    if self.sleepEvent.is_set():
        return
    
    # TRANSITION: Show ellipsis if enabled
    if self.show_ellipsis:
        self.matrix.clear()
        ellipsis = "..."
        text_width = len(ellipsis) * 6
        x = (self.display_width - text_width) // 2
        y = self.display_height // 2
        self.matrix.draw_text((x, y), ellipsis, font, self.text_color)
        self.matrix.render()
        self.sleepEvent.wait(self.transition_pause)
        
        if self.sleepEvent.is_set():
            return
    
    # SCREEN 2: Show punchline
    self.matrix.clear()
    self._draw_centered_multiline(punchline_lines, punchline_start_y, font, self.punchline_color)
    self.matrix.render()
    self.sleepEvent.wait(self.punchline_display_seconds)
```
