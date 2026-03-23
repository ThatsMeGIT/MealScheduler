from __future__ import annotations

import random
import threading
from datetime import datetime, timedelta

from backend.app.domain.models import DAY_KEYS, MEAL_KEYS, Ingredient, MealSlot, PlannedMeal, Recipe, WeeklyPlan
from backend.app.infrastructure.repository import MealRepository


class WeeklyPlanService:
    def __init__(self, repository: MealRepository) -> None:
        self.repository = repository
        self._scheduler_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def get_current_plan(self) -> WeeklyPlan | None:
        return self.repository.get_weekly_plan(self._current_week_start().isoformat())

    def create_or_refresh_current_plan(self, force: bool = False) -> WeeklyPlan:
        week_start_date = self._current_week_start()
        existing = self.repository.get_weekly_plan(week_start_date.isoformat())
        if existing and not force:
            return existing
        recipes = self.repository.list_recipes()
        if not recipes:
            raise ValueError("Mindestens ein Rezept wird benötigt")
        slots = self._active_slots(self.repository.get_settings(), week_start_date)
        if not slots:
            raise ValueError("Es ist kein Mahlzeiten-Slot aktiviert")
        chosen_recipes = self._pick_recipes(recipes, len(slots))
        meals: list[PlannedMeal] = []
        ingredients: list[Ingredient] = []
        for slot, recipe in zip(slots, chosen_recipes):
            meals.append(
                PlannedMeal(
                    date=slot.date.isoformat(),
                    day_name=slot.day_name,
                    meal_type=slot.meal_type,
                    meal_label=slot.meal_label,
                    recipe_name=recipe.name,
                    recipe_id=recipe.id,
                )
            )
            ingredients.extend(recipe.ingredients)
        plan = WeeklyPlan(
            week_start=week_start_date.isoformat(),
            meals=meals,
            shopping_list=self._build_shopping_list(ingredients),
        )
        self.repository.save_weekly_plan(plan)
        return plan

    def start_scheduler(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

    def stop_scheduler(self) -> None:
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=2)

    def _run_scheduler(self) -> None:
        from backend.app.services.mailing import MailService

        mailer = MailService(self.repository)
        while not self._stop_event.is_set():
            try:
                if self._should_send_now():
                    mailer.send_weekly_plan_email(self, force=False)
            except Exception:
                pass
            self._stop_event.wait(30)

    def _should_send_now(self) -> bool:
        settings = self.repository.get_settings()
        target_day = int(settings.get("schedule_day", "6"))
        target_time = settings.get("schedule_time", "09:00")
        if self.repository.current_week_was_sent():
            return False
        now = datetime.now()
        hour, minute = [int(part) for part in target_time.split(":", 1)]
        return now.weekday() == target_day and (now.hour, now.minute) >= (hour, minute)

    @staticmethod
    def _current_week_start():
        today = datetime.now().date()
        return today - timedelta(days=today.weekday())

    @staticmethod
    def _pick_recipes(recipes: list[Recipe], required_count: int) -> list[Recipe]:
        if len(recipes) >= required_count:
            return random.sample(recipes, required_count)
        pool = recipes[:]
        result: list[Recipe] = []
        while len(result) < required_count:
            random.shuffle(pool)
            result.extend(pool)
        return result[:required_count]

    @staticmethod
    def _active_slots(settings: dict[str, str], week_start_date) -> list[MealSlot]:
        slots: list[MealSlot] = []
        for day_index, (day_key, day_label) in enumerate(DAY_KEYS):
            current_date = week_start_date + timedelta(days=day_index)
            for meal_key, meal_label in MEAL_KEYS:
                if settings.get(f"slot_{day_key}_{meal_key}", "0") == "1":
                    slots.append(
                        MealSlot(
                            date=current_date,
                            day_key=day_key,
                            day_name=day_label,
                            meal_type=meal_key,
                            meal_label=meal_label,
                        )
                    )
        return slots

    @staticmethod
    def _build_shopping_list(ingredients: list[Ingredient]) -> str:
        aggregated: dict[tuple[str, str, str], dict] = {}
        flex_lines: list[tuple[str, str]] = []
        for ingredient in ingredients:
            name = ingredient.name.strip()
            unit = ingredient.unit.strip()
            category = ingredient.category.strip() or "Sonstiges"
            note = ingredient.note.strip()
            quantity = ingredient.quantity
            key = (category.lower(), name.lower(), unit.lower())
            if quantity is None:
                line = f"- {name}"
                if note:
                    line += f" ({note})"
                flex_lines.append((category, line))
                continue
            entry = aggregated.setdefault(
                key,
                {"category": category, "name": name, "unit": unit, "quantity": 0.0, "notes": set()},
            )
            entry["quantity"] += float(quantity)
            if note:
                entry["notes"].add(note)
        grouped: dict[str, list[str]] = {}
        for item in aggregated.values():
            quantity = str(int(item["quantity"])) if item["quantity"].is_integer() else f"{item['quantity']:.2f}".rstrip("0").rstrip(".")
            line = f"- {quantity} {item['unit']} {item['name']}".replace("  ", " ").strip()
            if item["notes"]:
                line += f" ({', '.join(sorted(item['notes']))})"
            grouped.setdefault(item["category"], []).append(line)
        for category, line in flex_lines:
            grouped.setdefault(category, []).append(line)
        if not grouped:
            return "Keine Zutaten gefunden."
        return "\n\n".join(f"{category}\n" + "\n".join(sorted(grouped[category])) for category in sorted(grouped))
