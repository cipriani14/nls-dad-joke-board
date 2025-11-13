# Dad Jokes Plugin - Complete Project Summary

## 📋 Project Overview

A plugin for the NHL LED Scoreboard that displays random dad jokes from icanhazdadjoke.com API. Jokes refresh every hour and scroll smoothly across LED matrix displays.

## 📁 File Structure

```
dad_jokes/
├── .gitignore              # Git ignore rules
├── plugin.json             # Plugin metadata (REQUIRED)
├── __init__.py             # Module initialization
├── board.py                # Main board implementation
├── config.sample.json      # Configuration template
├── layout_64x32.json       # Layout for 64x32 displays
├── layout_128x64.json      # Layout for 128x64 displays
├── README.md               # User documentation
├── DEPLOYMENT.md           # Deployment guide
├── test_dad_jokes.py       # Test suite
└── PROJECT_SUMMARY.md      # This file
```

## 🎯 Key Features

✅ **API Integration**

- Fetches jokes from free icanhazdadjoke.com API
- No API key required
- Respectful rate limiting (1 joke/hour default)

✅ **Smart Caching**

- Caches jokes locally in `jokes_cache.json`
- Reduces API calls
- Works offline with cached jokes

✅ **Responsive Display**

- Short jokes display centered
- Long jokes scroll smoothly
- Configurable scroll speed
- Works on 64x32 and 128x64 displays

✅ **Robust Error Handling**

- Graceful API failure handling
- Fallback joke if API unavailable
- Cached joke used when offline

✅ **Customizable**

- Text color options
- Display duration settings
- Scroll speed control
- Optional header display

## 🔧 Configuration Options

|Option                  |Type   |Default |Description                     |
|------------------------|-------|--------|--------------------------------|
|`text_color`            |String |“yellow”|Color of joke text              |
|`display_seconds`       |Integer|10      |Display duration for short jokes|
|`scroll_speed`          |Float  |0.05    |Scroll speed (lower = slower)   |
|`refresh_interval_hours`|Integer|1       |Hours between new jokes         |
|`show_header`           |Boolean|true    |Show “DAD JOKE” header          |
|`enabled`               |Boolean|true    |Enable/disable board            |

## 🚀 Quick Start

### 1. Upload Files to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Dad Jokes plugin"
git remote add origin https://github.com/cipriani14/nhl-scoreboard-dad-jokes.git
git push -u origin main
```

### 2. Test Before Deploying

```bash
cd dad_jokes/
python3 test_dad_jokes.py
```

### 3. Deploy to Scoreboard

```bash
# On your Pi
cd /home/pi/nhl-led-scoreboard/src/boards/plugins/
git clone https://github.com/cipriani14/nhl-scoreboard-dad-jokes.git dad_jokes
cd dad_jokes
cp config.sample.json config.json
nano config.json  # Edit settings
```

### 4. Add to Board Rotation

Edit `/home/pi/nhl-led-scoreboard/config/config.json`:

```json
{
  "states": {
    "off_day": [
      "dad_jokes",
      "clock",
      "scoreticker"
    ]
  }
}
```

### 5. Restart Scoreboard

```bash
sudo systemctl restart nhl-scoreboard
```

## 🧪 Testing Strategy

The included test suite (`test_dad_jokes.py`) validates:

1. **Plugin Metadata** - Validates plugin.json structure
1. **Configuration Files** - Checks config.sample.json
1. **Layout Files** - Validates layout JSON files
1. **API Connection** - Tests live API connectivity
1. **Board Class** - Verifies class can instantiate
1. **Cache Functionality** - Tests read/write operations

Run tests with:

```bash
python3 test_dad_jokes.py
```

Expected output:

```
✓ PASS | Plugin Metadata
✓ PASS | Configuration Files
✓ PASS | Layout Files
✓ PASS | API Connection
✓ PASS | Board Class
✓ PASS | Cache Functionality

Results: 6/6 tests passed
✓ All tests passed! Plugin is ready to deploy.
```

## 🐛 Common Issues & Solutions

### Issue: Plugin Not Loading

**Solution:**

```bash
# Check file permissions
chmod 644 /path/to/dad_jokes/*
chmod 755 /path/to/dad_jokes/

# Verify Python syntax
python3 -m py_compile board.py
```

### Issue: No Jokes Displaying

**Solution:**

```bash
# Check if plugin is enabled
cat config.json

# Force refresh
rm jokes_cache.json
sudo systemctl restart nhl-scoreboard
```

### Issue: API Connection Failed

**Solution:**

```bash
# Test API manually
curl -H "Accept: application/json" https://icanhazdadjoke.com/

# Check connectivity
ping icanhazdadjoke.com
```

## 📊 Code Architecture

### Class Hierarchy

```
BoardBase (from scoreboard)
    ↓
DadJokesBoard
    ├── __init__()          # Initialize configuration
    ├── render()            # Main display logic
    ├── _fetch_joke()       # API interaction
    ├── _load_cache()       # Load cached joke
    ├── _save_cache()       # Save joke to cache
    ├── _should_fetch_new_joke()  # Check if refresh needed
    └── _scroll_text()      # Scroll long jokes
```

### Data Flow

```
Scoreboard Startup
    ↓
Load plugin.json → Initialize DadJokesBoard
    ↓
Load config.json → Apply user settings
    ↓
Load jokes_cache.json (if exists)
    ↓
render() called by scoreboard
    ↓
Check if new joke needed → Fetch from API (if needed)
    ↓
Display joke (centered or scrolling)
    ↓
Cache joke for next display
```

## 🔄 Update Process

When you make changes:

1. **Update version** in `plugin.json`
1. **Test locally** with `test_dad_jokes.py`
1. **Commit and push** to GitHub
1. **Users update** with:
   
   ```bash
   cd /path/to/dad_jokes
   git pull
   sudo systemctl restart nhl-scoreboard
   ```

## 📦 Dependencies

- **Python:** ≥3.7
- **Required packages:** requests≥2.28.0
- **Scoreboard version:** ≥2025.9.0

Install dependencies:

```bash
pip3 install requests
```

## 🌐 API Information

**Endpoint:** https://icanhazdadjoke.com/

**Request:**

```bash
curl -H "Accept: application/json" https://icanhazdadjoke.com/
```

**Response:**

```json
{
  "id": "R7UfaahVfFd",
  "joke": "Why did the scarecrow win an award? Because he was outstanding in his field.",
  "status": 200
}
```

**Rate Limits:** No official limit, but be respectful (plugin defaults to 1/hour)

## 📝 License

This plugin follows the same license as the NHL LED Scoreboard project.

## 🤝 Contributing

Improvements welcome! Consider:

- Additional joke sources
- Joke categories/filtering
- Multi-language support
- Joke rating system
- Custom joke lists

## 📞 Support

For issues:

1. Check logs: `journalctl -u nhl-scoreboard -f`
1. Run test suite: `python3 test_dad_jokes.py`
1. Review this documentation
1. Open GitHub issue with:
- Log output
- Configuration file
- Test results

## 🎓 Learning Resources

- [NHL LED Scoreboard Docs](https://github.com/falkyre/nhl-led-scoreboard)
- [Plugin Development Guide](README.md#plugin-development-guide)
- [icanhazdadjoke API](https://icanhazdadjoke.com/api)

-----

**Version:** 1.0.0  
**Author:** Your Name  
**Last Updated:** 2025-11-13  
**Status:** Production Ready ✅
