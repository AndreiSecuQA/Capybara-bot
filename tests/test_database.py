import pytest
from database import (
    create_user, get_user, update_user, is_onboarding_complete,
    start_gym_session, add_exercise, end_gym_session, get_session_exercises,
    log_food, get_daily_summary, get_today_meals, update_daily_water,
    get_weekly_stats, init_db
)
from unittest.mock import patch
from datetime import datetime


class TestUserOperations:
    """Test user CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_user(self, in_memory_db):
        """Test creating a new user"""
        user = await get_user(12345)
        if user is None:
            await create_user(12345, "testuser")

        user = await get_user(12345)
        assert user is not None
        assert user["user_id"] == 12345
        assert user["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_returns_none_for_unknown(self, in_memory_db):
        """Test getting a non-existent user returns None"""
        user = await get_user(999999)
        assert user is None

    @pytest.mark.asyncio
    async def test_update_user_fields(self, in_memory_db, sample_user):
        """Test updating user fields"""
        user_id = sample_user["user_id"]

        await update_user(
            user_id,
            name="Updated Name",
            age=30,
            height_cm=182,
            weight_kg=78
        )

        user = await get_user(user_id)
        assert user["name"] == "Updated Name"
        assert user["age"] == 30
        assert user["height_cm"] == 182
        assert user["weight_kg"] == 78

    @pytest.mark.asyncio
    async def test_is_onboarding_complete_false_by_default(self, in_memory_db):
        """Test onboarding_complete is False by default"""
        await create_user(1001, "newuser")
        result = await is_onboarding_complete(1001)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_onboarding_complete_true_after_update(self, in_memory_db, sample_user):
        """Test onboarding_complete is True after setting it"""
        user_id = sample_user["user_id"]
        await update_user(user_id, onboarding_complete=1)
        result = await is_onboarding_complete(user_id)
        assert result is True


class TestGymOperations:
    """Test gym session and exercise operations"""

    @pytest.mark.asyncio
    async def test_start_gym_session_returns_session_id(self, in_memory_db, sample_user):
        """Test starting a gym session returns a valid session ID"""
        session_id = await start_gym_session(sample_user["user_id"])
        assert isinstance(session_id, int)
        assert session_id > 0

    @pytest.mark.asyncio
    async def test_add_exercise_calculates_volume(self, in_memory_db, sample_user):
        """Test adding an exercise calculates volume correctly"""
        session_id = await start_gym_session(sample_user["user_id"])

        # Add exercise: 4 sets x 8 reps x 80 kg = 2560 kg volume
        exercises = await get_session_exercises(session_id)
        initial_count = len(exercises)

        await add_exercise(session_id, sample_user["user_id"], "Bench Press", 4, 8, 80)

        exercises = await get_session_exercises(session_id)
        assert len(exercises) == initial_count + 1
        assert exercises[-1]["volume_kg"] == 4 * 8 * 80
        assert exercises[-1]["name"] == "Bench Press"

    @pytest.mark.asyncio
    async def test_end_gym_session_updates_calories(self, in_memory_db, sample_user):
        """Test ending gym session calculates calories burned"""
        session_id = await start_gym_session(sample_user["user_id"])

        await add_exercise(session_id, sample_user["user_id"], "Squat", 5, 5, 100)
        result = await end_gym_session(session_id, sample_user["user_id"])

        assert result is not None
        assert "duration_min" in result
        assert "calories_burned" in result
        assert "total_volume" in result
        assert result["calories_burned"] > 0
        assert result["total_volume"] == 5 * 5 * 100

    @pytest.mark.asyncio
    async def test_get_session_exercises(self, in_memory_db, sample_user):
        """Test retrieving exercises from a session"""
        session_id = await start_gym_session(sample_user["user_id"])

        await add_exercise(session_id, sample_user["user_id"], "Deadlift", 3, 5, 120)
        await add_exercise(session_id, sample_user["user_id"], "Bench Press", 4, 8, 80)

        exercises = await get_session_exercises(session_id)
        assert len(exercises) == 2
        assert exercises[0]["name"] == "Deadlift"
        assert exercises[1]["name"] == "Bench Press"

    @pytest.mark.asyncio
    async def test_multiple_exercises_in_session(self, in_memory_db, sample_user):
        """Test adding multiple exercises to one session"""
        session_id = await start_gym_session(sample_user["user_id"])

        await add_exercise(session_id, sample_user["user_id"], "Squat", 5, 5, 100)
        await add_exercise(session_id, sample_user["user_id"], "Bench Press", 4, 8, 80)
        await add_exercise(session_id, sample_user["user_id"], "Deadlift", 3, 5, 120)

        result = await end_gym_session(session_id, sample_user["user_id"])

        # Total volume: 5*5*100 + 4*8*80 + 3*5*120 = 2500 + 2560 + 1800 = 6860
        assert result["total_volume"] == 6860


class TestFoodOperations:
    """Test food logging operations"""

    @pytest.mark.asyncio
    async def test_log_food_updates_daily_summary(self, in_memory_db, sample_user):
        """Test logging food updates daily summary"""
        user_id = sample_user["user_id"]

        await log_food(user_id, "Oatmeal", 380, 12, 60, 8, "file_id_123")
        summary = await get_daily_summary(user_id)

        assert summary["total_calories"] == 380
        assert summary["total_protein"] == 12
        assert summary["total_carbs"] == 60
        assert summary["total_fat"] == 8

    @pytest.mark.asyncio
    async def test_multiple_food_logs_accumulate(self, in_memory_db, sample_user):
        """Test multiple food logs accumulate correctly"""
        uid = sample_user["user_id"]

        await log_food(uid, "Oatmeal", 380, 12, 60, 8, "f1")
        await log_food(uid, "Chicken", 450, 40, 10, 15, "f2")

        summary = await get_daily_summary(uid)
        assert summary["total_calories"] == 830
        assert summary["total_protein"] == 52
        assert summary["total_carbs"] == 70
        assert summary["total_fat"] == 23

    @pytest.mark.asyncio
    async def test_get_today_meals(self, in_memory_db, sample_user):
        """Test retrieving today's meals"""
        user_id = sample_user["user_id"]

        await log_food(user_id, "Breakfast", 400, 15, 60, 10, "f1")
        await log_food(user_id, "Lunch", 600, 40, 80, 15, "f2")

        meals = await get_today_meals(user_id)
        assert len(meals) == 2
        assert meals[0]["meal_name"] == "Breakfast"
        assert meals[0]["calories"] == 400
        assert meals[1]["meal_name"] == "Lunch"
        assert meals[1]["calories"] == 600

    @pytest.mark.asyncio
    async def test_log_food_without_photo_file_id(self, in_memory_db, sample_user):
        """Test logging food without a photo file ID"""
        user_id = sample_user["user_id"]

        await log_food(user_id, "Rice Bowl", 520, 20, 75, 12)
        summary = await get_daily_summary(user_id)

        assert summary["total_calories"] == 520
        assert summary["total_protein"] == 20


class TestDailySummary:
    """Test daily summary operations"""

    @pytest.mark.asyncio
    async def test_get_daily_summary_default_values(self, in_memory_db, sample_user):
        """Test getting daily summary returns default values for new day"""
        user_id = sample_user["user_id"]

        # Use a non-existent date to test default values
        summary = await get_daily_summary(user_id, "2020-01-01")

        assert summary["total_calories"] == 0
        assert summary["total_protein"] == 0
        assert summary["total_carbs"] == 0
        assert summary["total_fat"] == 0
        assert summary["water_glasses"] == 0

    @pytest.mark.asyncio
    async def test_update_daily_water(self, in_memory_db, sample_user):
        """Test updating water intake for the day"""
        user_id = sample_user["user_id"]

        await update_daily_water(user_id, 6)
        summary = await get_daily_summary(user_id)

        assert summary["water_glasses"] == 6


class TestWeeklyStats:
    """Test weekly statistics"""

    @pytest.mark.asyncio
    async def test_get_weekly_stats_returns_dict(self, in_memory_db, sample_user):
        """Test getting weekly stats returns a dictionary with expected keys"""
        user_id = sample_user["user_id"]

        stats = await get_weekly_stats(user_id)

        assert isinstance(stats, dict)
        assert "total_calories" in stats
        assert "avg_calories" in stats
        assert "avg_protein" in stats
        assert "avg_carbs" in stats
        assert "avg_fat" in stats
        assert "avg_water" in stats
        assert "total_burned" in stats
        assert "sessions" in stats
        assert "total_volume" in stats

    @pytest.mark.asyncio
    async def test_weekly_stats_with_no_data(self, in_memory_db, sample_user):
        """Test weekly stats with no data returns zeros"""
        user_id = sample_user["user_id"]

        stats = await get_weekly_stats(user_id)

        assert stats["total_calories"] == 0
        assert stats["avg_calories"] == 0
        assert stats["sessions"] == 0
        assert stats["total_volume"] == 0

    @pytest.mark.asyncio
    async def test_weekly_stats_with_food_and_gym_data(self, in_memory_db, sample_user):
        """Test weekly stats accumulates food and gym data"""
        user_id = sample_user["user_id"]

        # Add food
        await log_food(user_id, "Breakfast", 400, 20, 60, 10)
        await log_food(user_id, "Lunch", 600, 35, 80, 15)

        # Add gym session
        session_id = await start_gym_session(user_id)
        await add_exercise(session_id, user_id, "Bench Press", 4, 8, 80)
        await end_gym_session(session_id, user_id)

        stats = await get_weekly_stats(user_id)

        assert stats["total_calories"] == 1000
        assert stats["sessions"] == 1
        assert stats["total_volume"] == 2560
        assert stats["total_burned"] > 0
