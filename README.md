# TradingView Chart Capture Service

A sophisticated web automation service for TradingView chart capture with robust session management and multi-browser support.

## Features

- 🔐 **Auto-login TradingView** with persistent session management
- 📊 **Chart Capture API** - Capture any TradingView chart by symbol or chart ID
- 🌐 **Web Dashboard** - Easy-to-use interface for testing and monitoring
- 🔄 **Session Auto-renewal** - Intelligent cookie management and session validation
- 🎨 **Theme Support** - Dark/Light mode chart captures
- ⚡ **Fast Performance** - Puppeteer-based browser automation

## Tech Stack

- **Backend**: Flask (Python)
- **Automation**: Puppeteer (Node.js)
- **Browser**: Chrome/Chromium
- **Session Storage**: JSON-based cookie management

## API Endpoints

### Chart Capture
```bash
POST /api/capture
{
  "chart_id": "abc123",
  "ticker": "BTCUSDT", 
  "adjustment": 30,
  "interval": "60",
  "theme": "dark"
}
```

### Session Management
```bash
GET /api/session-status    # Check session status
POST /api/refresh-session # Refresh login session
```

## Quick Start

1. **Clone repository**
```bash
git clone <your-repo-url>
cd tradingview-capture
```

2. **Install dependencies**
```bash
pip install flask gunicorn requests selenium urllib3 pillow werkzeug
npm install puppeteer
```

3. **Run locally**
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

4. **Access dashboard**
Open http://localhost:5000

## Deploy to Koyeb (Free)

1. **Push to GitHub**
2. **Connect Koyeb** to your repository
3. **Select Docker** build
4. **Set port** to 5000
5. **Deploy!**

Your service will be live at: `https://your-app.koyeb.app`

## Configuration

The service auto-configures TradingView credentials. For production deployment, you can set environment variables:

- `SESSION_SECRET`: Flask session secret
- `NODE_ENV`: production

## Usage Examples

### Capture Chart by Symbol
```python
import requests

response = requests.post('https://your-app.koyeb.app/api/capture', json={
    'symbol': 'BINANCE:BTCUSDT',
    'theme': 'dark',
    'interval': '1h'
})

chart_path = response.json()['screenshot_path']
```

### Check Service Status
```bash
curl https://your-app.koyeb.app/status
```

## License

MIT License - Feel free to use for personal or commercial projects.

---

⚡ **Ready for production deployment with 24/7 uptime on Koyeb free tier!**