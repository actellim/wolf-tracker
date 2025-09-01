
import unittest
import os
import sys
import configparser
import sqlite3
from unittest.mock import patch, call
from datetime import date, datetime

# Add the project root to the python path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import main
from app.database import DatabaseManager
from app.logic import ReportLogic # Import ReportLogic

class TestMainApplication(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database and config file for testing."""
        self.db_file = "test_main_app.db"
        self.config_file = "test_config.ini"

        # Create a dummy config file
        config = configparser.ConfigParser()
        config['Paths'] = {'database_path': self.db_file}
        config['Workout'] = {
            'default_workout_name': 'Default Test Workout',
            'default_workout_calories': '250'
        }
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

        # Ensure the database is clean before each test
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
            
        db_manager = DatabaseManager(self.db_file)
        db_manager.setup()
        
        self.birth_date_str = '1990-01-01'
        self.profile_data = {
            'user_name': 'Test User',
            'height_cm': 175,
            'birth_date': self.birth_date_str,
            'sex_at_birth': 'Male'
        }
        db_manager.create_or_update_user_profile(self.profile_data)
        db_manager.close()

    def tearDown(self):
        """Clean up the temporary files."""
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    @patch('builtins.print')
    @patch('main.configparser.ConfigParser')
    @patch('builtins.input')
    @patch('argparse.ArgumentParser.parse_args')
    def test_morning_routine_with_weight(self, mock_parse_args, mock_input, mock_config_parser, mock_print):
        """Test the morning routine including the new weight log feature."""
        mock_parse_args.return_value.command = 'morning'
        mock_input.side_effect = ["180.5", "My dreams", "My intentions"]
        
        mock_config_instance = mock_config_parser.return_value
        mock_config_instance.get.side_effect = lambda section, option: {
            'Paths': {'database_path': self.db_file},
            'Workout': {'default_workout_name': 'Default Test Workout'}
        }[section][option]
        mock_config_instance.getint.side_effect = lambda section, option: {
            'Workout': {'default_workout_calories': 250}
        }[section][option]
        
        main()

        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        today_str = date.today().isoformat()
        
        cursor.execute("SELECT weight_lbs FROM weight_log WHERE log_date = ?", (today_str,))
        weight_log = cursor.fetchone()
        self.assertIsNotNone(weight_log)
        self.assertEqual(weight_log['weight_lbs'], 180.5)
        
        cursor.execute("SELECT dreams, intentions FROM daily_log WHERE log_date = ?", (today_str,))
        daily_log = cursor.fetchone()
        self.assertIsNotNone(daily_log)
        self.assertEqual(daily_log['dreams'], "My dreams")
        self.assertEqual(daily_log['intentions'], "My intentions")

        conn.close()

    @patch('builtins.print')
    @patch('main.configparser.ConfigParser')
    @patch('builtins.input')
    @patch('argparse.ArgumentParser.parse_args')
    def test_evening_routine_with_tdee_report(self, mock_parse_args, mock_input, mock_config_parser, mock_print):
        """Test the full evening routine, using ReportLogic to verify calculations."""
        today_str = date.today().isoformat()
        mock_parse_args.return_value.command = 'evening'
        mock_input.side_effect = [
            "Did pretty well.", "Finished the report.", "Productive",
            "Pizza", "800", "Salad", "250", "done",
            "y"
        ]

        mock_config_instance = mock_config_parser.return_value
        mock_config_instance.get.side_effect = lambda section, option: {
            'Paths': {'database_path': self.db_file},
            'Workout': {'default_workout_name': 'Default Test Workout'}
        }[section][option]
        mock_config_instance.getint.side_effect = lambda section, option: {
            'Workout': {'default_workout_calories': 250}
        }[section][option]

        db_manager = DatabaseManager(self.db_file)
        db_manager.connect()
        db_manager.log_weight(today_str, 180.0)
        db_manager.close()
        
        logic = ReportLogic(db_manager) # Use the real logic class

        main()

        # --- 1. Database Assertions (unchanged) ---
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM daily_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        self.assertIsNotNone(log)
        self.assertEqual(log['review_of_intentions'], "Did pretty well.")

        cursor.execute("SELECT COUNT(*) FROM nutrition_log WHERE log_date = ?", (today_str,))
        self.assertEqual(cursor.fetchone()[0], 2)

        cursor.execute("SELECT w.name FROM workout_log wl JOIN workouts w ON wl.workout_id = w.workout_id WHERE wl.log_date = ?", (today_str,))
        self.assertEqual(cursor.fetchone()['name'], 'Default Test Workout')

        conn.close()

        # --- 2. TDEE Report Assertions (Refined) ---
        # Use the logic class to get the expected values
        bmr = logic.calculate_bmr(self.profile_data, 180.0)
        tdee = logic.calculate_tdee(bmr, 250) # 250 from config
        consumed = 800 + 250
        deficit = round(tdee - consumed)

        expected_calls = [
            call('\n--- Generating Daily Energy Report ---'),
            call('\n--- Calorie & Energy Summary ---'),
            call(f"Based on your last recorded weight of 180.0 lbs on {today_str}:"),
            call(f"  - Your estimated Total Daily Energy Expenditure (TDEE) is: {tdee:,.0f} calories"),
            call(f"  - You consumed approximately: {consumed:,.0f} calories"),
            call(f"\nResult: You are in a caloric deficit of {deficit:,.0f} calories.")
        ]
        
        mock_print.assert_has_calls(expected_calls, any_order=False)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
