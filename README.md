# Dad Jokes Board Plugin

A fun plugin that displays random dad jokes from the [icanhazdadjoke.com](https://icanhazdadjoke.com) API on your NHL LED Scoreboard. Perfect for keeping things light during off-days or between games!

## Features

- 🎭 Fetches random dad jokes from icanhazdadjoke.com API
- ⏰ Automatically refreshes with a new joke every hour (configurable)
- 📜 Scrolls long jokes smoothly across the display
- 💾 Caches jokes locally to reduce API calls
- 🎨 Customizable text color and display timing
- 📱 Responsive layouts for both 64x32 and 128x64 displays
- 🔄 Graceful fallback if API is unavailable

## Installation

### 1. Copy Plugin Files

Copy the entire `dad_jokes` folder to your plugins directory:

```bash
cd /path/to/nhl-led-scoreboard/src/boards/plugins/
# Upload all dad_jokes files here
```

### 2. Create Configuration

```bash
cd dad_jokes
cp config.sample.json config.json
nano config.json
```

### 3. Configure Settings

Edit `config.json` with your preferences:

|Option                  |Type   |Default |Description                              |
|------------------------|-------|--------|-----------------------------------------|
|`text_color`            |String |“yellow”|Color of the joke text                   |
|`display_seconds`       |Integer|10      |Seconds to display if joke fits on screen|
|`scroll_speed`          |Float  |0.05    |Speed of scrolling (lower = slower)      |
|`refresh_interval_hours`|Integer|1       |Hours between fetching new jokes         |
|`show_header`           |Boolean|true    |Show “DAD JOKE” header                   |
|`enabled`               |Boolean|true    |Enable/disable the board                 |

### 4. Add to Board Rotation

Edit your main `config/config.json` to include the dad jokes board:

```json
"states": {
    "off_day": [
        "dad_jokes",
        "clock",
        "scoreticker"
    ],
    "nhl": [
        "nhl_board",
        "dad_jokes",
        "clock"
    ]
}
```

### 5. Restart Scoreboard

```bash
sudo systemctl restart nhl-scoreboard
```

## How It Works

### API Integration

The plugin uses the free [icanhazdadjoke.com](https://icanhazdadjoke.com) API which:

- Requires no API key
- Has no rate limits for reasonable use
- Returns random jokes in JSON format
- Is free for non-commercial use

### Caching System

To be respectful of the API and ensure reliability:

- Jokes are cached in `jokes_cache.json`
- A new joke is fetched only after the configured interval (default: 1 hour)
- If the API is unavailable, the cached joke is displayed
- Fallback joke is used if no cache exists and API fails

### Display Behavior

**Short jokes** (fit on screen):

- Display centered on the screen
- Show for the configured duration (default: 10 seconds)

**Long jokes** (don’t fit):

- Scroll from right to left across the display
- Scroll speed is configurable
- Header remains static while joke scrolls

## Configuration Examples

### Quick Rotation (New Joke Every 15 Minutes)

```json
{
  "refresh_interval_hours": 0.25,
  "display_seconds": 5,
  "text_color": "cyan"
}
```

### Slow Scroll for Readability

```json
{
  "scroll_speed": 0.1,
  "text_color": "white",
  "show_header": true
}
```

### Minimal Display

```json
{
  "show_header": false,
  "text_color": "yellow",
  "display_seconds": 15
}
```

## Troubleshooting

### Jokes Not Updating

**Check the cache file:**

```bash
cat jokes_cache.json
```

The file shows when the last joke was fetched. Delete it to force a refresh:

```bash
rm jokes_cache.json
```

### API Connection Issues

Check the logs:

```bash
journalctl -u nhl-scoreboard -f | grep "Dad Jokes"
```

If you see connection errors, the plugin will use cached or fallback jokes.

### Text Not Scrolling

- Verify `scroll_speed` is set (try 0.05)
- Check that your display width is correctly configured
- Long jokes should automatically scroll

### No Jokes Displaying

1. Verify plugin is enabled in config
1. Check that `dad_jokes` is in your board rotation
1. Look for errors in the logs
1. Try restarting the scoreboard

## API Rate Limiting

The plugin is designed to be respectful of the icanhazdadjoke.com API:

- Default: 1 joke per hour = 24 API calls per day
- Cached jokes reduce actual API calls
- No API key required
- Free for non-commercial use

If you want to fetch jokes more frequently, adjust `refresh_interval_hours`, but please be respectful of the free service.

## Credits

- Jokes provided by [icanhazdadjoke.com](https://icanhazdadjoke.com)
- Plugin created for [NHL LED Scoreboard](https://github.com/falkyre/nhl-led-scoreboard)

## License

This plugin follows the same license as the NHL LED Scoreboard project.

## Support

For issues or questions:

1. Check the [main plugin documentation](../../../../../PLUGINS.md)
1. Review the logs for error messages
1. Open an issue on GitHub with:
- Your config.json (remove sensitive info)
- Relevant log output
- Display size and scoreboard version

-----

**Enjoy the laughs! 🎭**
