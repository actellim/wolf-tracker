import sqlite3
from datetime import date, timedelta

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
            return dict(row)
        return None

    # --- Daily Log Methods ---
    def ensure_daily_log_exists(self, log_date: str):
        """Creates a daily_log entry for the given date if one doesn't already exist."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO daily_log (log_date) VALUES (?)", (log_date,))
        self.conn.commit()

    def save_morning_log(self, log_date: str, dreams: str, intentions: str):
        """Saves the morning-specific data to the daily_log."""
        self.ensure_daily_log_exists(log_date)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE daily_log
            SET dreams = ?, intentions = ?
            WHERE log_date = ?
        """, (dreams, intentions, log_date))
        self.conn.commit()

    def save_evening_log(self, log_date: str, review: str, accomplishment: str, mood: str):
        """Saves the evening-specific data to the daily_log."""
        self.ensure_daily_log_exists(log_date)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE daily_log
            SET review_of_intentions = ?, accomplishment = ?, mood = ?
            WHERE log_date = ?
        """, (review, accomplishment, mood, log_date))
        self.conn.commit()
    
    def get_yesterdays_intentions(self, today_date: str) -> str | None:
        """Fetches the intentions from the previous day's log."""
        yesterday = date.fromisoformat(today_date) - timedelta(days=1)
        yesterday_str = yesterday.isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT intentions FROM daily_log WHERE log_date = ?", (yesterday_str,))
        row = cursor.fetchone()
        
        if row and row['intentions']:
            return row['intentions']
        return None

    def get_todays_intentions(self, today_date: str) -> str | None:
        """Fetches the intentions from today's log."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT intentions FROM daily_log WHERE log_date = ?", (today_date,))
        row = cursor.fetchone()
        
        if row and row['intentions']:
            return row['intentions']
        return None

    def clear_morning_data_for_date(self, log_date: str):
        """
        Clears the morning-specific fields (dreams, intentions) from the daily_log
        for a specific date to allow for overwriting.
        """
        cursor = self.conn.cursor()
        
        # Clear the morning-specific fields in the main daily_log table
        cursor.execute("""
            UPDATE daily_log
            SET dreams = NULL, intentions = NULL
            WHERE log_date = ?
        """, (log_date,))
        
        self.conn.commit()

    def clear_evening_data_for_date(self, log_date: str):
        """
        Clears all nutrition and workout logs for a specific date to allow for overwriting.
        It also clears the evening review fields from the daily_log.
        """
        cursor = self.conn.cursor()
        # Clear related logs that reference daily_log via foreign key
        cursor.execute("DELETE FROM nutrition_log WHERE log_date = ?", (log_date,))
        cursor.execute("DELETE FROM workout_log WHERE log_date = ?", (log_date,))
        
        # Clear the evening-specific fields in the main daily_log table
        cursor.execute("""
            UPDATE daily_log
            SET review_of_intentions = NULL, accomplishment = NULL, mood = NULL
            WHERE log_date = ?
        """, (log_date,))
        
        self.conn.commit()

    # --- Nutrition Methods ---
    def add_food_item(self, name: str, calories: int) -> int:
        """Adds a new food to the food_items table if it doesn't exist. Returns the food_id."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO food_items (name, calories) VALUES (?, ?)", (name, calories))
        self.conn.commit()
        cursor.execute("SELECT food_id FROM food_items WHERE name = ?", (name,))
        return cursor.fetchone()['food_id']

    def get_all_food_items(self) -> list[dict]:
        """Retrieves all food items."""
        pass

    def log_nutrition_entry(self, log_date: str, food_id: int, quantity: float = 1.0):
        """Adds a row to the nutrition_log table."""
        self.ensure_daily_log_exists(log_date)
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO nutrition_log (log_date, food_id, quantity) VALUES (?, ?, ?)", (log_date, food_id, quantity))
        self.conn.commit()

    # --- Workout Methods ---
    def get_meal_components(self, meal_id: int) -> list[dict]:
        """Retrieves all food_ids and quantities for a given recurring meal."""
        pass

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

    def add_or_get_workout(self, workout_name: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO workouts (name) VALUES (?)", (workout_name,))
        self.conn.commit()
        cursor.execute("SELECT workout_id FROM workouts WHERE name = ?", (workout_name,))
        return cursor.fetchone()['workout_id']

    def add_or_get_exercise(self, name: str, calories_burned: int) -> int:
        """Adds an exercise to the exercises table if it doesn't exist. Returns the exercise_id."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO exercises (name, calories_burned) VALUES (?, ?)", (name, calories_burned))
        self.conn.commit()
        cursor.execute("SELECT exercise_id FROM exercises WHERE name = ?", (name,))
        return cursor.fetchone()['exercise_id']

    def log_workout(self, log_date: str, workout_id: int):
        """Logs that a specific workout was performed on a given date."""
        self.ensure_daily_log_exists(log_date)
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO workout_log (log_date, workout_id) VALUES (?, ?)", (log_date, workout_id))
        self.conn.commit()

    # --- Calorie Tracking Methods ---

    def log_weight(self, log_date: str, weight_lbs: float):
        """Logs a weight entry for a specific date."""
        self.ensure_daily_log_exists(log_date)
        cursor = self.conn.cursor()
        # Use INSERT OR REPLACE to handle cases where a weight is re-entered for the same day.
        # This requires a unique constraint on log_date in the weight_log table.
        # Let's add that constraint to the schema if it's not there.
        # For now, we'll just delete the old one if it exists.
        cursor.execute("DELETE FROM weight_log WHERE log_date = ?", (log_date,))
        cursor.execute("INSERT INTO weight_log (log_date, weight_lbs) VALUES (?, ?)", (log_date, weight_lbs))
        self.conn.commit()

    def get_most_recent_weight(self) -> dict | None:
        """Retrieves the most recent weight entry from the log."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT weight_lbs, log_date FROM weight_log ORDER BY log_date DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_total_consumed_calories_for_date(self, log_date: str) -> int:
        """Calculates the sum of all calories from food logged on a specific date."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SUM(fi.calories * nl.quantity)
            FROM nutrition_log nl
            JOIN food_items fi ON nl.food_id = fi.food_id
            WHERE nl.log_date = ?
        """, (log_date,))
        result = cursor.fetchone()[0]
        return int(result) if result is not None else 0

    def get_total_workout_calories_for_date(self, log_date: str) -> int:
        """
        Calculates the sum of all calories burned from workouts logged on a specific date.
        This is a complex query that joins the log with workouts and their component exercises.
        For now, we assume a simple 'Default Workout' and will need to enhance the schema
        and exercise logging to make this truly dynamic.
        
        NOTE: This implementation is a placeholder. A full implementation requires exercises
        to be linked to workouts and have calorie values. We will simulate this for now.
        The `exercises` table needs `calories_burned`.
        """
        cursor = self.conn.cursor()
        # This query is complex and depends on a fully populated compositional fitness system.
        # We will assume a simplified version where the 'Default Workout' has a hardcoded calorie value
        # by creating an exercise with the same name and linking it.
        # This is a stand-in for a full workout_components implementation.
        cursor.execute("""
            SELECT SUM(e.calories_burned)
            FROM workout_log wl
            JOIN workouts w ON wl.workout_id = w.workout_id
            JOIN exercises e ON e.name = w.name -- Simplified assumption
            WHERE wl.log_date = ?
        """, (log_date,))
        result = cursor.fetchone()[0]
        return int(result) if result is not None else 0

    def get_all_data_for_date(self, log_date: str) -> dict:
        """
        Fetches all data related to a specific date from multiple tables.
        Returns a dictionary containing keys like 'daily_log', 'nutrition', 'workout', 'weight'.
        """
        pass

if __name__ == "__main__":
    import os
    
    DB_FILE = "test_wolf_tracker.db"
 
    def setup_database():
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        db_manager = DatabaseManager(DB_FILE)
        db_manager.setup()
        return db_manager

    def test_setup():
        print("\nRunning test_setup...")
        db_manager = setup_database()
        assert db_manager.conn is not None
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profile';")
        assert cursor.fetchone() is not None
        db_manager.close()
        print("test_setup: PASSED") 

    def test_database_connection():
        print("Running test_database_connection...")
        db_manager = DatabaseManager(DB_FILE)
        db_manager.connect()
        assert db_manager.conn is not None
        db_manager.close()
        print("test_database_connection: PASSED")

    def test_table_creation():
        print("\nRunning test_table_creation...")
        db_manager = setup_database()
        cursor = db_manager.conn.cursor()
        tables = ["user_profile", "daily_log", "weight_log", "food_items", "exercises", "workouts", "courses", "assignments"]
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            assert cursor.fetchone() is not None, f"Table {table} not created."
        db_manager.close()
        print("test_table_creation: PASSED")

    def test_user_profile_operations():
        print("\nRunning test_user_profile_operations...")
        db_manager = setup_database()
        assert db_manager.get_user_profile() is None
        profile_data = {'user_name': "Test User", 'height_cm': 180.5, 'birth_date': "1990-01-15", 'sex_at_birth': "Male"}
        db_manager.create_or_update_user_profile(profile_data)
        retrieved = db_manager.get_user_profile()
        assert retrieved is not None and retrieved['user_name'] == "Test User"
        today_str = date.today().isoformat()
        db_manager.save_morning_log(today_str, "dreams today", "intentions for today")
        assert db_manager.get_todays_intentions(today_str) == "intentions for today"
        db_manager.close()
        print("test_user_profile_operations: PASSED")

    def test_daily_log_operations():
        print("\nRunning test_daily_log_operations...")
        db_manager = setup_database()
        today_str = date.today().isoformat()
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()
        db_manager.save_morning_log(yesterday_str, "dreams", "yesterday_intentions")
        assert db_manager.get_yesterdays_intentions(today_str) == "yesterday_intentions"
        db_manager.save_evening_log(today_str, "review", "accomplishment", "mood")
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT * FROM daily_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        assert log['review_of_intentions'] == "review"
        db_manager.close()
        print("test_daily_log_operations: PASSED")

    def test_nutrition_operations():
        print("\nRunning test_nutrition_operations...")
        db_manager = setup_database()
        today_str = date.today().isoformat()
        food_id_1 = db_manager.add_food_item("Apple", 95)
        db_manager.log_nutrition_entry(today_str, food_id_1)
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT * FROM nutrition_log WHERE log_date = ?", (today_str,))
        logs = cursor.fetchall()
        assert len(logs) == 1
        db_manager.close()
        print("test_nutrition_operations: PASSED")

    def test_workout_operations():
        print("\nRunning test_workout_operations...")
        db_manager = setup_database()
        today_str = date.today().isoformat()
        workout_id = db_manager.add_or_get_workout("Default Workout")
        db_manager.log_workout(today_str, workout_id)
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT * FROM workout_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        assert log is not None
        db_manager.close()
        print("test_workout_operations: PASSED")

    def test_overwrite_evening_data():
        print("\\nRunning test_overwrite_evening_data...")
        db_manager = setup_database()
        today_str = date.today().isoformat()

        # --- First Pass ---
        db_manager.ensure_daily_log_exists(today_str)
        db_manager.save_evening_log(today_str, "Initial review", "Initial accomplishment", "Okay")
        food_id_1 = db_manager.add_food_item("Old Food", 100)
        db_manager.log_nutrition_entry(today_str, food_id_1)
        workout_id_1 = db_manager.add_or_get_workout("Old Workout")
        db_manager.log_workout(today_str, workout_id_1)
        
        # --- Verification of First Pass ---
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT * FROM nutrition_log WHERE log_date = ?", (today_str,))
        assert len(cursor.fetchall()) == 1
        cursor.execute("SELECT * FROM workout_log WHERE log_date = ?", (today_str,))
        assert len(cursor.fetchall()) == 1
        cursor.execute("SELECT * FROM daily_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        assert log['accomplishment'] == "Initial accomplishment"

        # --- Clear and Second Pass ---
        db_manager.clear_evening_data_for_date(today_str)
        db_manager.save_evening_log(today_str, "Updated review", "Updated accomplishment", "Great")
        food_id_2 = db_manager.add_food_item("New Food", 200)
        db_manager.log_nutrition_entry(today_str, food_id_2)
        db_manager.log_nutrition_entry(today_str, food_id_2) # Add two entries
        workout_id_2 = db_manager.add_or_get_workout("New Workout")
        db_manager.log_workout(today_str, workout_id_2)

        # --- Final Verification ---
        cursor.execute("SELECT fi.name FROM nutrition_log nl JOIN food_items fi ON nl.food_id = fi.food_id WHERE nl.log_date = ?", (today_str,))
        nutrition_logs = cursor.fetchall()
        assert len(nutrition_logs) == 2
        assert nutrition_logs[0]['name'] == "New Food"
        
        cursor.execute("SELECT w.name FROM workout_log wl JOIN workouts w ON wl.workout_id = w.workout_id WHERE wl.log_date = ?", (today_str,))
        workout_logs = cursor.fetchall()
        assert len(workout_logs) == 1
        assert workout_logs[0]['name'] == "New Workout"

        cursor.execute("SELECT * FROM daily_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        assert log['accomplishment'] == "Updated accomplishment"
        assert log['review_of_intentions'] == "Updated review"

        db_manager.close()
        print("test_overwrite_evening_data: PASSED")

    def test_overwrite_morning_data():
        print("\\nRunning test_overwrite_morning_data...")
        db_manager = setup_database()
        today_str = date.today().isoformat()

        # --- First Pass ---
        db_manager.save_morning_log(today_str, "Initial dream", "Initial intention")
        
        # --- Verification of First Pass ---
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT * FROM daily_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        assert log['dreams'] == "Initial dream"
        assert log['intentions'] == "Initial intention"

        # --- Clear and Second Pass ---
        db_manager.clear_morning_data_for_date(today_str)
        db_manager.save_morning_log(today_str, "Updated dream", "Updated intention")

        # --- Final Verification ---
        cursor.execute("SELECT * FROM daily_log WHERE log_date = ?", (today_str,))
        log = cursor.fetchone()
        assert log['dreams'] == "Updated dream"
        assert log['intentions'] == "Updated intention"
        
        db_manager.close()
        print("test_overwrite_morning_data: PASSED")

    def test_calorie_tracking_operations():
        print("\\nRunning test_calorie_tracking_operations...")
        db_manager = setup_database()
        today_str = date.today().isoformat()
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()

        # 1. Log and retrieve weight
        db_manager.log_weight(yesterday_str, 182.5)
        db_manager.log_weight(today_str, 180.0)
        recent_weight = db_manager.get_most_recent_weight()
        assert recent_weight['weight_lbs'] == 180.0

        # 2. Log food and calculate consumed calories
        food1_id = db_manager.add_food_item("Pizza Slice", 350)
        food2_id = db_manager.add_food_item("Salad", 150)
        db_manager.log_nutrition_entry(today_str, food1_id, 2)  # 2 slices of pizza
        db_manager.log_nutrition_entry(today_str, food2_id, 1)  # 1 salad
        total_calories = db_manager.get_total_consumed_calories_for_date(today_str)
        assert total_calories == (350 * 2) + 150  # Should be 850

        # 3. Log workout and calculate burned calories
        # This part requires a more complex setup that we simulate here.
        # We need an exercise that matches our logged workout's name.
        workout_name = "Morning Run"
        db_manager.add_or_get_exercise(name=workout_name, calories_burned=300)
        workout_id = db_manager.add_or_get_workout(workout_name)
        db_manager.log_workout(today_str, workout_id)
        
        burned_calories = db_manager.get_total_workout_calories_for_date(today_str)
        assert burned_calories == 300

        db_manager.close()
        print("test_calorie_tracking_operations: PASSED")

    try:
        test_setup()
        test_database_connection()
        test_table_creation()
        test_user_profile_operations()
        test_daily_log_operations()
        test_nutrition_operations()
        test_workout_operations()
        test_overwrite_evening_data()
        test_overwrite_morning_data()
        test_calorie_tracking_operations()
        print("\nAll tests completed successfully!")

    finally:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print(f"\nCleaned up {DB_FILE}.")
