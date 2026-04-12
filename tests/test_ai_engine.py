import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from bot.ai_engine import analyze_food_photo, get_daily_tip


class TestAnalyzeFoodPhoto:
    """Test food photo analysis with Gemini"""

    @pytest.mark.asyncio
    async def test_analyze_food_photo_returns_dict(self, mock_anthropic_client):
        """Test that analyze_food_photo returns a dictionary"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "meal_name": "Oatmeal with berries",
            "calories": 380,
            "protein_g": 12.5,
            "carbs_g": 65.0,
            "fat_g": 8.0,
            "confidence": "high",
            "notes": "Healthy breakfast"
        })

        mock_vision.generate_content.return_value = mock_response

        result = await analyze_food_photo(b"fake_image_bytes", "en")

        assert isinstance(result, dict)
        assert result["calories"] == 380
        assert result["meal_name"] == "Oatmeal with berries"
        assert "protein_g" in result
        assert result["confidence"] == "high"

    @pytest.mark.asyncio
    async def test_analyze_food_photo_parses_json(self, mock_anthropic_client):
        """Test that analyze_food_photo correctly parses JSON"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "meal_name": "Chicken Breast",
            "calories": 450,
            "protein_g": 50,
            "carbs_g": 0,
            "fat_g": 10,
            "confidence": "high",
            "notes": ""
        })

        mock_vision.generate_content.return_value = mock_response

        result = await analyze_food_photo(b"image_data", "en")

        assert result["meal_name"] == "Chicken Breast"
        assert result["calories"] == 450
        assert result["protein_g"] == 50

    @pytest.mark.asyncio
    async def test_analyze_food_photo_handles_json_in_code_block(self, mock_anthropic_client):
        """Test analyze_food_photo extracts JSON from code blocks"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = '```json\n{"meal_name":"Pizza","calories":600,"protein_g":25,"carbs_g":80,"fat_g":20,"confidence":"medium","notes":""}\n```'

        mock_vision.generate_content.return_value = mock_response

        result = await analyze_food_photo(b"fake_bytes", "en")

        assert result["meal_name"] == "Pizza"
        assert result["calories"] == 600
        assert result["protein_g"] == 25

    @pytest.mark.asyncio
    async def test_analyze_food_photo_handles_markdown_code_block(self, mock_anthropic_client):
        """Test analyze_food_photo handles markdown code block without json prefix"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = '```\n{"meal_name":"Rice Bowl","calories":520,"protein_g":28,"carbs_g":75,"fat_g":12,"confidence":"high","notes":""}\n```'

        mock_vision.generate_content.return_value = mock_response

        result = await analyze_food_photo(b"image", "en")

        assert result["meal_name"] == "Rice Bowl"
        assert result["calories"] == 520

    @pytest.mark.asyncio
    async def test_analyze_food_photo_returns_default_on_error(self, mock_anthropic_client):
        """Test analyze_food_photo returns default values on error"""
        mock_vision, mock_text = mock_anthropic_client
        mock_vision.generate_content.side_effect = Exception("API Error")

        result = await analyze_food_photo(b"bad_data", "en")

        assert result["meal_name"] == "Unknown meal"
        assert result["calories"] == 400
        assert result["confidence"] == "low"
        assert result["notes"] == "Analysis failed"

    @pytest.mark.asyncio
    async def test_analyze_food_photo_with_different_languages(self, mock_anthropic_client):
        """Test analyze_food_photo works with different languages"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "meal_name": "Salată",
            "calories": 250,
            "protein_g": 15,
            "carbs_g": 20,
            "fat_g": 10,
            "confidence": "high",
            "notes": ""
        })

        mock_vision.generate_content.return_value = mock_response

        result = await analyze_food_photo(b"image", "ro")

        assert result["meal_name"] == "Salată"
        assert result["calories"] == 250

    @pytest.mark.asyncio
    async def test_analyze_food_photo_confidence_levels(self, mock_anthropic_client):
        """Test analyze_food_photo with different confidence levels"""
        mock_vision, mock_text = mock_anthropic_client
        confidence_levels = ["low", "medium", "high"]

        for confidence in confidence_levels:
            mock_response = MagicMock()
            mock_response.text = json.dumps({
                "meal_name": "Test Meal",
                "calories": 400,
                "protein_g": 20,
                "carbs_g": 50,
                "fat_g": 10,
                "confidence": confidence,
                "notes": ""
            })

            mock_vision.generate_content.return_value = mock_response

            result = await analyze_food_photo(b"image", "en")

            assert result["confidence"] == confidence


class TestGetDailyTip:
    """Test daily motivational tip generation"""

    @pytest.mark.asyncio
    async def test_get_daily_tip_returns_string(self, mock_anthropic_client):
        """Test that get_daily_tip returns a string"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = "Great job hitting your protein goal today!"

        mock_text.generate_content.return_value = mock_response

        user_data = {
            "goal": "gain_muscle",
            "fitness_level": "intermediate",
            "calorie_target": 2500
        }
        daily = {
            "total_calories": 2100,
            "total_protein": 140,
            "gym_session": 1
        }

        tip = await get_daily_tip(user_data, daily, "en")

        assert isinstance(tip, str)
        assert len(tip) > 0

    @pytest.mark.asyncio
    async def test_get_daily_tip_for_different_goals(self, mock_anthropic_client):
        """Test get_daily_tip with different fitness goals"""
        mock_vision, mock_text = mock_anthropic_client
        goals = ["gain_muscle", "weight_loss", "endurance", "general_fitness"]

        for goal in goals:
            mock_response = MagicMock()
            mock_response.text = f"Keep working on your {goal} goal!"

            mock_text.generate_content.return_value = mock_response

            user_data = {"goal": goal, "fitness_level": "intermediate", "calorie_target": 2000}
            daily = {"total_calories": 1800, "total_protein": 120, "gym_session": 0}

            tip = await get_daily_tip(user_data, daily, "en")

            assert isinstance(tip, str)
            assert len(tip) > 0

    @pytest.mark.asyncio
    async def test_get_daily_tip_returns_fallback_on_error(self, mock_anthropic_client):
        """Test get_daily_tip returns fallback tip on error"""
        mock_vision, mock_text = mock_anthropic_client
        mock_text.generate_content.side_effect = Exception("API Error")

        user_data = {"goal": "gain_muscle", "fitness_level": "beginner", "calorie_target": 2000}
        daily = {"total_calories": 1500, "total_protein": 100, "gym_session": 0}

        tip = await get_daily_tip(user_data, daily, "en")

        assert isinstance(tip, str)
        assert len(tip) > 0

    @pytest.mark.asyncio
    async def test_get_daily_tip_respects_language(self, mock_anthropic_client):
        """Test get_daily_tip uses the specified language"""
        mock_vision, mock_text = mock_anthropic_client
        for lang in ["en", "ro", "ru"]:
            mock_response = MagicMock()
            mock_response.text = f"Tip in {lang}"

            mock_text.generate_content.return_value = mock_response

            user_data = {"goal": "general", "fitness_level": "beginner", "calorie_target": 2000}
            daily = {"total_calories": 1800, "total_protein": 100, "gym_session": 0}

            tip = await get_daily_tip(user_data, daily, lang)

            assert isinstance(tip, str)

    @pytest.mark.asyncio
    async def test_get_daily_tip_with_complete_user_data(self, mock_anthropic_client):
        """Test get_daily_tip with comprehensive user and daily data"""
        mock_vision, mock_text = mock_anthropic_client
        mock_response = MagicMock()
        mock_response.text = "You're crushing it! Keep it up!"

        mock_text.generate_content.return_value = mock_response

        user_data = {
            "goal": "muscle_gain",
            "fitness_level": "advanced",
            "calorie_target": 2800,
            "protein_target": 200
        }
        daily = {
            "total_calories": 2750,
            "total_protein": 195,
            "total_carbs": 300,
            "total_fat": 80,
            "gym_session": 1,
            "calories_burned": 600
        }

        tip = await get_daily_tip(user_data, daily, "en")

        assert isinstance(tip, str)
        assert len(tip) > 0
