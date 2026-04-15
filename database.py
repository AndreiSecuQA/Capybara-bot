import aiosqlite
import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_PATH

async def init_db():
    """Initialize database with all required tables"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'en',
                gender TEXT,
                name TEXT,
                age INTEGER,
                height_cm REAL,
                weight_kg REAL,
                goal TEXT,
                gym_frequency INTEGER,
                gym_duration_min INTEGER,
                fitness_level TEXT,
                diet_preference TEXT,
                wake_time TEXT,
                sleep_time TEXT,
                daily_water_goal INTEGER DEFAULT 8,
                health_conditions TEXT,
                calorie_target REAL DEFAULT 2000,
                protein_target REAL DEFAULT 150,
                carbs_target REAL DEFAULT 200,
                fat_target REAL DEFAULT 65,
                bmi REAL,
                bmi_category TEXT,
                onboarding_complete INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrations: add columns to existing DBs that were created without them
        _migrations = [
            "ALTER TABLE users ADD COLUMN gender TEXT",
            "ALTER TABLE users ADD COLUMN bmi REAL",
            "ALTER TABLE users ADD COLUMN bmi_category TEXT",
            "ALTER TABLE users ADD COLUMN calorie_target REAL DEFAULT 2000",
            "ALTER TABLE users ADD COLUMN protein_target REAL DEFAULT 150",
            "ALTER TABLE users ADD COLUMN carbs_target REAL DEFAULT 200",
            "ALTER TABLE users ADD COLUMN fat_target REAL DEFAULT 65",
        ]
        for _m in _migrations:
            try:
                await db.execute(_m)
            except Exception:
                pass  # Column already exists — safe to ignore

        await db.commit()

        await db.execute("""
            CREATE TABLE IF NOT EXISTS gym_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                duration_min INTEGER,
                total_volume_kg REAL,
                calories_burned INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                user_id INTEGER,
                name TEXT,
                sets INTEGER,
                reps INTEGER,
                weight_kg REAL,
                volume_kg REAL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES gym_sessions(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS food_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                meal_name TEXT,
                calories INTEGER,
                protein_g REAL,
                carbs_g REAL,
                fat_g REAL,
                photo_file_id TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                total_calories INTEGER DEFAULT 0,
                total_protein REAL DEFAULT 0,
                total_carbs REAL DEFAULT 0,
                total_fat REAL DEFAULT 0,
                water_glasses INTEGER DEFAULT 0,
                gym_session INTEGER DEFAULT 0,
                calories_burned INTEGER DEFAULT 0,
                gym_duration_min INTEGER DEFAULT 0,
                UNIQUE(user_id, date),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await db.commit()

async def get_user(user_id: int):
    """Get user by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def create_user(user_id: int, username: str):
    """Create new user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def update_user(user_id: int, **fields):
    """Update user fields"""
    if not fields:
        return

    columns = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [user_id]

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            f"UPDATE users SET {columns} WHERE user_id = ?",
            values
        )
        await db.commit()

async def is_onboarding_complete(user_id: int) -> bool:
    """Check if user completed onboarding"""
    user = await get_user(user_id)
    return user is not None and user["onboarding_complete"] == 1

async def start_gym_session(user_id: int) -> int:
    """Start new gym session, return session_id"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO gym_sessions (user_id, started_at) VALUES (?, ?)",
            (user_id, datetime.now().isoformat())
        )
        await db.commit()
        return cursor.lastrowid

async def add_exercise(session_id: int, user_id: int, name: str, sets: int, reps: int, weight_kg: float):
    """Add exercise to session"""
    volume_kg = sets * reps * weight_kg
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO exercises (session_id, user_id, name, sets, reps, weight_kg, volume_kg, logged_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, user_id, name, sets, reps, weight_kg, volume_kg, datetime.now().isoformat())
        )
        await db.commit()

async def get_session_exercises(session_id: int):
    """Get all exercises in a session"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM exercises WHERE session_id = ? ORDER BY logged_at",
            (session_id,)
        ) as cursor:
            return await cursor.fetchall()

async def end_gym_session(session_id: int, user_id: int):
    """End gym session, calculate stats"""
    now = datetime.now()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get session start time
        async with db.execute("SELECT started_at FROM gym_sessions WHERE id = ?", (session_id,)) as cursor:
            session = await cursor.fetchone()

        start_time = datetime.fromisoformat(session["started_at"])
        duration_min = int((now - start_time).total_seconds() / 60)

        # Get user weight
        async with db.execute("SELECT weight_kg FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()

        weight_kg = user["weight_kg"] or 70

        # Calculate calories burned (MET=6 for moderate gym)
        duration_hours = duration_min / 60
        calories_burned = int(6 * weight_kg * duration_hours)

        # Get total volume
        async with db.execute(
            "SELECT SUM(volume_kg) as total FROM exercises WHERE session_id = ?",
            (session_id,)
        ) as cursor:
            result = await cursor.fetchone()

        total_volume = result["total"] or 0

        # Update session
        await db.execute(
            """UPDATE gym_sessions SET ended_at = ?, duration_min = ?, total_volume_kg = ?, calories_burned = ?
               WHERE id = ?""",
            (now.isoformat(), duration_min, total_volume, calories_burned, session_id)
        )

        # Update daily summary
        today = now.strftime("%Y-%m-%d")
        await db.execute(
            """INSERT INTO daily_summary (user_id, date, gym_session, calories_burned, gym_duration_min)
               VALUES (?, ?, 1, ?, ?)
               ON CONFLICT(user_id, date) DO UPDATE SET
                   gym_session = 1, calories_burned = ?, gym_duration_min = ?""",
            (user_id, today, calories_burned, duration_min, calories_burned, duration_min)
        )

        await db.commit()
        return {
            "duration_min": duration_min,
            "calories_burned": calories_burned,
            "total_volume": total_volume
        }

async def log_food(user_id: int, meal_name: str, calories: int, protein: float, carbs: float, fat: float, photo_file_id: str = None):
    """Log food intake"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        await db.execute(
            """INSERT INTO food_logs (user_id, meal_name, calories, protein_g, carbs_g, fat_g, photo_file_id, logged_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, meal_name, calories, protein, carbs, fat, photo_file_id, now.isoformat())
        )

        # Update daily summary
        await db.execute(
            """INSERT INTO daily_summary (user_id, date, total_calories, total_protein, total_carbs, total_fat)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, date) DO UPDATE SET
                   total_calories = total_calories + ?,
                   total_protein = total_protein + ?,
                   total_carbs = total_carbs + ?,
                   total_fat = total_fat + ?""",
            (user_id, today, calories, protein, carbs, fat, calories, protein, carbs, fat)
        )

        await db.commit()

async def get_daily_summary(user_id: int, date: str = None):
    """Get daily summary for user"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM daily_summary WHERE user_id = ? AND date = ?",
            (user_id, date)
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            return dict(row)

        return {
            "total_calories": 0,
            "total_protein": 0,
            "total_carbs": 0,
            "total_fat": 0,
            "water_glasses": 0,
            "gym_session": 0,
            "calories_burned": 0,
            "gym_duration_min": 0
        }

async def get_today_meals(user_id: int):
    """Get all meals logged today"""
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT meal_name, calories FROM food_logs
               WHERE user_id = ? AND DATE(logged_at) = ?
               ORDER BY logged_at""",
            (user_id, today)
        ) as cursor:
            return await cursor.fetchall()

async def update_daily_water(user_id: int, glasses: int):
    """Update water intake for today"""
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO daily_summary (user_id, date, water_glasses)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, date) DO UPDATE SET water_glasses = ?""",
            (user_id, today, glasses, glasses)
        )
        await db.commit()

async def get_weekly_stats(user_id: int):
    """Get stats for last 7 days"""
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    date_str = week_ago.strftime("%Y-%m-%d")

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Daily summary stats
        async with db.execute(
            """SELECT
                SUM(total_calories) as total_calories,
                AVG(total_calories) as avg_calories,
                SUM(total_protein) as total_protein,
                AVG(total_protein) as avg_protein,
                SUM(total_carbs) as total_carbs,
                AVG(total_carbs) as avg_carbs,
                SUM(total_fat) as total_fat,
                AVG(total_fat) as avg_fat,
                AVG(water_glasses) as avg_water,
                SUM(calories_burned) as total_burned
               FROM daily_summary
               WHERE user_id = ? AND date >= ?""",
            (user_id, date_str)
        ) as cursor:
            summary = await cursor.fetchone()

        # Gym sessions stats
        async with db.execute(
            """SELECT COUNT(*) as sessions, SUM(total_volume_kg) as total_volume
               FROM gym_sessions
               WHERE user_id = ? AND DATE(started_at) >= ?""",
            (user_id, date_str)
        ) as cursor:
            gym = await cursor.fetchone()

        return {
            "total_calories": summary["total_calories"] or 0,
            "avg_calories": summary["avg_calories"] or 0,
            "avg_protein": summary["avg_protein"] or 0,
            "avg_carbs": summary["avg_carbs"] or 0,
            "avg_fat": summary["avg_fat"] or 0,
            "avg_water": summary["avg_water"] or 0,
            "total_burned": summary["total_burned"] or 0,
            "sessions": gym["sessions"] or 0,
            "total_volume": gym["total_volume"] or 0
        }
