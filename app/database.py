import sqlite3

class DatabaseManager:
    """Handles all database connections and CRUD operations."""

    def __init__(self, db_path: str):
        """Initializes the DatabaseManager with the path to the SQLite database."""
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establishes the database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def setup(self):
        """Connects to the database and creates the necessary tables."""
        self.connect()
        self.create_tables()

    def create_tables(self):
        """Executes the full SQL schema to create all tables if they don't exist."""
        if not self.conn:
            raise Exception("Database not connected. Call connect() before creating tables.")
        
        schema = """
-- SQL Schema for Wolf Tracker (Journaling & Academic) - Final Version
-- Adapted for SQLite3
-- --------------------------------------------------------------------

--
-- Table: schema_version
-- Purpose: Tracks the current version of the database schema to handle migrations.
--
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

--
-- Table: user_profile
-- Purpose: Store semi-permanent user data for TDEE calculations. Assumes a single user.
--
CREATE TABLE IF NOT EXISTS user_profile (
    profile_id INTEGER PRIMARY KEY,
    user_name TEXT,
    height_cm REAL NOT NULL,
    birth_date TEXT NOT NULL, -- YYYY-MM-DD format
    sex_at_birth TEXT NOT NULL -- 'Male' or 'Female' for BMR formulas
);

--
-- Table: daily_log
-- Purpose: The central anchor for a single day's summary events.
--
CREATE TABLE IF NOT EXISTS daily_log (
    log_date TEXT PRIMARY KEY, -- YYYY-MM-DD format, ensures one log summary per day
    dreams TEXT,
    intentions TEXT,
    review_of_intentions TEXT,
    accomplishment TEXT, -- One thing done well
    mood TEXT
);

--
-- Table: weight_log
-- Purpose: Track discrete weight entries over time.
--
CREATE TABLE IF NOT EXISTS weight_log (
    weight_id INTEGER PRIMARY KEY,
    log_date TEXT NOT NULL,
    weight_lbs REAL NOT NULL,
    FOREIGN KEY (log_date) REFERENCES daily_log (log_date) ON DELETE CASCADE
);

-- ======================================================
-- Learning & Vector Support
-- ======================================================

CREATE TABLE IF NOT EXISTS learning_log (
    learning_id INTEGER PRIMARY KEY,
    log_date TEXT NOT NULL,
    description TEXT NOT NULL,
    description_vector BLOB, -- For storing vector embeddings as bytes
    FOREIGN KEY (log_date) REFERENCES daily_log (log_date) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expected_learning_outcomes (
    elo_id INTEGER PRIMARY KEY,
    course_id TEXT NOT NULL,
    description TEXT NOT NULL,
    description_vector BLOB, -- For storing vector embeddings as bytes
    FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
);

-- ======================================================
-- Nutrition Tracking System
-- ======================================================

CREATE TABLE IF NOT EXISTS food_items (
    food_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    calories INTEGER NOT NULL,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL
);

CREATE TABLE IF NOT EXISTS recurring_meals (
    meal_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recurring_meal_components (
    meal_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity REAL NOT NULL DEFAULT 1,
    PRIMARY KEY (meal_id, food_id),
    FOREIGN KEY (meal_id) REFERENCES recurring_meals (meal_id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items (food_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nutrition_log (
    nutrition_id INTEGER PRIMARY KEY,
    log_date TEXT NOT NULL,
    food_id INTEGER NOT NULL,
    quantity REAL NOT NULL DEFAULT 1,
    FOREIGN KEY (log_date) REFERENCES daily_log (log_date) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items (food_id)
);

-- ======================================================
-- Compositional Fitness Tracking System
-- ======================================================

--
-- Table: exercises
-- Purpose: Defines individual, reusable exercises with their caloric value.
--
CREATE TABLE IF NOT EXISTS exercises (
    exercise_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    calories_burned INTEGER NOT NULL -- Or REAL if you want decimal precision
);

--
-- Table: workouts
-- Purpose: Defines the name of a workout routine. The calorie total is calculated, not stored.
--
CREATE TABLE IF NOT EXISTS workouts (
    workout_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE -- e.g., "Workout A", "Leg Day"
);

--
-- Table: workout_components
-- Purpose: A junction table linking workouts to their component exercises (Many-to-Many).
--
CREATE TABLE IF NOT EXISTS workout_components (
    workout_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    PRIMARY KEY (workout_id, exercise_id),
    FOREIGN KEY (workout_id) REFERENCES workouts (workout_id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE
);

--
-- Table: workout_log
-- Purpose: A simple log of which workout was completed on a given day. (This table remains the same).
--
CREATE TABLE IF NOT EXISTS workout_log (
    workout_log_id INTEGER PRIMARY KEY,
    log_date TEXT NOT NULL,
    workout_id INTEGER NOT NULL,
    FOREIGN KEY (log_date) REFERENCES daily_log (log_date) ON DELETE CASCADE,
    FOREIGN KEY (workout_id) REFERENCES workouts (workout_id)
);

-- ======================================================
-- Wolf Tracker Academic Schema
-- ======================================================

CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    instructor TEXT,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY,
    course_id TEXT NOT NULL,
    due_date TEXT NOT NULL,
    turned_in INTEGER NOT NULL DEFAULT 0, -- 0 for false, 1 for true
    date_turned_in TEXT,
    worth_weight REAL NOT NULL,
    mark REAL,
    description TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exams (
    exam_id INTEGER PRIMARY KEY,
    course_id TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    worth_weight REAL NOT NULL,
    mark REAL,
    description TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY,
    course_id TEXT NOT NULL,
    due_date TEXT NOT NULL,
    turned_in INTEGER NOT NULL DEFAULT 0,
    date_turned_in TEXT,
    worth_weight REAL NOT NULL,
    mark REAL,
    description TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_deliverables (
    deliverable_id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    due_date TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    date_done TEXT,
    description TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
);
        """
        self.conn.executescript(schema)

    def get_schema_version(self) -> int:
        """Retrieves the current schema version from the database."""
        pass

    def set_schema_version(self, version: int):
        """Updates the schema version number."""
        pass

    # --- User Profile Methods ---
    def create_or_update_user_profile(self, profile_data: dict):
        """Saves or updates the single user profile."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (profile_id, user_name, height_cm, birth_date, sex_at_birth)
            VALUES (1, ?, ?, ?, ?)
        """, (profile_data['user_name'], profile_data['height_cm'], profile_data['birth_date'], profile_data['sex_at_birth']))
        self.conn.commit()

    def get_user_profile(self) -> dict | None:
        """Retrieves the user profile. Returns a dict or None if not found."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_name, height_cm, birth_date, sex_at_birth FROM user_profile WHERE profile_id = 1")
        row = cursor.fetchone()
        if row:
            # Convert the sqlite3.Row object to a dictionary
            return dict(row)
        return None

    # --- Daily Log Methods ---
    def ensure_daily_log_exists(self, log_date: str):
        """Creates a daily_log entry for the given date if one doesn't already exist."""
        pass

    def save_morning_log(self, log_date: str, dreams: str, intentions: str):
        """Saves the morning-specific data to the daily_log."""
        pass

    def save_evening_log(self, log_date: str, review: str, accomplishment: str, mood: str):
        """Saves the evening-specific data to the daily_log."""
        pass
    
    def get_yesterdays_intentions(self, today_date: str) -> str:
        """Fetches the intentions from the previous day's log."""
        pass

    # --- Nutrition Methods ---
    def add_food_item(self, food_data: dict) -> int:
        """Adds a new food to the food_items table."""
        pass

    def get_all_food_items(self) -> list[dict]:
        """Retrieves all food items."""
        pass

    def log_nutrition_entry(self, log_date: str, food_id: int, quantity: float):
        """Adds a row to the nutrition_log table."""
        pass
        
    def get_meal_components(self, meal_id: int) -> list[dict]:
        """Retrieves all food_ids and quantities for a given recurring meal."""
        pass

    # --- NEW Workout Methods ---
    def add_exercise(self, name: str, calories: int) -> int:
        """Adds a single exercise to the exercises table."""
        pass



    def get_all_exercises(self) -> list[dict]:
        """Retrieves all defined exercises."""
        pass

    def create_workout(self, name: str) -> int:
        """Creates a new workout in the workouts table and returns its ID."""
        pass

    def get_all_workouts(self) -> list[dict]:
        """Retrieves all defined workouts."""
        pass
        
    def add_exercise_to_workout(self, workout_id: int, exercise_id: int):
        """Links an exercise to a workout in the workout_components table."""
        pass
        
    def get_workout_calorie_sum(self, workout_id: int) -> int:
        """
        Calculates the total calorie burn for a workout by summing its
        component exercises directly in the database.
        """
        pass

    # --- Data Retrieval for Reporting ---
    def get_all_data_for_date(self, log_date: str) -> dict:
        """
        Fetches all data related to a specific date from multiple tables.
        Returns a dictionary containing keys like 'daily_log', 'nutrition', 'workout', 'weight'.
        """
        pass

if __name__ == "__main__":
    import os
    
    # Define the database file for testing
    DB_FILE = "test_wolf_tracker.db"
    
    # Ensure the old database file is removed before testing
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    # --- Test Suite ---

    def test_setup():
        """Tests the setup method."""
        print("\nRunning test_setup...")
        db_manager = DatabaseManager(DB_FILE)
        db_manager.setup()
        assert db_manager.conn is not None, "Connection should be established."
        # Check if a table exists to confirm create_tables was called
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profile';")
        assert cursor.fetchone() is not None, "Table 'user_profile' should exist after setup."
        db_manager.close()
        print("test_setup: PASSED")
    
    def test_database_connection():
        """Tests the connect and close methods."""
        print("Running test_database_connection...")
        db_manager = DatabaseManager(DB_FILE)
        db_manager.connect()
        assert db_manager.conn is not None, "Connection should not be None after connect()"
        db_manager.close()
        # To truly check if it's closed, we could try a small operation
        # but for now, we'll trust the close method. A more robust test
        # might try to fetch from a closed connection and expect an error.
        print("test_database_connection: PASSED")

    def test_table_creation():
        """Tests the create_tables method."""
        print("\nRunning test_table_creation...")
        db_manager = DatabaseManager(DB_FILE)
        db_manager.connect()
        
        # Test create_tables without a connection
        unconnected_manager = DatabaseManager(DB_FILE)
        try:
            unconnected_manager.create_tables()
            assert False, "Should have raised an exception for creating tables on a disconnected db."
        except Exception as e:
            print(f"Caught expected exception: {e}")
            assert "Database not connected" in str(e)

        db_manager.create_tables()
        cursor = db_manager.conn.cursor()
        
        # Verify a few tables exist to be confident
        tables_to_check = [
            "user_profile", "daily_log", "weight_log", "food_items",
            "exercises", "workouts", "courses", "assignments"
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            assert cursor.fetchone() is not None, f"Table '{table}' should have been created."
        
        db_manager.close()
        print("test_table_creation: PASSED")

    def test_user_profile_operations():
        """Tests creating, updating, and retrieving the user profile."""
        print("\nRunning test_user_profile_operations...")
        db_manager = DatabaseManager(DB_FILE)
        db_manager.connect()
        db_manager.create_tables() # Ensure tables are there

        # 1. Test retrieval when no profile exists
        retrieved_profile = db_manager.get_user_profile()
        assert retrieved_profile is None, "Should return None when no profile exists."

        # 2. Create the profile
        profile_data = {
            'user_name': "Test User",
            'height_cm': 180.5,
            'birth_date': "1990-01-15",
            'sex_at_birth': "Male"
        }
        db_manager.create_or_update_user_profile(profile_data)

        # 3. Retrieve and verify
        retrieved_profile = db_manager.get_user_profile()
        assert retrieved_profile is not None, "Profile should exist after creation."
        # Note: The 'profile_id' is not selected in get_user_profile
        assert retrieved_profile['user_name'] == "Test User"
        assert retrieved_profile['height_cm'] == 180.5
        assert retrieved_profile['birth_date'] == "1990-01-15"
        assert retrieved_profile['sex_at_birth'] == "Male"
        
        # 4. Update the profile
        updated_profile_data = {
            'user_name': "Test User Updated",
            'height_cm': 181.0,
            'birth_date': "1990-01-16",
            'sex_at_birth': "Female"
        }
        db_manager.create_or_update_user_profile(updated_profile_data)
        
        # 5. Retrieve and verify update
        retrieved_updated_profile = db_manager.get_user_profile()
        assert retrieved_updated_profile['user_name'] == "Test User Updated"
        assert retrieved_updated_profile['height_cm'] == 181.0
        assert retrieved_updated_profile['birth_date'] == "1990-01-16"
        assert retrieved_updated_profile['sex_at_birth'] == "Female"
        
        db_manager.close()
        print("test_user_profile_operations: PASSED")
        
    # --- Execute Tests ---
    try:
        test_setup()
        test_database_connection()
        test_table_creation()
        test_user_profile_operations()
        
        print("\nAll tests completed successfully!")
        
    finally:
        # Clean up the test database file
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print(f"\nCleaned up {DB_FILE}.")
