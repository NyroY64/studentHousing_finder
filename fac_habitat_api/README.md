# Fac Habitat API Scraper

A comprehensive toolkit for reverse engineering and scraping the Fac Habitat student housing API.

## Features

- 🔍 **API Exploration** - Tools to discover and analyze API endpoints
- ⚡ **Async Scraping** - High-performance concurrent data collection
- 📊 **Data Analysis** - Understand the data structure and patterns
- 📧 **Email Notifications** - Get alerts for new available residences
- 💾 **Database Tracking** - SQLite database to track discovered residences

## Files

### Main Scrapers
- **`main.py`** - Original synchronous scraper with enhanced debugging
- **`async_scraper.py`** - Fast async version using aiohttp (10x faster)

### Analysis Tools
- **`api_explorer.py`** - Discovers API endpoints and patterns
- **`data_analyzer.py`** - Analyzes the residence data structure

### Configuration
- **`config.py`** - Configuration (BASE_URL, departments to search)
- **`requirements.txt`** - Python dependencies

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Explore the API
Run the API explorer to discover endpoints:
```bash
python api_explorer.py
```

### 3. Analyze the Data
Understand what data is available:
```bash
python data_analyzer.py
```

### 4. Run the Scraper
Choose between sync or async version:

**Synchronous (with debug logging):**
```bash
DEBUG=1 python main.py
```

**Asynchronous (faster):**
```bash
python async_scraper.py
```

## Configuration

Edit `config.py` to customize:

```python
BASE_URL = "https://www.fac-habitat.com"
DEPARTMENTS = ['75', '91', '92', '93', '94', '95']  # Paris and surrounding areas
```

## Email Notifications

Set environment variables for email alerts:

```bash
export EMAIL_ADDRESS="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export RECIPIENT_ADDRESS="recipient@email.com"  # Optional, defaults to EMAIL_ADDRESS
```

**Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

## Debug Mode

Enable detailed logging:
```bash
export DEBUG=1
python main.py
```

This will:
- Show DEBUG level logs
- Log iframe URLs for pattern analysis
- Capture script tags that might contain API calls
- Show availability text for each residence

## API Endpoints Discovered

### Main Endpoint
- `GET /fr/residences/json` - Returns all residences with metadata

### Residence Pages
- `/fr/residences-etudiantes/id-{residence_id}-{slugified-title}`

### Availability (via iframe)
- Embedded in reservation iframe on each residence page
- Look for `<span id="avail_area_0">` for availability text

## Data Fields

Each residence in the JSON includes:
- `titre_fr` - Residence name
- `adresse` - Street address
- `ville` - City
- `cp` - Postal code
- `gestionnaire` - Property manager
- `telephone` - Phone number
- `email` - Contact email
- `latitude`, `longitude` - GPS coordinates
- ... and more (run `data_analyzer.py` to see all fields)

## Performance Comparison

| Scraper | Speed | Use Case |
|---------|-------|----------|
| `main.py` | ~2-3 residences/second | Debugging, detailed logging |
| `async_scraper.py` | ~20-30 residences/second | Production, fast scanning |

## Output Files

- **`available_residences.json`** - List of available residences
- **`simplified_residences.json`** - All residences with key fields only
- **`residences.db`** - SQLite database tracking seen residences
- **`scraper.log`** / **`async_scraper.log`** - Execution logs

## Tips for API Reverse Engineering

1. **Network Tab:** Open browser DevTools → Network tab while browsing the site
2. **Look for XHR/Fetch:** Filter for API calls to find hidden endpoints
3. **Check Headers:** Some APIs require specific headers or cookies
4. **Rate Limiting:** Be respectful - add delays if you notice rate limits
5. **Legal:** Ensure your scraping complies with the site's ToS and robots.txt

## Filtering Residences

The scraper automatically:
- ✅ Filters by department codes (postal code prefixes)
- ✅ Skips Logifac residences (if configured)
- ✅ Only alerts for NEW available residences (using SQLite tracking)

## Troubleshooting

**No residences found:**
- Check if the website structure has changed
- Run `api_explorer.py` to verify endpoints still work
- Enable DEBUG mode to see detailed logs

**Email not sending:**
- Verify environment variables are set
- For Gmail, ensure you're using an App Password
- Check firewall/network allows SMTP port 465

**Slow performance:**
- Use `async_scraper.py` for faster execution
- Reduce the number of departments in config
- Adjust the connection limit in async_scraper (default: 10)

## License

For educational and personal use. Respect the website's terms of service.
