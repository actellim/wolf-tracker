# Wolf Tracker

Wolf Tracker is a personal, local-first, command-line journaling application designed to foster intentionality, track health and fitness metrics, and support academic discipline. It is built to be a robust, private, and highly customizable tool for self-improvement.

The application operates through automated morning and evening routines, triggered by `cron` jobs, that guide the user through a structured process of reflection, goal-setting, and data logging.

## Core Features

*   **Automated Daily Journaling:** Morning and evening prompts to cultivate a routine of intention and reflection.
*   **Health & Fitness Tracking:** Log daily nutrition, workouts, and weight to calculate and monitor your Total Daily Energy Expenditure (TDEE).
*   **Academic Tracker:** Manage courses, assignments, exams, and projects to stay on top of academic responsibilities (planned for v1.0).
*   **Local-First Database:** All data is stored in a private SQLite database file on your local machine.
*   **Composable Data:** Define individual exercises and food items, then combine them into reusable workouts and meals for fast and efficient logging.
*   **Markdown Reporting:** Generates a clean, daily Markdown summary of your logs.

## Technology & Architecture

Wolf Tracker is built with Python and SQLite, emphasizing a clean and modular architecture that separates concerns into distinct components:

*   **`main.py`**: The entry point that handles command-line argument parsing and orchestrates the application flow.
*   **`app/database.py` (`DatabaseManager`)**: Manages all SQLite database connections and CRUD operations.
*   **`app/logic.py` (`ReportLogic`)**: Handles business logic, such as TDEE/BMR calculations.
*   **`app/ui.py` (`ConsoleUI`)**: Manages all interactive console prompts and user input.
*   **`app/reporting.py` (`MarkdownReporter`)**: Formats and saves the final daily summary reports.

## Project Roadmap

The development of Wolf Tracker is planned in several key phases:

1.  **✅ MVP (Core Journaling):** Establish the foundational features, including user setup, the basic morning/evening journaling loop, and simple, daily Markdown reporting.
2.  **🚀 v0.1 (Quality of Life):** Greatly enhance the user experience by replacing basic prompts with a polished `questionary`-based UI. Implement full management menus for creating reusable meals and workouts, and introduce TDEE calculations to the daily summary.
3.  **🛠️ v0.2 (Robustness):** Make the application more resilient with the addition of a database migration system, a data backup command, and more advanced weekly summary reports.
4.  **🐺 v1.0 (Wolf Tracker Integration):** Integrate the full suite of academic tracking features. This version will also lay the groundwork for future AI capabilities by generating vector embeddings for learning logs, enabling powerful semantic search and analysis.
