import pytest
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup
from bot.keyboards import (
    language_keyboard, gender_keyboard, goal_keyboard, gym_frequency_keyboard,
    gym_duration_keyboard, fitness_level_keyboard, diet_keyboard, water_goal_keyboard,
    main_menu_keyboard, gym_menu_keyboard, food_action_keyboard, sets_keyboard,
    reps_keyboard, confirm_keyboard, back_keyboard
)


class TestLanguageKeyboard:
    """Test language selection keyboard"""

    def test_language_keyboard_has_3_buttons(self):
        """Test that language keyboard has 3 buttons"""
        kb = language_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 3

    def test_language_keyboard_has_correct_labels(self):
        """Test language keyboard has correct language labels"""
        kb = language_keyboard()
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        labels = [btn.text for btn in all_buttons]

        assert any("Română" in label or "ro" in label for label in labels)
        assert any("English" in label or "en" in label for label in labels)
        assert any("Русский" in label or "ru" in label for label in labels)


class TestGenderKeyboard:
    """Test gender selection keyboard"""

    def test_gender_keyboard_has_2_buttons(self):
        """Test gender keyboard has 2 buttons"""
        kb = gender_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 2

    @pytest.mark.parametrize("lang", ["en", "ro", "ru"])
    def test_gender_keyboard_all_languages(self, lang):
        """Test gender keyboard works for all languages"""
        kb = gender_keyboard(lang)
        assert isinstance(kb, InlineKeyboardMarkup)
        assert len(kb.inline_keyboard) > 0


class TestGoalKeyboard:
    """Test goal selection keyboard"""

    def test_goal_keyboard_returns_inline_markup(self):
        """Test that goal keyboard returns InlineKeyboardMarkup"""
        kb = goal_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_goal_keyboard_has_5_buttons(self):
        """Test goal keyboard has 5 buttons"""
        kb = goal_keyboard("en")
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 5

    @pytest.mark.parametrize("lang", ["en", "ro", "ru"])
    def test_goal_keyboard_all_languages(self, lang):
        """Test goal keyboard works for all languages"""
        kb = goal_keyboard(lang)
        assert isinstance(kb, InlineKeyboardMarkup)


class TestGymFrequencyKeyboard:
    """Test gym frequency keyboard"""

    def test_gym_frequency_keyboard_has_7_buttons(self):
        """Test gym frequency keyboard has 7 buttons (1-7 days)"""
        kb = gym_frequency_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 7


class TestGymDurationKeyboard:
    """Test gym duration keyboard"""

    def test_gym_duration_keyboard_has_5_buttons(self):
        """Test gym duration keyboard has 5 buttons"""
        kb = gym_duration_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 5


class TestFitnessLevelKeyboard:
    """Test fitness level keyboard"""

    def test_fitness_level_keyboard_has_3_buttons(self):
        """Test fitness level keyboard has 3 buttons"""
        kb = fitness_level_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 3

    @pytest.mark.parametrize("lang", ["en", "ro", "ru"])
    def test_fitness_level_keyboard_all_languages(self, lang):
        """Test fitness level keyboard works for all languages"""
        kb = fitness_level_keyboard(lang)
        assert isinstance(kb, InlineKeyboardMarkup)


class TestDietKeyboard:
    """Test diet preference keyboard"""

    def test_diet_keyboard_has_5_buttons(self):
        """Test diet keyboard has 5 buttons"""
        kb = diet_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 5


class TestWaterGoalKeyboard:
    """Test water goal keyboard"""

    def test_water_goal_keyboard_has_4_buttons(self):
        """Test water goal keyboard has 4 buttons"""
        kb = water_goal_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 4


class TestMainMenuKeyboard:
    """Test main menu reply keyboard"""

    def test_main_menu_keyboard_returns_reply_markup(self):
        """Test main menu keyboard returns ReplyKeyboardMarkup"""
        kb = main_menu_keyboard("en")
        assert isinstance(kb, ReplyKeyboardMarkup)

    def test_main_menu_keyboard_has_required_buttons(self):
        """Test main menu keyboard has required buttons"""
        kb = main_menu_keyboard("en")
        assert isinstance(kb, ReplyKeyboardMarkup)

        all_buttons = [btn for row in kb.keyboard for btn in row]
        assert len(all_buttons) >= 5

    @pytest.mark.parametrize("lang", ["en", "ro", "ru"])
    def test_main_menu_keyboard_all_languages(self, lang):
        """Test main menu keyboard works for all languages"""
        kb = main_menu_keyboard(lang)
        assert isinstance(kb, ReplyKeyboardMarkup)


class TestGymMenuKeyboard:
    """Test gym session menu keyboard"""

    def test_gym_menu_keyboard_has_3_buttons(self):
        """Test gym menu keyboard has 3 buttons"""
        kb = gym_menu_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 3

    @pytest.mark.parametrize("lang", ["en", "ro", "ru"])
    def test_gym_menu_keyboard_all_languages(self, lang):
        """Test gym menu keyboard works for all languages"""
        kb = gym_menu_keyboard(lang)
        assert kb is not None


class TestFoodActionKeyboard:
    """Test food analysis action keyboard"""

    def test_food_action_keyboard_has_3_buttons(self):
        """Test food action keyboard has 3 buttons"""
        kb = food_action_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 3

    def test_food_action_keyboard_has_record_edit_skip(self):
        """Test food action keyboard has record, edit, and skip buttons"""
        kb = food_action_keyboard("en")
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]

        callback_data_list = [btn.callback_data for btn in all_buttons]
        assert "record_food" in callback_data_list
        assert "edit_food" in callback_data_list
        assert "skip_food" in callback_data_list


class TestSetsKeyboard:
    """Test sets keyboard"""

    def test_sets_keyboard_has_6_buttons(self):
        """Test sets keyboard has 6 buttons (1-6 sets)"""
        kb = sets_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 6


class TestRepsKeyboard:
    """Test reps keyboard"""

    def test_reps_keyboard_has_7_buttons(self):
        """Test reps keyboard has 7 buttons for common rep ranges"""
        kb = reps_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 7


class TestConfirmKeyboard:
    """Test confirmation keyboard"""

    def test_confirm_keyboard_has_2_buttons(self):
        """Test confirm keyboard has 2 buttons (Yes/No)"""
        kb = confirm_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 2

    def test_confirm_keyboard_has_yes_no(self):
        """Test confirm keyboard has yes and no options"""
        kb = confirm_keyboard("en")
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]

        callback_data_list = [btn.callback_data for btn in all_buttons]
        assert "confirm_yes" in callback_data_list
        assert "confirm_no" in callback_data_list


class TestBackKeyboard:
    """Test back button keyboard"""

    def test_back_keyboard_has_1_button(self):
        """Test back keyboard has 1 button"""
        kb = back_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(all_buttons) == 1
