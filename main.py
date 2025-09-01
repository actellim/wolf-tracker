import configparser
import sys
import argparse
from datetime import date
from app.database import DatabaseManager
from app.ui import ConsoleUI
from app.logic import ReportLogic

def main():
    """
    Main function to run the Wolf Tracker application.
    """
    # --- Configuration and Setup ---
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        db_path = config.get('Paths', 'database_path')
        default_workout_name = config.get('Workout', 'default_workout_name')
        # New: Get the default calories for the placeholder workout
        default_workout_calories = config.getint('Workout', 'default_workout_calories')
    except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError, ValueError) as e:
        print(f"Error reading config.ini: {e}", file=sys.stderr)
        sys.exit(1)

    db_manager = DatabaseManager(db_path)
    db_manager.setup()
    ui = ConsoleUI()
    logic = ReportLogic(db_manager) # Instantiate the logic class

    # --- User Profile Handling ---
    user_profile = db_manager.get_user_profile()
    if not user_profile:
        print("No user profile found. Let's create one.")
        profile_data = ui.prompt_for_user_profile()
        db_manager.create_or_update_user_profile(profile_data)
        user_profile = db_manager.get_user_profile()
        print("\nUser profile saved.")

    print(f"\nWelcome back, {user_profile['user_name']}!")

    # --- Command Parsing ---
    parser = argparse.ArgumentParser(description="Wolf Tracker - A personal journaling tool.")
    parser.add_argument('command', nargs='?', choices=['morning', 'evening'], help="The routine to run.")
    args = parser.parse_args()

    # --- Main Application Logic ---
    today_str = date.today().isoformat()

    if args.command == 'morning':
        db_manager.clear_morning_data_for_date(today_str)
        yesterdays_intentions = db_manager.get_yesterdays_intentions(today_str)
        morning_data = ui.run_morning_prompts(yesterdays_intentions)
        db_manager.save_morning_log(today_str, morning_data['dreams'], morning_data['intentions'])
        
        # New: Log weight if provided
        if morning_data.get('weight_lbs') is not None:
            db_manager.log_weight(today_str, morning_data['weight_lbs'])
            print(f"Weight of {morning_data['weight_lbs']} lbs logged for today.")

        print("\nMorning log saved successfully!")

    elif args.command == 'evening':
        db_manager.clear_evening_data_for_date(today_str)
        todays_intentions = db_manager.get_todays_intentions(today_str)
        evening_data = ui.run_evening_prompts(todays_intentions)
        
        # Save general evening review data
        db_manager.save_evening_log(
            today_str,
            evening_data['review_of_intentions'],
            evening_data['accomplishment'],
            evening_data['mood']
        )

        # Process and save nutrition data
        for food_item in evening_data.get('nutrition', []):
            food_id = db_manager.add_food_item(food_item['name'], food_item['calories'])
            db_manager.log_nutrition_entry(today_str, food_id)

        # Process and save workout data
        if evening_data.get('did_workout'):
            # This is a placeholder for the full compositional system.
            # We create a generic exercise with the default calorie value.
            db_manager.add_or_get_exercise(name=default_workout_name, calories_burned=default_workout_calories)
            workout_id = db_manager.add_or_get_workout(default_workout_name)
            db_manager.log_workout(today_str, workout_id)
            print(f"\nLogged '{default_workout_name}'.")

        print("\nEvening log and activities saved successfully!")

        # --- New: TDEE Calculation and Summary --- #
        print("\n--- Generating Daily Energy Report ---")
        weight_data = db_manager.get_most_recent_weight()
        if not weight_data:
            print("\nCannot calculate TDEE without a weight entry. Please log your weight.", file=sys.stderr)
            db_manager.close()
            sys.exit(1)

        # Fetch data needed for TDEE
        consumed_calories = db_manager.get_total_consumed_calories_for_date(today_str)
        activity_calories = db_manager.get_total_workout_calories_for_date(today_str)
        
        # Perform the calculations
        bmr = logic.calculate_bmr(user_profile, weight_data['weight_lbs'])
        tdee = logic.calculate_tdee(bmr, activity_calories)
        deficit = round(tdee - consumed_calories)

        # Display the final summary
        ui.display_calorie_summary(
            tdee=tdee, 
            consumed=consumed_calories, 
            deficit=deficit, 
            weight_lbs=weight_data['weight_lbs'],
            weight_date=weight_data['log_date']
        )

    elif not args.command:
        print("\nRun with 'morning' or 'evening' to log your activities.")

    # --- Cleanup ---
    db_manager.close()
    print("\nWolf Tracker application finished.")

if __name__ == "__main__":
    main()
