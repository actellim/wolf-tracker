
import unittest
from unittest.mock import patch, call

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

    def run_morning_prompts(self, yesterdays_intentions: str | None) -> dict:
        """
        Displays yesterday's intentions and prompts for today's morning log.
        Includes an optional weight prompt.
        """
        print("\n--- Morning Routine ---")
        if yesterdays_intentions:
            print(f"\nYesterday's intentions were: \n- {yesterdays_intentions}")

        # --- New Weight Prompt ---
        weight_lbs_str = input("Enter your weight in lbs (or press Enter to skip): ")
        weight_lbs = float(weight_lbs_str) if weight_lbs_str else None

        print("\nToday's Prompts:")
        dreams = input("Record any notable dreams: ")
        intentions = input("What are your intentions for the day? ")

        return {
            "dreams": dreams,
            "intentions": intentions,
            "weight_lbs": weight_lbs
        }

    def run_evening_prompts(self, todays_intentions: str | None) -> dict:
        """
        Prompts the user for their evening log entries (review, nutrition, workout).
        """
        print("\n--- Evening Review ---")
        if todays_intentions:
            print(f"\nToday's intentions were: \n- {todays_intentions}")
        
        review_of_intentions = input("Review your intentions. How did it go? ")
        accomplishment = input("What is one thing you did well today? ")
        mood = input("What was your overall mood today? (e.g., Happy, Sad, Productive): ")

        # Nutrition & Workout
        nutrition_data = self.prompt_for_nutrition()
        did_workout = self.prompt_for_workout()

        return {
            "review_of_intentions": review_of_intentions,
            "accomplishment": accomplishment,
            "mood": mood,
            "nutrition": nutrition_data,
            "did_workout": did_workout
        }

    def prompt_for_nutrition(self) -> list[dict]:
        """
        Prompts the user to log food items and their calories in a loop.
        """
        print("\n--- Nutrition Log ---")
        foods = []
        while True:
            food_name = input("Enter food name (or 'done' to finish): ")
            if food_name.lower() == 'done':
                break
            if not food_name:
                print("Food name cannot be empty.")
                continue
            try:
                calories = int(input(f"Enter calories for {food_name}: "))
                foods.append({"name": food_name, "calories": calories})
            except ValueError:
                print("Invalid input. Please enter a whole number for calories.")
        return foods

    def prompt_for_workout(self) -> bool:
        """
        Asks the user if they worked out today.
        """
        print("\n--- Workout Log ---")
        did_workout = input("Did you work out today? (y/n): ").lower()
        return did_workout == 'y'

    def display_calorie_summary(self, tdee: float, consumed: int, deficit: int, weight_lbs: float, weight_date: str):
        """
        Displays the final TDEE and calorie consumption summary.
        """
        print("\n--- Calorie & Energy Summary ---")
        print(f"Based on your last recorded weight of {weight_lbs:.1f} lbs on {weight_date}:")
        print(f"  - Your estimated Total Daily Energy Expenditure (TDEE) is: {tdee:,.0f} calories")
        print(f"  - You consumed approximately: {consumed:,.0f} calories")
        
        if deficit > 0:
            print(f"\nResult: You are in a caloric deficit of {deficit:,.0f} calories.")
        else:
            print(f"\nResult: You are in a caloric surplus of {-deficit:,.0f} calories.")

# --- Test Suite ---
class TestConsoleUI(unittest.TestCase):

    @patch('builtins.input', side_effect=["Test User", "180.5", "1990-01-15", "Male"])
    def test_prompt_for_user_profile(self, mock_input):
        ui = ConsoleUI()
        expected_profile = {
            "user_name": "Test User",
            "height_cm": 180.5,
            "birth_date": "1990-01-15",
            "sex_at_birth": "Male",
        }
        self.assertEqual(ui.prompt_for_user_profile(), expected_profile)

    @patch('builtins.input', side_effect=["185.5", "Flying dreams", "Write the tests"])
    @patch('builtins.print')
    def test_run_morning_prompts_with_weight(self, mock_print, mock_input):
        ui = ConsoleUI()
        yesterdays_intentions = "Finish the main feature"
        expected_log = {
            "dreams": "Flying dreams",
            "intentions": "Write the tests",
            "weight_lbs": 185.5
        }
        result = ui.run_morning_prompts(yesterdays_intentions)
        self.assertEqual(result, expected_log)
        mock_print.assert_any_call(f"\nYesterday's intentions were: \n- {yesterdays_intentions}")

    @patch('builtins.input', side_effect=["", "No dreams", "Start a new chapter"])
    @patch('builtins.print')
    def test_run_morning_prompts_skip_weight(self, mock_print, mock_input):
        ui = ConsoleUI()
        expected_log = {
            "dreams": "No dreams",
            "intentions": "Start a new chapter",
            "weight_lbs": None
        }
        self.assertEqual(ui.run_morning_prompts(None), expected_log)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=[
        "Completed them all!", "Finished the UI tests", "Productive", # Evening review
        "Oats", "350", "Protein Shake", "200", "done",              # Nutrition
        "y"                                                          # Workout
    ])
    def test_run_evening_prompts_full(self, mock_input, mock_print):
        ui = ConsoleUI()
        todays_intentions = "Finish the UI tests"
        expected_data = {
            "review_of_intentions": "Completed them all!",
            "accomplishment": "Finished the UI tests",
            "mood": "Productive",
            "nutrition": [
                {"name": "Oats", "calories": 350},
                {"name": "Protein Shake", "calories": 200}
            ],
            "did_workout": True
        }
        self.assertEqual(ui.run_evening_prompts(todays_intentions), expected_data)
        mock_print.assert_any_call(f"\nToday's intentions were: \n- {todays_intentions}")

    @patch('builtins.input', side_effect=['n'])
    def test_prompt_for_workout_no(self, mock_input):
        ui = ConsoleUI()
        self.assertFalse(ui.prompt_for_workout())

    @patch('builtins.print')
    def test_display_calorie_summary_deficit(self, mock_print):
        ui = ConsoleUI()
        ui.display_calorie_summary(tdee=2400, consumed=1900, deficit=500, weight_lbs=180.0, weight_date="2024-01-01")
        self.assertIn(call("\nResult: You are in a caloric deficit of 500 calories."), mock_print.call_args_list)

    @patch('builtins.print')
    def test_display_calorie_summary_surplus(self, mock_print):
        ui = ConsoleUI()
        ui.display_calorie_summary(tdee=2400, consumed=2600, deficit=-200, weight_lbs=180.0, weight_date="2024-01-01")
        self.assertIn(call("\nResult: You are in a caloric surplus of 200 calories."), mock_print.call_args_list)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)
