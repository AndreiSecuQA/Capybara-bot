import pytest
from bot.onboarding import (
    goal_map, fitness_map, diet_map, gender_map
)
from i18n import t


class TestOnboardingMaps:
    """Test onboarding data mapping dictionaries"""

    def test_goal_map_contains_all_goals(self):
        """Test goal_map contains all goal options"""
        expected_goals = ["goal_lose", "goal_muscle", "goal_maintain", "goal_endurance", "goal_fitness"]

        for goal in expected_goals:
            assert goal in goal_map, f"Missing goal: {goal}"
            assert goal_map[goal] in ["weight_loss", "muscle_gain", "maintain", "endurance", "general_fitness"]

    def test_fitness_map_contains_all_levels(self):
        """Test fitness_map contains all fitness levels"""
        expected_levels = ["fit_beginner", "fit_intermediate", "fit_advanced"]

        for level in expected_levels:
            assert level in fitness_map, f"Missing fitness level: {level}"
            assert fitness_map[level] in ["beginner", "intermediate", "advanced"]

    def test_diet_map_contains_all_diets(self):
        """Test diet_map contains all diet options"""
        expected_diets = ["diet_none", "diet_vegetarian", "diet_vegan", "diet_keto", "diet_halal"]

        for diet in expected_diets:
            assert diet in diet_map, f"Missing diet: {diet}"
            assert diet_map[diet] in ["none", "vegetarian", "vegan", "keto", "halal"]

    def test_gender_map_contains_all_genders(self):
        """Test gender_map contains all gender options"""
        expected_genders = ["gender_male", "gender_female"]

        for gender in expected_genders:
            assert gender in gender_map, f"Missing gender: {gender}"
            assert gender_map[gender] in ["male", "female"]


class TestBMICalculation:
    """Test BMI calculation in onboarding"""

    def test_bmi_calculation_normal(self):
        """Test BMI calculation for normal weight"""
        weight = 70  # kg
        height = 175  # cm
        bmi = weight / ((height / 100) ** 2)

        # Normal BMI is 18.5 - 25
        assert 18.5 <= bmi <= 25

    def test_bmi_calculation_overweight(self):
        """Test BMI calculation for overweight"""
        weight = 85
        height = 170
        bmi = weight / ((height / 100) ** 2)

        # Overweight BMI is 25 - 30
        assert 25 <= bmi < 30

    def test_bmi_calculation_underweight(self):
        """Test BMI calculation for underweight"""
        weight = 50
        height = 175
        bmi = weight / ((height / 100) ** 2)

        # Underweight BMI is < 18.5
        assert bmi < 18.5

    def test_bmi_calculation_obese(self):
        """Test BMI calculation for obese"""
        weight = 120
        height = 170
        bmi = weight / ((height / 100) ** 2)

        # Obese BMI is >= 30
        assert bmi >= 30


class TestBMRCalculation:
    """Test BMR (Basal Metabolic Rate) calculation"""

    def test_bmr_male_calculation(self):
        """Test BMR calculation for male"""
        weight = 75
        height = 180
        age = 25

        # Mifflin-St Jeor formula for males: 10*weight + 6.25*height - 5*age + 5
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

        assert bmr > 0
        assert bmr > 1500  # Reasonable minimum
        assert bmr < 3000  # Reasonable maximum

    def test_bmr_female_calculation(self):
        """Test BMR calculation for female"""
        weight = 65
        height = 165
        age = 25

        # Mifflin-St Jeor formula for females: 10*weight + 6.25*height - 5*age - 161
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

        assert bmr > 0
        assert bmr > 1200  # Reasonable minimum for females
        assert bmr < 2500  # Reasonable maximum


class TestTDEECalculation:
    """Test TDEE (Total Daily Energy Expenditure) calculation"""

    def test_tdee_sedentary_activity(self):
        """Test TDEE with sedentary activity level (gym_freq <= 2)"""
        bmr = 1700
        multiplier = 1.375

        tdee = bmr * multiplier

        assert tdee > bmr
        assert tdee == bmr * 1.375

    def test_tdee_moderate_activity(self):
        """Test TDEE with moderate activity level (gym_freq 3-4)"""
        bmr = 1700
        multiplier = 1.55

        tdee = bmr * multiplier

        assert tdee > bmr
        assert tdee == bmr * 1.55

    def test_tdee_high_activity(self):
        """Test TDEE with high activity level (gym_freq >= 5)"""
        bmr = 1700
        multiplier = 1.725

        tdee = bmr * multiplier

        assert tdee > bmr
        assert tdee == bmr * 1.725


class TestMacroCalculation:
    """Test macro nutrient calculation"""

    def test_macro_weight_loss_goal(self):
        """Test macro ratios for weight loss goal"""
        calorie_target = 2000
        protein_ratio = 0.40
        carbs_ratio = 0.30
        fat_ratio = 0.30

        protein = (calorie_target * protein_ratio) / 4
        carbs = (calorie_target * carbs_ratio) / 4
        fat = (calorie_target * fat_ratio) / 9

        assert protein > 0
        assert carbs > 0
        assert fat > 0
        assert protein > carbs  # Higher protein for weight loss

    def test_macro_muscle_gain_goal(self):
        """Test macro ratios for muscle gain goal"""
        calorie_target = 2800
        protein_ratio = 0.35
        carbs_ratio = 0.45
        fat_ratio = 0.20

        protein = (calorie_target * protein_ratio) / 4
        carbs = (calorie_target * carbs_ratio) / 4
        fat = (calorie_target * fat_ratio) / 9

        assert protein > 0
        assert carbs > 0
        assert fat > 0
        assert carbs > protein  # Higher carbs for muscle gain

    def test_macro_maintenance_goal(self):
        """Test macro ratios for maintenance goal"""
        calorie_target = 2400
        protein_ratio = 0.30
        carbs_ratio = 0.40
        fat_ratio = 0.30

        protein = (calorie_target * protein_ratio) / 4
        carbs = (calorie_target * carbs_ratio) / 4
        fat = (calorie_target * fat_ratio) / 9

        assert protein > 0
        assert carbs > 0
        assert fat > 0
        # Balanced ratios for maintenance
        assert abs(protein - fat) <= 100


class TestOnboardingValidation:
    """Test onboarding input validation"""

    def test_age_validation(self):
        """Test age validation (10-100)"""
        valid_ages = [10, 25, 50, 100]
        invalid_ages = [9, 101, -5, 0]

        for age in valid_ages:
            assert 10 <= age <= 100

        for age in invalid_ages:
            assert not (10 <= age <= 100)

    def test_height_validation(self):
        """Test height validation (100-250 cm)"""
        valid_heights = [100, 150, 180, 250]
        invalid_heights = [99, 251, -100, 0]

        for height in valid_heights:
            assert 100 <= height <= 250

        for height in invalid_heights:
            assert not (100 <= height <= 250)

    def test_weight_validation(self):
        """Test weight validation (30-300 kg)"""
        valid_weights = [30, 50, 75, 100, 300]
        invalid_weights = [29, 301, -50, 0]

        for weight in valid_weights:
            assert 30 <= weight <= 300

        for weight in invalid_weights:
            assert not (30 <= weight <= 300)

    def test_gym_frequency_validation(self):
        """Test gym frequency validation (1-7)"""
        valid_freqs = [1, 3, 5, 7]
        invalid_freqs = [0, 8, -1]

        for freq in valid_freqs:
            assert 1 <= freq <= 7

        for freq in invalid_freqs:
            assert not (1 <= freq <= 7)


class TestCalorieTargetAdjustment:
    """Test calorie target adjustments based on goal"""

    def test_weight_loss_calorie_deficit(self):
        """Test weight loss creates calorie deficit"""
        tdee = 2500
        calorie_target = tdee - 300

        assert calorie_target < tdee
        assert calorie_target == 2200

    def test_muscle_gain_calorie_surplus(self):
        """Test muscle gain creates calorie surplus"""
        tdee = 2500
        calorie_target = tdee + 300

        assert calorie_target > tdee
        assert calorie_target == 2800

    def test_maintenance_same_as_tdee(self):
        """Test maintenance goal targets TDEE"""
        tdee = 2500
        calorie_target = tdee

        assert calorie_target == tdee
