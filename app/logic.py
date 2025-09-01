from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database import DatabaseManager


class ReportLogic:
    """Handles business logic, calculations, and data aggregation for reports."""

    def __init__(self, db_manager: "DatabaseManager"):
        """Initializes the logic class with a database manager instance."""
        self.db_manager = db_manager

    def _calculate_age(self, birth_date_str: str) -> int:
        """Helper to calculate age from a birth date string in YYYY-MM-DD format."""
        birth_date = date.fromisoformat(birth_date_str)
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def _lbs_to_kg(self, weight_lbs: float) -> float:
        """Helper to convert pounds to kilograms."""
        return weight_lbs * 0.453592

    def calculate_bmr(self, profile: dict, weight_lbs: float) -> float:
        """
        Calculates Basal Metabolic Rate using the Mifflin-St Jeor equation.
        """
        age = self._calculate_age(profile["birth_date"])
        weight_kg = self._lbs_to_kg(weight_lbs)
        height_cm = profile["height_cm"]
        sex_at_birth = profile["sex_at_birth"]

        if sex_at_birth.lower() == "male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        elif sex_at_birth.lower() == "female":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        else:
            # Default to the male formula if sex is not specified as male or female
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        return bmr

    def calculate_tdee(self, bmr: float, activity_calories: int) -> float:
        """
        Calculates Total Daily Energy Expenditure.
        Assumes a sedentary base and adds explicit activity calories.
        """
        sedentary_tdee = bmr * 1.2
        return sedentary_tdee + activity_calories

    def estimate_current_weight(self, last_measured_weight: float, calorie_logs: list) -> float:
        """
        Calculates an estimated current weight based on the last known measurement
        and the calorie surplus/deficit since that date. THIS IS FOR DISPLAY ONLY.
        """
        # This will be implemented in a future step.
        pass

    def get_daily_summary(self, log_date: str) -> dict:
        """
        Orchestrates the creation of the final data summary for a given day.
        """
        # This will be implemented in a future step.
        pass
