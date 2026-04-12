# Capybara Bot 🐾

A production-ready Telegram bot for fitness tracking, nutrition analysis, and personal health management. Capybara Bot helps you monitor your workouts, track your calories, and achieve your fitness goals.

## Features

### 🏋️ Workout Tracking
- Log gym exercises with sets, reps, and weight
- Track session duration and estimated calories burned
- View session summaries with total volume lifted
- Multiple languages support (English, Romanian, Russian)

### 📸 Food Photo Analysis
- Upload food photos for AI-powered nutrition analysis
- Automatic calorie and macro estimation using Claude Vision
- Manual editing of analyzed values
- Daily meal logging and tracking

### 📊 Progress Dashboard
- Real-time daily progress visualization
- Track calories consumed vs. target
- Monitor protein, carbs, and fat intake
- Water intake tracking
- AI-generated personalized tips based on your data

### ⚙️ Personalized Onboarding
- 15-step interactive onboarding flow
- BMI calculation and interpretation
- Automatic daily calorie target calculation using Mifflin-St Jeor formula
- Macro distribution based on your fitness goal
- Support for 5 fitness goals and 3 fitness levels
- 5 diet preference options

### 📈 Statistics & Analytics
- Weekly statistics summary
- Average daily calories and macros
- Workout frequency and volume tracking
- Hydration monitoring
- Comprehensive health dashboard

### 🌍 Multilingual Support
- English (en)
- Romanian (ro)
- Russian (ru)

## Architecture

```
Capybara-bot/
├── main.py                 # Bot entry point
├── config.py              # Configuration and environment variables
├── database.py            # SQLite database functions and models
├── i18n.py               # Translation strings for 3 languages
├── bot/
│   ├── __init__.py
│   ├── onboarding.py     # 15-step user setup flow
│   ├── workout.py        # Gym session conversation handler
│   ├── food.py           # Food photo analysis handler
│   ├── progress.py       # Daily progress dashboard
│   ├── ai_engine.py      # Claude Vision & API integration
│   ├── keyboards.py      # All UI keyboard definitions
│   └── handlers.py       # Command and message handlers
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Telegram Bot Token (get from @BotFather)
- Anthropic API Key (from Anthropic dashboard)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AndreiSecuQA/Capybara-bot.git
cd Capybara-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Configure your tokens in `.env`:
```
TELEGRAM_TOKEN=your_bot_token_from_botfather
ANTHROPIC_API_KEY=your_api_key_from_anthropic
DATABASE_PATH=capybara.db
TIMEZONE=Europe/Bucharest
```

6. Run the bot:
```bash
python main.py
```

The bot will now be running and listening for updates from Telegram!

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize or resume user profile |
| `/help` | Show available commands |
| `/gym` | Start a new gym session |
| `/progress` | View today's progress dashboard |
| `/stats` | Show weekly statistics |
| `/settings` | View your profile settings |

## Menu Buttons

After onboarding, you'll see these main menu buttons:

- 🏋️ **Go to Gym** - Start logging a workout session
- 📸 **Log Food** - Upload a food photo for analysis
- 📊 **My Progress** - View today's daily dashboard
- 📈 **Stats** - View weekly statistics
- ⚙️ **Settings** - View your profile information

## Onboarding Flow

The bot guides new users through a 15-step setup:

1. **Language Selection** - Choose between English, Romanian, Russian
2. **Name** - Enter your name
3. **Gender** - Male or Female
4. **Age** - Validate between 10-100
5. **Height** - In cm (100-250)
6. **Weight** - In kg (30-300)
7. **Goal** - Weight loss, muscle gain, maintain, endurance, or fitness
8. **Gym Frequency** - Days per week (1-7)
9. **Gym Duration** - Typical session length (30-120 min)
10. **Fitness Level** - Beginner, Intermediate, Advanced
11. **Diet Preference** - None, Vegetarian, Vegan, Keto, Halal
12. **Wake Time** - In HH:MM format
13. **Sleep Time** - In HH:MM format
14. **Water Goal** - Daily glasses (6-12)
15. **Health Conditions** - Free text or 'none'

After completion, the bot calculates:
- BMI and BMI category
- Daily calorie target using Mifflin-St Jeor formula
- Macro distribution based on your goal

## Database Schema

The bot uses SQLite with 5 main tables:

- **users** - User profiles and settings
- **gym_sessions** - Workout sessions
- **exercises** - Individual exercises logged
- **food_logs** - Meal logs with nutrition info
- **daily_summary** - Aggregated daily data

## Calorie & Macro Calculation

### Calorie Target Formula (Mifflin-St Jeor)
- **BMR** = 10×weight + 6.25×height - 5×age + 5 (males)
- **TDEE** = BMR × Activity Multiplier
- Activity multipliers:
  - 1-2 days/week: 1.375
  - 3-4 days/week: 1.55
  - 5-7 days/week: 1.725
- Goal adjustment: ±300 kcal based on goal

### Macro Splits (by goal)
| Goal | Protein | Carbs | Fat |
|------|---------|-------|-----|
| Weight Loss | 40% | 30% | 30% |
| Muscle Gain | 35% | 45% | 20% |
| Maintain | 30% | 40% | 30% |

## AI Features

### Food Photo Analysis
Uses Claude Vision to analyze food photos:
- Identifies meal type
- Estimates calories
- Calculates macros (protein, carbs, fat)
- Provides confidence level

### Daily Tips
AI generates personalized motivational tips based on:
- Your fitness goal
- Current fitness level
- Today's calorie and macro progress
- Whether you've had a gym session

## Error Handling

The bot includes comprehensive error handling:
- Graceful fallbacks for API failures
- User-friendly error messages in the selected language
- Input validation with helpful prompts
- Database transaction integrity

## Production Considerations

- SQLite database for lightweight deployment
- Async/await throughout for high concurrency
- Structured logging for debugging
- Environment variable configuration
- Modular bot module structure
- Comprehensive translation system

## Tech Stack

- **Bot Framework**: python-telegram-bot 20.7
- **AI Integration**: Anthropic Claude Sonnet 4.6
- **Database**: SQLite with aiosqlite
- **Async**: Python asyncio
- **Config**: python-dotenv

## Contributing

To contribute to Capybara Bot:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or feature requests, please open a GitHub issue.

---

Built with ❤️ for fitness enthusiasts everywhere. Happy training! 💪
