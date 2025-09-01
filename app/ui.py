import unittest
from unittest.mock import patch

class ConsoleUI:
    """Handles all user interaction via the console."""

    def prompt_for_user_profile(self) -> dict:
        """
        Prompts the user for their profile information and returns it as a dictionary.
        """
        print("--- Create or Update Your Profile ---")
        user_name = input("What is your name? ")
        height_cm = float(input("What is your height in cm? "))
        birth_date = input("What is your birth date (YYYY-MM-DD)? ") # Consider adding validation
        sex_at_birth = input("What is your sex at birth (Male/Female)? ") # For BMR calculation

        return {
            "user_name": user_name,
            "height_cm": height_cm,
            "birth_date": birth_date,
            "sex_at_birth": sex_at_birth,
        }

# --- Test Suite ---
class TestConsoleUI(unittest.TestCase):

    @patch('builtins.input', side_effect=["Test User", "180.5", "1990-01-15", "Male"])
    def test_prompt_for_user_profile(self, mock_input):
        """Tests if the user profile prompt gathers data correctly."""
        print("\nRunning test_prompt_for_user_profile...")
        ui = ConsoleUI()
        expected_profile = {
            "user_name": "Test User",
            "height_cm": 180.5,
            "birth_date": "1990-01-15",
            "sex_at_birth": "Male",
        }

        actual_profile = ui.prompt_for_user_profile()
        
        self.assertEqual(actual_profile, expected_profile)
        print("test_prompt_for_user_profile: PASSED")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
