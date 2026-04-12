import pytest
import aiosqlite
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Set environment variable before anything imports database
os.environ['DATABASE_PATH'] = ':memory:'


@pytest.fixture
async def in_memory_db():
    """Create in-memory SQLite database for testing"""
    # Initialize the database with in-memory path
    db_path = ':memory:'

    # Create tables manually for in-memory test database
    async with aiosqlite.connect(db_path) as db:
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

    yield db_path


@pytest.fixture
async def sample_user(in_memory_db):
    """Create a sample user in the test database"""
    # Import with in-memory path already set
    import database

    # Monkey-patch the database module to use in-memory db
    original_connect = aiosqlite.connect

    async def patched_connect(path, *args, **kwargs):
        if path == ':memory:' or path == database.DATABASE_PATH:
            return await original_connect(':memory:', *args, **kwargs)
        return await original_connect(path, *args, **kwargs)

    with patch('aiosqlite.connect', patched_connect):
        from database import create_user, update_user, get_user

        user_id = 12345
        await create_user(user_id, "testuser")

        # Update with realistic data
        await update_user(
            user_id,
            name="Test User",
            language="en",
            gender="male",
            age=28,
            height_cm=180,
            weight_kg=75,
            goal="muscle_gain",
            gym_frequency=4,
            gym_duration_min=60,
            fitness_level="intermediate",
            diet_preference="none",
            wake_time="07:00",
            sleep_time="23:00",
            daily_water_goal=8,
            calorie_target=2500,
            protein_target=175,
            carbs_target=250,
            fat_target=70,
            bmi=23.1,
            bmi_category="Normal"
        )

        user = await get_user(user_id)
        return user


@pytest.fixture
def mock_anthropic_client():
    """Mock Gemini models for testing"""
    with patch('bot.ai_engine._vision_model') as mock_vision, \
         patch('bot.ai_engine._text_model') as mock_text:
        yield mock_vision, mock_text
