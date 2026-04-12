import anthropic
import base64
import json
from config import ANTHROPIC_API_KEY

try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
except Exception:
    # Fallback for testing or if API key is not available
    client = None

async def analyze_food_photo(image_bytes: bytes, lang: str) -> dict:
    """Send photo to Claude Vision and get nutrition data"""
    try:
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Analyze this food photo and respond ONLY with a JSON object (no markdown, no code blocks):
{
  "meal_name": "descriptive meal name",
  "calories": <integer>,
  "protein_g": <float>,
  "carbs_g": <float>,
  "fat_g": <float>,
  "confidence": "low|medium|high",
  "notes": "brief note if any"
}
Only return the JSON."""
                    }
                ],
            }]
        )

        text = message.content[0].text.strip()
        # Clean up if wrapped in code blocks
        if "```" in text:
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()

        return json.loads(text)
    except Exception as e:
        # Return default if analysis fails
        return {
            "meal_name": "Unknown meal",
            "calories": 500,
            "protein_g": 20,
            "carbs_g": 50,
            "fat_g": 15,
            "confidence": "low",
            "notes": f"Error in analysis: {str(e)}"
        }

async def get_daily_tip(user_data: dict, daily_summary: dict, lang: str) -> str:
    """Generate a short motivational tip based on today's data"""
    try:
        goal = user_data.get('goal', 'general')
        fitness_level = user_data.get('fitness_level', 'beginner')
        calories = daily_summary.get('total_calories', 0)
        calorie_target = user_data.get('calorie_target', 2000)
        protein = daily_summary.get('total_protein', 0)
        protein_target = user_data.get('protein_target', 150)
        gym = daily_summary.get('gym_session', 0)

        prompt = f"""User: goal={goal}, fitness={fitness_level}
Today: {calories}/{calorie_target} kcal, {protein:.0f}/{protein_target:.0f}g protein, gym={'done' if gym else 'no'}
Language: {lang} (respond in this language only)

Give ONE short, specific, motivational fitness tip (max 1 sentence, 10-15 words). Be encouraging!"""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        # Return generic tip on error
        tips = {
            "en": "Keep pushing towards your goal! 💪",
            "ro": "Continua sa te lupta pentru obiectivele tale! 💪",
            "ru": "Продолжайте работать над своими целями! 💪"
        }
        return tips.get(lang, tips["en"])
