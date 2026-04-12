import pytest
from bot.progress import progress_bar


class TestProgressBar:
    """Test progress bar visualization"""

    def test_progress_bar_full(self):
        """Test progress bar when fully filled"""
        bar = progress_bar(100, 100)
        assert "░" not in bar
        assert "█" in bar
        assert bar == "█" * 10

    def test_progress_bar_empty(self):
        """Test progress bar when empty"""
        bar = progress_bar(0, 100)
        assert "█" not in bar
        assert "░" in bar

    def test_progress_bar_half(self):
        """Test progress bar at 50% capacity"""
        bar = progress_bar(50, 100, length=10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5

    def test_progress_bar_quarter(self):
        """Test progress bar at 25% capacity"""
        bar = progress_bar(25, 100, length=8)
        filled = int(8 * (25 / 100))
        assert bar.count("█") == filled

    def test_progress_bar_overflow_capped(self):
        """Test progress bar caps at 100%"""
        bar = progress_bar(200, 100, length=10)
        assert bar == "█" * 10
        assert "░" not in bar

    def test_progress_bar_custom_length(self):
        """Test progress bar with custom length"""
        bar = progress_bar(30, 100, length=5)
        assert len(bar) == 5

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total (should not divide by zero)"""
        bar = progress_bar(0, 0)
        assert isinstance(bar, str)
        assert len(bar) == 10

    def test_progress_bar_one_character(self):
        """Test progress bar with length of 1"""
        bar = progress_bar(100, 100, length=1)
        assert bar == "█"

    def test_progress_bar_different_values(self):
        """Test progress bar with various percentage values"""
        test_cases = [
            (10, 100, 10, 1),   # 10% -> 1 filled out of 10
            (33, 100, 10, 3),   # 33% -> 3 filled out of 10
            (75, 100, 10, 7),   # 75% -> 7 filled out of 10
        ]

        for current, total, length, expected_filled in test_cases:
            bar = progress_bar(current, total, length)
            assert bar.count("█") == expected_filled
            assert len(bar) == length

    def test_progress_bar_very_small_current(self):
        """Test progress bar with very small current value"""
        bar = progress_bar(1, 1000, length=10)
        # 1/1000 = 0.001, so 0.1% -> should still show at least some indication
        assert isinstance(bar, str)
        assert len(bar) == 10

    def test_progress_bar_float_values(self):
        """Test progress bar with float values"""
        bar = progress_bar(75.5, 100.0, length=10)
        assert isinstance(bar, str)
        assert len(bar) == 10
        assert "█" in bar
