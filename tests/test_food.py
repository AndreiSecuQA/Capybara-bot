import pytest
import json
from database import (
    log_food, get_daily_summary, get_today_meals, init_db
)


class TestFoodLogging:
    """Test food logging operations"""

    @pytest.mark.asyncio
    async def test_log_food_stores_correctly(self, in_memory_db, sample_user):
        """Test that food is logged correctly"""
        uid = sample_user["user_id"]
        await log_food(uid, "Salad", 250, 20, 15, 10, "photo_id_1")

        meals = await get_today_meals(uid)
        assert len(meals) == 1
        assert meals[0]["meal_name"] == "Salad"
        assert meals[0]["calories"] == 250

    @pytest.mark.asyncio
    async def test_log_food_without_photo(self, in_memory_db, sample_user):
        """Test logging food without a photo file ID"""
        uid = sample_user["user_id"]
        await log_food(uid, "Rice Bowl", 520, 20, 75, 12)

        summary = await get_daily_summary(uid)
        assert summary["total_calories"] == 520

    @pytest.mark.asyncio
    async def test_daily_summary_accumulates_foods(self, in_memory_db, sample_user):
        """Test that daily summary accumulates multiple food logs"""
        uid = sample_user["user_id"]

        await log_food(uid, "Breakfast", 400, 15, 60, 10, "f1")
        await log_food(uid, "Lunch", 600, 35, 80, 15, "f2")
        await log_food(uid, "Dinner", 500, 40, 50, 20, "f3")

        summary = await get_daily_summary(uid)

        assert summary["total_calories"] == 1500
        assert summary["total_protein"] == 90
        assert summary["total_carbs"] == 190
        assert summary["total_fat"] == 45

    @pytest.mark.asyncio
    async def test_daily_summary_resets_per_day(self, in_memory_db, sample_user):
        """Test that daily summary is per-date"""
        uid = sample_user["user_id"]

        await log_food(uid, "Breakfast", 400, 15, 60, 10)
        today_summary = await get_daily_summary(uid)

        assert today_summary["total_calories"] == 400

        yesterday_summary = await get_daily_summary(uid, "2020-01-01")
        assert yesterday_summary["total_calories"] == 0

    @pytest.mark.asyncio
    async def test_multiple_food_logs_same_meal(self, in_memory_db, sample_user):
        """Test logging same meal type multiple times"""
        uid = sample_user["user_id"]

        await log_food(uid, "Coffee", 50, 2, 5, 0)
        await log_food(uid, "Coffee", 50, 2, 5, 0)

        summary = await get_daily_summary(uid)
        assert summary["total_calories"] == 100

    @pytest.mark.asyncio
    async def test_get_today_meals_returns_list(self, in_memory_db, sample_user):
        """Test that get_today_meals returns a list"""
        uid = sample_user["user_id"]

        await log_food(uid, "Meal1", 400, 20, 50, 15)
        meals = await get_today_meals(uid)

        assert isinstance(meals, list)
        assert len(meals) > 0

    @pytest.mark.asyncio
    async def test_get_today_meals_empty(self, in_memory_db, sample_user):
        """Test that get_today_meals returns empty list for new user"""
        uid = sample_user["user_id"]

        meals = await get_today_meals(uid)
        assert isinstance(meals, list)
        assert len(meals) == 0


class TestFoodAnalysisJSON:
    """Test JSON parsing for food analysis"""

    def test_food_json_parsing_valid(self):
        """Test parsing valid food analysis JSON"""
        raw = '{"meal_name":"Rice bowl","calories":520,"protein_g":28,"carbs_g":75,"fat_g":12,"confidence":"high","notes":""}'
        parsed = json.loads(raw)

        assert parsed["meal_name"] == "Rice bowl"
        assert parsed["calories"] == 520
        assert parsed["protein_g"] == 28
        assert parsed["carbs_g"] == 75
        assert parsed["fat_g"] == 12

    def test_food_json_parsing_strips_code_block(self):
        """Test stripping markdown code block from JSON"""
        text = '```json\n{"meal_name":"Soup","calories":200,"protein_g":10,"carbs_g":25,"fat_g":5,"confidence":"medium","notes":""}\n```'

        if "```" in text:
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()

        parsed = json.loads(text)

        assert parsed["meal_name"] == "Soup"
        assert parsed["calories"] == 200

    def test_food_json_parsing_without_json_prefix(self):
        """Test stripping code block without json prefix"""
        text = '```\n{"meal_name":"Pizza","calories":600,"protein_g":25,"carbs_g":80,"fat_g":20,"confidence":"medium","notes":""}\n```'

        if "```" in text:
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()

        parsed = json.loads(text)

        assert parsed["meal_name"] == "Pizza"
        assert parsed["calories"] == 600

    def test_food_json_with_special_characters(self):
        """Test parsing JSON with special characters in meal name"""
        raw = '{"meal_name":"Sauté de Champignons","calories":150,"protein_g":5,"carbs_g":10,"fat_g":8,"confidence":"high","notes":"French dish"}'
        parsed = json.loads(raw)

        assert "Sauté" in parsed["meal_name"]
        assert parsed["calories"] == 150

    def test_food_json_all_fields(self):
        """Test that all required fields are present in parsed JSON"""
        raw = '{"meal_name":"Complete Meal","calories":500,"protein_g":30,"carbs_g":60,"fat_g":12,"confidence":"high","notes":"Good balance"}'
        parsed = json.loads(raw)

        required_fields = ["meal_name", "calories", "protein_g", "carbs_g", "fat_g", "confidence", "notes"]

        for field in required_fields:
            assert field in parsed, f"Missing field: {field}"


class TestMacroAccumulation:
    """Test macro nutrient accumulation"""

    @pytest.mark.asyncio
    async def test_protein_accumulation(self, in_memory_db, sample_user):
        """Test protein accumulation across meals"""
        uid = sample_user["user_id"]

        await log_food(uid, "Chicken", 450, 50, 0, 25)
        await log_food(uid, "Eggs", 200, 20, 5, 12)
        await log_food(uid, "Milk", 150, 10, 15, 5)

        summary = await get_daily_summary(uid)

        assert summary["total_protein"] == 80

    @pytest.mark.asyncio
    async def test_carbs_accumulation(self, in_memory_db, sample_user):
        """Test carbs accumulation across meals"""
        uid = sample_user["user_id"]

        await log_food(uid, "Rice", 350, 5, 80, 2)
        await log_food(uid, "Pasta", 400, 15, 70, 5)
        await log_food(uid, "Bread", 150, 5, 30, 1)

        summary = await get_daily_summary(uid)

        assert summary["total_carbs"] == 180

    @pytest.mark.asyncio
    async def test_fat_accumulation(self, in_memory_db, sample_user):
        """Test fat accumulation across meals"""
        uid = sample_user["user_id"]

        await log_food(uid, "Olive Oil", 200, 0, 0, 22)
        await log_food(uid, "Nuts", 300, 10, 10, 25)
        await log_food(uid, "Cheese", 250, 25, 3, 20)

        summary = await get_daily_summary(uid)

        assert summary["total_fat"] == 67

    @pytest.mark.asyncio
    async def test_calorie_accumulation(self, in_memory_db, sample_user):
        """Test total calorie accumulation"""
        uid = sample_user["user_id"]

        foods = [
            ("Breakfast", 400, 15, 60, 10),
            ("Snack", 150, 5, 20, 5),
            ("Lunch", 600, 40, 80, 15),
            ("Snack", 100, 3, 15, 3),
            ("Dinner", 550, 45, 60, 12),
        ]

        for name, cal, pro, carb, fat in foods:
            await log_food(uid, name, cal, pro, carb, fat)

        summary = await get_daily_summary(uid)

        assert summary["total_calories"] == 1800

    @pytest.mark.asyncio
    async def test_micro_meals_add_up(self, in_memory_db, sample_user):
        """Test that many small meals accumulate correctly"""
        uid = sample_user["user_id"]

        for i in range(5):
            await log_food(uid, f"Snack {i+1}", 100, 5, 15, 3)

        summary = await get_daily_summary(uid)

        assert summary["total_calories"] == 500
        assert summary["total_protein"] == 25
        assert summary["total_carbs"] == 75
        assert summary["total_fat"] == 15


class TestFoodMacroRanges:
    """Test macro nutrient ranges"""

    @pytest.mark.asyncio
    async def test_high_protein_meal(self, in_memory_db, sample_user):
        """Test logging high-protein meal"""
        uid = sample_user["user_id"]

        await log_food(uid, "Lean Beef", 400, 50, 10, 15)

        summary = await get_daily_summary(uid)

        assert summary["total_protein"] == 50

    @pytest.mark.asyncio
    async def test_high_carb_meal(self, in_memory_db, sample_user):
        """Test logging high-carb meal"""
        uid = sample_user["user_id"]

        await log_food(uid, "Pasta with Sauce", 500, 20, 100, 5)

        summary = await get_daily_summary(uid)

        assert summary["total_carbs"] == 100

    @pytest.mark.asyncio
    async def test_high_fat_meal(self, in_memory_db, sample_user):
        """Test logging high-fat meal"""
        uid = sample_user["user_id"]

        await log_food(uid, "Salmon with Oil", 450, 40, 5, 35)

        summary = await get_daily_summary(uid)

        assert summary["total_fat"] == 35
