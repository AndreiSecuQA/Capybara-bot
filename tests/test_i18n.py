import pytest
from i18n import TRANSLATIONS, t


class TestTranslations:
    """Test translation system"""

    def test_all_keys_exist_in_all_languages(self):
        """Test that all keys exist in all language dictionaries"""
        en_keys = set(TRANSLATIONS["en"].keys())

        for lang in ["ro", "ru"]:
            lang_keys = set(TRANSLATIONS[lang].keys())
            missing = en_keys - lang_keys

            assert not missing, f"Missing keys in '{lang}': {missing}"

    @pytest.mark.parametrize("lang", ["en", "ro", "ru"])
    def test_no_empty_translations(self, lang):
        """Test that no translation values are empty"""
        for key, value in TRANSLATIONS[lang].items():
            assert value, f"Empty translation for key '{key}' in '{lang}'"

    def test_t_returns_correct_language(self):
        """Test that t() returns the correct language translation"""
        en_result = t("en", "welcome")
        ro_result = t("ro", "welcome")
        ru_result = t("ru", "welcome")

        assert en_result != ro_result
        assert ro_result != ru_result
        assert "Capybara Bot" in en_result
        assert "Capybara Bot" in ro_result
        assert "Capybara Bot" in ru_result

    def test_t_falls_back_to_english_for_unknown_lang(self):
        """Test that t() falls back to English for unknown language"""
        result = t("fr", "ask_age")
        en_result = t("en", "ask_age")

        assert result == en_result

    def test_t_formats_kwargs(self):
        """Test that t() properly formats keyword arguments"""
        result = t("en", "exercise_added", exercise="Bench Press", sets=4, reps=8, weight=80)

        assert "Bench Press" in result
        assert "4" in result
        assert "8" in result
        assert "80" in result

    def test_t_returns_key_if_completely_missing(self):
        """Test that t() returns the key if translation doesn't exist"""
        result = t("en", "this_key_does_not_exist_xyz")

        assert result == "this_key_does_not_exist_xyz"

    def test_t_with_name_formatting(self):
        """Test translation with name formatting"""
        result = t("en", "onboarding_complete", name="Andrei", bmi=23.5, bmi_category="Normal",
                   calorie_target=2500, protein_target=175, carbs_target=250, fat_target=70)

        assert "Andrei" in result
        assert "23.5" in result
        assert "Normal" in result

    def test_language_keyboard_keys(self):
        """Test that language selection keys exist"""
        assert "choose_language" in TRANSLATIONS["en"]
        assert "choose_language" in TRANSLATIONS["ro"]
        assert "choose_language" in TRANSLATIONS["ru"]

    def test_goal_keys_exist(self):
        """Test that all goal keys exist in all languages"""
        goal_keys = [
            "ask_goal",
            "goal_lose_weight",
            "goal_gain_muscle",
            "goal_maintain",
            "goal_endurance",
            "goal_general_fitness"
        ]

        for key in goal_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"

    def test_gender_keys_exist(self):
        """Test that gender keys exist in all languages"""
        gender_keys = ["ask_gender", "gender_male", "gender_female"]

        for key in gender_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"

    def test_fitness_level_keys_exist(self):
        """Test that fitness level keys exist in all languages"""
        fitness_keys = ["ask_fitness_level", "fitness_beginner", "fitness_intermediate", "fitness_advanced"]

        for key in fitness_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"

    def test_diet_preference_keys_exist(self):
        """Test that diet preference keys exist in all languages"""
        diet_keys = ["ask_diet_preference", "diet_none", "diet_vegetarian", "diet_vegan", "diet_keto", "diet_halal"]

        for key in diet_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"

    def test_button_keys_exist(self):
        """Test that main menu button keys exist in all languages"""
        button_keys = ["btn_gym", "btn_food", "btn_progress", "btn_stats", "btn_settings"]

        for key in button_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"

    def test_error_message_keys_exist(self):
        """Test that error message keys exist in all languages"""
        error_keys = ["error", "invalid_input", "invalid_number", "invalid_time", "cancel", "success"]

        for key in error_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"

    def test_validation_error_keys(self):
        """Test that validation error keys exist in all languages"""
        validation_keys = ["age_invalid", "height_invalid", "weight_invalid"]

        for key in validation_keys:
            for lang in ["en", "ro", "ru"]:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in '{lang}'"
