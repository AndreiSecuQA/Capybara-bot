# 🚀 Deploy Capybara Bot on Railway

## Prerequisites
- GitHub account with the repo
- Railway account (free at railway.app)
- Telegram Bot Token (from @BotFather)
- Google Gemini API Key (free at https://aistudio.google.com/app/apikey)

## Steps

### 1. Create Railway account
Go to [railway.app](https://railway.app) and sign up with your GitHub account.

### 2. Create new project
- Click **"New Project"**
- Select **"Deploy from GitHub repo"**
- Choose **AndreiSecuQA/Capybara-bot**
- Railway will detect the Dockerfile automatically

### 3. Add environment variables
In Railway dashboard → your service → **Variables** tab, add:
```
TELEGRAM_TOKEN=8630601890:AAGcL-2ey6PbNBB8E_hraHei20SKEwfuWAs
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
TIMEZONE=Europe/Bucharest
```

### 4. Add persistent volume (for database)
- Go to your service → **Volumes** tab
- Click **"Add Volume"**
- Mount path: `/data`
- This ensures your database survives redeploys

### 5. Deploy
- Click **"Deploy"** — Railway builds and starts the bot automatically
- Check **Logs** tab to confirm: `🐾 Capybara Bot is running!`

### 6. Auto-deploy on code changes
Every time you push to GitHub, Railway automatically redeploys — zero downtime!

## Monitoring
- **Logs**: Railway dashboard → Logs tab (real-time)
- **Metrics**: CPU/RAM usage visible in dashboard
- **Restarts**: Automatic on failure (configured in railway.toml)

## Cost
- Free tier: $5 credit/month (enough for a small bot)
- Hobby plan: $5/month for always-on service

## 🛠️ Dev Agent Setup

The `/dev` command lets you make code changes directly from Telegram. Claude reads the relevant files, makes the changes, pushes to GitHub, and Railway auto-redeploys.

### Additional Railway Variables needed:
```
ADMIN_TELEGRAM_ID=your_telegram_user_id
ANTHROPIC_API_KEY=your_claude_api_key
GITHUB_TOKEN=your_github_pat
GITHUB_REPO=AndreiSecuQA/Capybara-bot
```

### How to get each:
- **ADMIN_TELEGRAM_ID**: Message @userinfobot on Telegram, copy your user ID
- **ANTHROPIC_API_KEY**: Create key at https://console.anthropic.com
- **GITHUB_TOKEN**: Create at https://github.com/settings/tokens (needs `repo` scope)

### Usage:
- `/dev add a /weight command to update current weight`
- `/dev change the gym reminder time to 20:30`
- `/dev add calorie goal progress to the daily summary`

Claude will autonomously:
1. Read the relevant files from the repo
2. Understand the current code structure
3. Make the requested changes
4. Commit and push to GitHub
5. Railway redeploys automatically (~2 min)

Only the user with ADMIN_TELEGRAM_ID can use this command.
