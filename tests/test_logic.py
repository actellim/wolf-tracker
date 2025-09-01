
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the app directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.logic import ReportLogic

class TestReportLogic(unittest.TestCase):

    def setUp(self):
        """Set up a mock database manager and a sample user profile before each test."""
        self.mock_db_manager = MagicMock()
        self.logic = ReportLogic(self.mock_db_manager)
        self.sample_profile = {
            "user_name": "Test User",
            "height_cm": 180,
            "birth_date": "1990-01-15",
            "sex_at_birth": "Male"
        }

    def test_calculate_age(self):
        """Test the internal helper method for age calculation."""
        print("\nRunning test_calculate_age...")
        age = self.logic._calculate_age("1990-01-15")
        # This assertion depends on the current date, making it fragile.
        # For this test, we'll assume the current year is 2024 for predictability.
        # A better implementation would mock `date.today()`.
        from datetime import date
        today = date.today()
        expected_age = today.year - 1990 - ((today.month, today.day) < (1, 15))
        self.assertEqual(age, expected_age)
        print("test_calculate_age: PASSED")

    def test_calculate_bmr_male(self):
        """Test BMR calculation for a male profile."""
        print("\nRunning test_calculate_bmr_male...")
        weight_lbs = 180
        # BMR = (10 * 81.6466) + (6.25 * 180) - (5 * age) + 5
        # Let's assume age is 34 for this calculation
        self.logic._calculate_age = MagicMock(return_value=34)
        bmr = self.logic.calculate_bmr(self.sample_profile, weight_lbs)
        # Expected: (10 * 81.6466) + (6.25 * 180) - (5 * 34) + 5 = 816.466 + 1125 - 170 + 5 = 1776.466
        self.assertAlmostEqual(bmr, 1776.47, places=2)
        print("test_calculate_bmr_male: PASSED")

    def test_calculate_bmr_female(self):
        """Test BMR calculation for a female profile."""
        print("\nRunning test_calculate_bmr_female...")
        self.sample_profile['sex_at_birth'] = 'Female'
        weight_lbs = 135
        # BMR = (10 * 61.2349) + (6.25 * 180) - (5 * age) - 161
        # Let's assume age is 34 for this calculation
        self.logic._calculate_age = MagicMock(return_value=34)
        bmr = self.logic.calculate_bmr(self.sample_profile, weight_lbs)
        # Expected: (10 * 61.2349) + (6.25 * 180) - (5 * 34) - 161 = 612.349 + 1125 - 170 - 161 = 1406.349
        self.assertAlmostEqual(bmr, 1406.35, places=2)
        print("test_calculate_bmr_female: PASSED")

    def test_calculate_tdee(self):
        """Test the final TDEE calculation."""
        print("\nRunning test_calculate_tdee...")
        bmr = 1776.47
        activity_calories = 350
        # TDEE = (BMR * 1.2) + activity_calories
        tdee = self.logic.calculate_tdee(bmr, activity_calories)
        # Expected: (1776.47 * 1.2) + 350 = 2131.764 + 350 = 2481.764
        self.assertAlmostEqual(tdee, 2481.76, places=2)
        print("test_calculate_tdee: PASSED")

if __name__ == '__main__':
    unittest.main()
