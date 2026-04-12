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
