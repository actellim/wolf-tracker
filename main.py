import configparser
import sys
from app.database import DatabaseManager
from app.ui import ConsoleUI

def main():
    """
    Main function to run the Wolf Tracker application.
    """
    # --- Configuration and Database Setup ---
    config = configparser.ConfigParser()
    try:
        if not config.read('config.ini'):
            raise FileNotFoundError("config.ini not found or is empty.")
        db_path = config.get('Paths', 'database_path')
    except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError) as e:
        print(f"Error: Could not read configuration from config.ini: {e}", file=sys.stderr)
        print("Please ensure 'config.ini' exists and contains a 'database_path' setting under the [Paths] section.", file=sys.stderr)
        sys.exit(1)

    db_manager = DatabaseManager(db_path)
    db_manager.setup()

    # --- UI and Application Logic ---
    ui = ConsoleUI()

    # Check if a user profile already exists.
    user_profile = db_manager.get_user_profile()

    if user_profile:
        print(f"Welcome back, {user_profile['user_name']}!")
    else:
        # If no profile, prompt to create one.
        print("No user profile found. Let's create one.")
        profile_data = ui.prompt_for_user_profile()
        db_manager.create_or_update_user_profile(profile_data)
        print("\nUser profile has been saved successfully.")


    # --- Cleanup ---
    db_manager.close()
    print("Wolf Tracker application finished.")

if __name__ == "__main__":
    main()
