# Project Roadmap

## ✅ MVP: The Core Journaling Loop

**Goal:** Create a functional, automated daily journal. The user can set up their profile, answer morning and evening prompts, log basic nutrition and workouts, and receive a daily Markdown note. The focus is on functionality over polish.

- **[x] Phase 0: Project Setup**
    - [x] Initialize `git` repository in `~/Projects/wolf-tracker/`.
    - [x] Create and populate the `.gitignore` file.
    - [x] Create the Python virtual environment (`venv`).
    - [x] Create the complete file and folder structure (`main.py`, `app/`, etc.).
    - [x] Create the `config.ini` file with default paths.

- **[x] Phase 1: Database and Setup**
    - [x] Implement the `DatabaseManager` class in `app/database.py`.
    - [x] Implement the `.connect()`, `.close()`, and `.create_tables()` methods. The `create_tables` method should execute the entire final schema.
    - [x] Implement the `setup` command in `main.py`.
    - [x] Implement `ConsoleUI.prompt_for_user_profile()` using basic `input()` for now.
    - [x] Implement `DatabaseManager.create_or_update_user_profile()`.

- **[ ] Phase 2: Core Routines**
    - [ ] Implement the argument parsing in `main.py` for `morning` and `evening` commands.
    - [ ] **Morning Routine:**
        - [ ] Implement `DatabaseManager.get_yesterdays_intentions()`.
        - [ ] Implement `ConsoleUI.run_morning_prompts()` (using basic `input()`).
        - [ ] Implement `DatabaseManager.save_morning_log()`.
    - [ ] **Evening Routine (MVP Version):**
        - [ ] Implement `ConsoleUI.run_evening_prompts()` (using basic `input()`).
        - [ ] For nutrition, the prompt should be a simple loop: "Enter food name:", "Enter calories:". This will call `DatabaseManager.add_food_item()` and `log_nutrition_entry()`.
        - [ ] For workouts, the prompt should be simple: "Did you work out? [y/n]". If yes, ask "Which workout?" and log a static entry (the compositional logic will be built later).
        - [ ] Implement `DatabaseManager.save_evening_log()`.

- **[ ] Phase 3: Reporting & Automation**
    - [ ] Implement `DatabaseManager.get_all_data_for_date()`.
    - [ ] Implement the `MarkdownReporter` class in `app/reporting.py`.
    - [ ] Implement the `.generate_report_string()` and `.save_report()` methods.
    - [ ] Manually create and configure the two `cron` jobs to run `main.py morning` and `main.py evening`.

---

## 🚀 Version 0.1: Quality of Life & Management

**Goal:** Refine the user experience with a better UI, full management capabilities for nutrition and workouts, and intelligent data entry shortcuts.

- **[ ] UI Overhaul:**
    - [ ] Integrate the `questionary` library.
    - [ ] Replace all `input()` calls in `app/ui.py` with `questionary` prompts for menus, text, confirmations, and selections.
- **[ ] Full Management Menus:**
    - [ ] Implement the `manage` command in `main.py`.
    - [ ] Implement `ConsoleUI.manage_food_items_menu()`.
    - [ ] Implement `ConsoleUI.manage_recurring_meals_menu()` and the backend logic for creating meals from components.
    - [ ] Implement `ConsoleUI.manage_workouts_menu()` and the backend logic for creating workouts from component exercises.
- **[ ] Feature Enhancements:**
    - [ ] Implement the "Log the same meals/workout as yesterday?" feature in the evening routine.
    - [ ] Implement the TDEE/BMR calculation methods in `app/logic.py`.
    - [ ] Display the daily calorie summary (deficit/surplus) in the console at the end of the evening routine.

---

## 🛠️ Version 0.2: Robustness & Advanced Reporting

**Goal:** Make the application more resilient and powerful by adding a migration system, data safety features, and more insightful reporting.

- **[ ] Schema Migrations:**
    - [ ] Implement the lightweight migration system.
    - [ ] Add `get_schema_version()` and `set_schema_version()` to `DatabaseManager`.
    - [ ] Add the `run_migrations()` logic to the startup sequence in `main.py`.
- **[ ] Data Safety:**
    - [ ] Implement the `backup` command in `main.py` to create a timestamped copy of the database file.
- **[ ] Advanced Reporting:**
    - [ ] Add a `weekly` command to `main.py`.
    - [ ] Implement logic to gather the last 7 days of data.
    - [ ] Generate a weekly summary report in both Markdown and CSV format.
    - [ ] Implement the display-only `estimate_current_weight()` calculation and include it in daily/weekly reports.

---

## 🐺 Version 1.0: Wolf Tracker Integration

**Goal:** Integrate the full academic tracking suite and lay the groundwork for future AI-powered features.

- **[ ] Academic Feature Parity:**
    - [ ] Add CRUD methods to `DatabaseManager` for `courses`, `assignments`, `exams`, `projects`, and `project_deliverables`.
    - [ ] Add management menus to the `manage` command in `ConsoleUI` for all academic tables.
- **[ ] Daily Integration:**
    - [ ] Implement a "Dashboard" feature, triggered by `python main.py dashboard` or included in the morning routine output, that lists upcoming deadlines.
    - [ ] Add a menu in the `learning_log` prompt to optionally link a learned item to a course ELO.
- **[ ] Future-Proofing:**
    - [ ] Integrate the `sentence-transformers` library.
    - [ ] Update the database methods for `learning_log` and `expected_learning_outcomes` to automatically generate and save the vector embedding to the `description_vector` column when a new entry is created.

