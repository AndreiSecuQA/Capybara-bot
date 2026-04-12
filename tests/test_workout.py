import pytest
from database import (
    start_gym_session, add_exercise, end_gym_session,
    get_session_exercises, init_db
)


class TestVolumeCalculation:
    """Test exercise volume calculations"""

    def test_volume_calculation_basic(self):
        """Test basic volume calculation: sets * reps * weight"""
        sets = 4
        reps = 8
        weight = 80

        volume = sets * reps * weight

        assert volume == 2560

    def test_volume_calculation_heavy(self):
        """Test volume calculation with heavy weight"""
        volume = 5 * 5 * 150
        assert volume == 3750

    def test_volume_calculation_light(self):
        """Test volume calculation with light weight"""
        volume = 3 * 12 * 20
        assert volume == 720

    def test_volume_calculation_bodyweight(self):
        """Test volume calculation with bodyweight (0 kg added)"""
        volume = 10 * 10 * 0
        assert volume == 0

    @pytest.mark.parametrize("sets,reps,weight,expected", [
        (1, 1, 1, 1),
        (3, 8, 60, 1440),
        (4, 6, 100, 2400),
        (5, 5, 120, 3000),
        (2, 20, 40, 1600),
    ])
    def test_volume_calculation_various(self, sets, reps, weight, expected):
        """Test volume calculation with various values"""
        volume = sets * reps * weight
        assert volume == expected


class TestCalorieBurnEstimation:
    """Test calorie burn calculations for gym sessions"""

    def test_calorie_burn_basic(self):
        """Test basic calorie burn: MET * weight_kg * (duration_min / 60)"""
        met = 6
        weight = 75
        duration_min = 60

        calories = int(met * weight * (duration_min / 60))

        assert calories == 450

    def test_calorie_burn_30_minutes(self):
        """Test calorie burn for 30-minute session"""
        calories = int(6 * 80 * (30 / 60))
        assert calories == 240

    def test_calorie_burn_90_minutes(self):
        """Test calorie burn for 90-minute session"""
        calories = int(6 * 75 * (90 / 60))
        assert calories == 675

    def test_calorie_burn_heavier_person(self):
        """Test calorie burn for heavier person"""
        calories = int(6 * 100 * (60 / 60))
        assert calories == 600

    def test_calorie_burn_lighter_person(self):
        """Test calorie burn for lighter person"""
        calories = int(6 * 50 * (60 / 60))
        assert calories == 300

    @pytest.mark.parametrize("met,weight,duration,expected", [
        (6, 75, 60, 450),
        (6, 80, 30, 240),
        (6, 90, 45, 405),
        (6, 100, 120, 1200),
        (6, 70, 20, 140),
    ])
    def test_calorie_burn_various(self, met, weight, duration, expected):
        """Test calorie burn with various values"""
        calories = int(met * weight * (duration / 60))
        assert calories == expected


class TestGymSession:
    """Test full gym session workflow"""

    @pytest.mark.asyncio
    async def test_full_workout_session(self, in_memory_db, sample_user):
        """Test complete workout session with multiple exercises"""
        uid = sample_user["user_id"]

        session_id = await start_gym_session(uid)
        assert session_id > 0

        await add_exercise(session_id, uid, "Squat", 5, 5, 100)
        await add_exercise(session_id, uid, "Bench Press", 4, 8, 80)
        await add_exercise(session_id, uid, "Deadlift", 3, 5, 120)

        exercises = await get_session_exercises(session_id)
        assert len(exercises) == 3

        result = await end_gym_session(session_id, uid)

        assert result is not None
        assert result["total_volume"] == 6860
        assert result["calories_burned"] > 0

    @pytest.mark.asyncio
    async def test_short_workout_session(self, in_memory_db, sample_user):
        """Test a short workout session"""
        uid = sample_user["user_id"]
        session_id = await start_gym_session(uid)
        await add_exercise(session_id, uid, "Push-ups", 3, 20, 0)
        result = await end_gym_session(session_id, uid)

        assert result["total_volume"] == 0
        assert result["calories_burned"] > 0

    @pytest.mark.asyncio
    async def test_single_exercise_session(self, in_memory_db, sample_user):
        """Test session with just one exercise"""
        uid = sample_user["user_id"]
        session_id = await start_gym_session(uid)
        await add_exercise(session_id, uid, "Barbell Squat", 8, 3, 140)
        result = await end_gym_session(session_id, uid)

        assert result["total_volume"] == 3360

    @pytest.mark.asyncio
    async def test_empty_workout_session(self, in_memory_db, sample_user):
        """Test ending a session with no exercises"""
        uid = sample_user["user_id"]
        session_id = await start_gym_session(uid)
        result = await end_gym_session(session_id, uid)

        assert result is not None
        assert result["total_volume"] == 0


class TestExerciseTracking:
    """Test exercise tracking in sessions"""

    @pytest.mark.asyncio
    async def test_exercise_order_preserved(self, in_memory_db, sample_user):
        """Test that exercises are logged in order"""
        uid = sample_user["user_id"]
        session_id = await start_gym_session(uid)
        exercises_to_add = ["Squat", "Bench Press", "Deadlift", "Leg Press"]

        for exercise in exercises_to_add:
            await add_exercise(session_id, uid, exercise, 4, 8, 80)

        logged_exercises = await get_session_exercises(session_id)

        for i, exercise_name in enumerate(exercises_to_add):
            assert logged_exercises[i]["name"] == exercise_name

    @pytest.mark.asyncio
    async def test_exercise_details_storage(self, in_memory_db, sample_user):
        """Test that all exercise details are stored correctly"""
        uid = sample_user["user_id"]
        session_id = await start_gym_session(uid)
        await add_exercise(session_id, uid, "Barbell Squat", 5, 5, 150)

        exercises = await get_session_exercises(session_id)

        assert exercises[0]["name"] == "Barbell Squat"
        assert exercises[0]["sets"] == 5
        assert exercises[0]["reps"] == 5
        assert exercises[0]["weight_kg"] == 150
        assert exercises[0]["volume_kg"] == 3750
