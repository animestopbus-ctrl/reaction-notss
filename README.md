# 🚀 LastPerson07 Auto Reaction Bot

Production-ready Telegram bot that automatically adds emoji reactions to messages in groups & channels.

## ✨ Features

- ✅ Auto-reacts with verified Telegram emojis
- ✅ Per-chat configuration
- ✅ Random/Fixed emoji modes
- ✅ Anti-flood delays (0-60s)
- ✅ Modern anime UI
- ✅ MongoDB storage
- ✅ FastAPI health checks
- ✅ Docker support
- ✅ Full admin panel

## 🚀 Quick Start (Docker)

```bash
# Clone & setup
git clone <repo>
cd LastPerson07
cp .env.example .env
# Edit .env with your credentials

# Run with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

🔧 Local Development
bash
pip install -r requirements.txt
cp .env.example .env

# Edit .env

python main.py
📱 Bot Commands
text
Admin:
/addemoji 👍 ❤️
/removeemoji 👍
/listemoji
/setdelay 3
/random on

Owner:
/ban -1001234567890
/stats
/logs
/broadcast
🐳 Docker Deploy (VPS/Render/Railway)
VPS: docker-compose up -d

Render: Connect GitHub → Docker → Add env vars

Railway: railway up with env vars

UptimeRobot: Monitor /health endpoint (HTTP GET, 5min interval)

🔐 Environment Variables
text
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URL=your_mongo_url
OWNER_ID=your_user_id
LOG_CHANNEL=-100xxxxxxxxxx
BOT_USERNAME=yourbotusername
👨‍💻 Credits
Developer: @MrDhanpalSharma
Community: @THEUPDATEDGUYS

Powered by The Updated Guys 🦾

text

### `Procfile` (for Heroku/Render/Railway)

web: uvicorn main:app --host=0.0.0.0 --port=$PORT

text

## 🚀 Deployment Instructions

### 1. **Local Run**

```bash
git clone <your-repo>
cd LastPerson07
cp .env.example .env
# Fill .env with your Telegram API credentials
pip install -r requirements.txt
mkdir logs
python main.py
2. Docker Local
bash
docker-compose up -d
curl localhost:8000/health  # Should return {"status": "healthy"}
3. VPS Deployment
bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy
git clone <repo>
cd LastPerson07
cp .env.example .env  # Edit env
docker-compose up -d
4. Railway/Render
Push to GitHub

Connect repo

Add all .env variables

Deploy (Docker auto-detected)

5. UptimeRobot Setup
text
Monitor Type: HTTP(s)
URL: https://your-domain.com/health
Interval: 5 minutes
```
