import json
import logging
import io
import PIL.Image
from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)


async def analyze_food_photo(image_bytes: bytes, lang: str) -> dict:
    """Send food photo to Gemini Vision and get nutrition data as JSON."""
    try:
        image = PIL.Image.open(io.BytesIO(image_bytes))

        prompt = """Analyze this food photo and respond ONLY with a valid JSON object, no other text:
{
  "meal_name": "descriptive meal name in English",
  "calories": <integer estimate>,
  "protein_g": <float>,
  "carbs_g": <float>,
  "fat_g": <float>,
  "confidence": "low|medium|high",
  "notes": "brief note about the meal"
}
Be as accurate as possible based on typical portion sizes."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, image]
        )
        text = response.text.strip()

        # Strip markdown code blocks if present
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue

        return json.loads(text)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in analyze_food_photo: {e}")
        return {
            "meal_name": "Unknown meal",
            "calories": 400,
            "protein_g": 20.0,
            "carbs_g": 40.0,
            "fat_g": 15.0,
            "confidence": "low",
            "notes": "Could not analyze photo accurately"
        }
    except Exception as e:
        logger.error(f"Error in analyze_food_photo: {e}")
        return {
            "meal_name": "Unknown meal",
            "calories": 400,
            "protein_g": 20.0,
            "carbs_g": 40.0,
            "fat_g": 15.0,
            "confidence": "low",
            "notes": "Analysis failed"
        }


async def get_daily_tip(user_data: dict, daily_summary: dict, lang: str) -> str:
    """Generate a short motivational tip using Gemini based on today's data."""
    try:
        lang_instruction = {
            "ro": "Răspunde în limba română.",
            "ru": "Отвечай на русском языке.",
            "en": "Respond in English."
        }.get(lang, "Respond in English.")

        goal = user_data.get("goal", "general_fitness")
        fitness_level = user_data.get("fitness_level", "intermediate")
        calorie_target = user_data.get("calorie_target", 2000)
        total_calories = daily_summary.get("total_calories", 0)
        total_protein = daily_summary.get("total_protein", 0)
        had_gym = daily_summary.get("gym_session", 0)

        prompt = f"""You are a friendly fitness coach. {lang_instruction}

User profile: goal={goal}, fitness_level={fitness_level}
Today's data: calories consumed={total_calories}/{calorie_target} target, protein={total_protein}g, gym session today={'yes' if had_gym else 'no'}

Give ONE short, specific, motivating tip (max 1 sentence) based on this data. Be concrete and actionable."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        logger.error(f"Error in get_daily_tip: {e}")
        tips = {
            "ro": "Continuă să faci progres, fiecare zi contează! 💪",
            "ru": "Продолжай двигаться вперёд, каждый день важен! 💪",
            "en": "Keep pushing forward, every day counts! 💪"
        }
        return tips.get(lang, tips["en"])
