# Bluesky Game Challenge Analyzer

Tool to analyze Bluesky posts containing #GameChallenge hashtag, extract game titles, and analyze trends.

## Project Structure

## Dependencies Setup

### System Requirements
```bash
# Update system
sudo apt update
sudo apt upgrade

# Install Python and requirements
sudo apt install python3-pip python3-venv
```

### Python Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install atproto
pip install pandas
pip install python-dateutil
pip install pytz
pip install requests
pip install matplotlib seaborn
```

### Ollama Setup (Optional - for game title extraction)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
systemctl start ollama

# Pull Mistral model
ollama pull mistral
```

### Configuration
1. Create data directory:
```bash
mkdir data
```
2. Set up Bluesky credentials in get_bsky_posts.py:
```bash
client.login('your-handle.bsky.social', 'your-password')
```

### Usage
1. Collect posts:
```bash
python3 get_bsky_posts.py
```
2. Analyze game titles (requires Ollama):
```bash
python3 extractgames.py
```

### Data Files
- posts_gamechallenge_YYYYMMDD.json: Daily post data
- unmatched_posts.txt: Posts without identified game titles
- TextDump_GameOnly.txt: Reference game titles list (required)

### Features
- Fetches posts with #GameChallenge hashtag
- Extracts game titles using local LLM
- Saves structured data in JSON/CSV
- Handles rate limiting for API calls
- Tracks unmatched posts for review
### Notes
- API calls are rate-limited (15s delay)
- Requires Bluesky account
- Game title extraction requires Ollama running locally
