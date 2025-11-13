"""
Dad Jokes Board implementation.
"""
from boards.base_board import BoardBase
from . import __version__, __description__, __board_name__
import logging
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

debug = logging.getLogger("scoreboard")

class DadJokesBoard(BoardBase):
    """
    Displays dad jokes from icanhazdadjoke.com API.
    Fetches a new joke every hour and scrolls it across the display.
    """

    def __init__(self, data, matrix, sleepEvent):
        super().__init__(data, matrix, sleepEvent)

        # Board metadata
        self.board_name = __board_name__
        self.board_version = __version__
        self.board_description = __description__

        # Configuration with defaults
        self.text_color = self.board_config.get("text_color", "yellow")
        self.display_seconds = self.board_config.get("display_seconds", 10)
        self.scroll_speed = self.board_config.get("scroll_speed", 0.05)
        self.refresh_interval_hours = self.board_config.get("refresh_interval_hours", 1)
        self.show_header = self.board_config.get("show_header", True)
        
        # API configuration
        self.api_url = "https://icanhazdadjoke.com/"
        self.cache_file = Path(__file__).parent / "jokes_cache.json"
        
        # Initialize joke data
        self.current_joke = None
        self.last_fetch_time = None
        
        # Load cached joke if available
        self._load_cache()
        
        debug.info(f"Dad Jokes Board initialized (v{self.board_version}) - Name: {self.board_name}")

    def _load_cache(self):
        """Load cached joke from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    self.current_joke = cache.get('joke')
                    last_fetch_str = cache.get('last_fetch')
                    if last_fetch_str:
                        self.last_fetch_time = datetime.fromisoformat(last_fetch_str)
                    debug.debug("Loaded cached joke")
        except Exception as e:
            debug.error(f"Error loading joke cache: {e}")
            self.current_joke = None
            self.last_fetch_time = None

    def _save_cache(self):
        """Save current joke to cache file."""
        try:
            cache = {
                'joke': self.current_joke,
                'last_fetch': self.last_fetch_time.isoformat() if self.last_fetch_time else None
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            debug.debug("Saved joke to cache")
        except Exception as e:
            debug.error(f"Error saving joke cache: {e}")

    def _should_fetch_new_joke(self):
        """Check if we should fetch a new joke based on time interval."""
        if not self.current_joke or not self.last_fetch_time:
            return True
        
        time_since_last_fetch = datetime.now() - self.last_fetch_time
        should_fetch = time_since_last_fetch >= timedelta(hours=self.refresh_interval_hours)
        
        if should_fetch:
            debug.info(f"Time to fetch new joke (last fetch: {time_since_last_fetch.total_seconds()/3600:.1f}h ago)")
        
        return should_fetch

    def _fetch_joke(self):
        """Fetch a new joke from the API."""
        try:
            debug.info("Fetching new dad joke from API...")
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'NHL LED Scoreboard Dad Jokes Plugin (https://github.com/falkyre/nhl-led-scoreboard)'
            }
            
            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.current_joke = data.get('joke', 'No joke available')
            self.last_fetch_time = datetime.now()
            
            self._save_cache()
            
            debug.info(f"Successfully fetched joke: {self.current_joke[:50]}...")
            return True
            
        except requests.exceptions.RequestException as e:
            debug.error(f"Failed to fetch joke from API: {e}")
            if not self.current_joke:
                self.current_joke = "Why don't scientists trust atoms? Because they make up everything!"
                debug.info("Using fallback joke")
            return False
        except Exception as e:
            debug.error(f"Unexpected error fetching joke: {e}")
            if not self.current_joke:
                self.current_joke = "Error loading joke. Try again later!"
            return False

    def _get_text_width(self, text, font):
        """Calculate the width of text in pixels."""
        try:
            # Try to get text dimensions from the font
            return font.getlength(text)
        except:
            # Fallback: estimate based on character count
            return len(text) * 6

    def render(self):
        """
        Render the dad joke on the display.
        """
        # Check if we need a new joke
        if self._should_fetch_new_joke():
            self._fetch_joke()
        
        # Ensure we have a joke
        if not self.current_joke:
            self._fetch_joke()
        
        if not self.current_joke:
            debug.error("No joke available to display")
            return
        
        self.matrix.clear()
        
        # Get layout
        layout = self.get_board_layout('dad_jokes')
        
        # Prepare text
        if self.show_header:
            header = "DAD JOKE"
            joke_text = self.current_joke
        else:
            header = None
            joke_text = self.current_joke
        
        # Get font
        font = self.data.config.layout.font
        
        # Calculate if text needs scrolling
        text_width = self._get_text_width(joke_text, font)
        needs_scroll = text_width > self.display_width
        
        joke_y_start = 8 # Default Y position if no header and no layout

        if layout and 'header' in layout and header:
            # Draw header using layout
            self.matrix.draw_text_layout(layout['header'], header, fillColor='white')
            
            # Get joke Y-position from layout, with fallback
            if 'joke' in layout and layout['joke'] and 'position' in layout['joke']:
                try:
                    joke_y_start = layout['joke']['position'][1]
                except (TypeError, IndexError):
                    joke_y_start = 12 # Fallback if position is malformed
            else:
                joke_y_start = 12 # Fallback if no joke layout
        
        elif header: # Fallback header positioning (no layout)
            self.matrix.draw_text_centered(2, header, font, 'white')
            joke_y_start = 12
        
        elif layout and 'joke' in layout and layout['joke'] and 'position' in layout['joke']:
             # No header, but layout has joke position
             try:
                joke_y_start = layout['joke']['position'][1]
             except (TypeError, IndexError):
                joke_y_start = 8 # Fallback if position is malformed
        
        if needs_scroll:
            # Scroll the joke text
            self._scroll_text(joke_text, joke_y_start, font)
        else:
            # Static display - center the text
            if layout and 'joke' in layout and layout['joke']:
                self.matrix.draw_text_layout(layout['joke'], joke_text, fillColor=self.text_color)
            else:
                self.matrix.draw_text_centered(joke_y_start, joke_text, font, self.text_color)
            
            self.matrix.render()
            self.sleepEvent.wait(self.display_seconds)

    def _scroll_text(self, text, y_position, font):
        """Scroll text across the display."""
        text_width = self._get_text_width(text, font)
        
        # Start position (right side of screen)
        x_position = self.display_width
        
        # Scroll until text is completely off the left side
        while x_position > -text_width:
            if self.sleepEvent.is_set():
                break
            
            self.matrix.clear()
            
            # Redraw header if enabled
            if self.show_header:
                header_layout = self.get_board_layout('dad_jokes')
                if header_layout and 'header' in header_layout:
                    self.matrix.draw_text_layout(header_layout['header'], "DAD JOKE", fillColor='white')
                else:
                    self.matrix.draw_text_centered(2, "DAD JOKE", font, 'white')
            
            # Draw scrolling text
            self.matrix.draw_text((int(x_position), y_position), text, font, self.text_color)
            self.matrix.render()
            
            # Move text left
            x_position -= 1
            
            # Sleep for smooth scrolling
            self.sleepEvent.wait(self.scroll_speed)
