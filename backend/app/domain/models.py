from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date


DAY_KEYS = [
    ("monday", "Montag"),
    ("tuesday", "Dienstag"),
    ("wednesday", "Mittwoch"),
    ("thursday", "Donnerstag"),
    ("friday", "Freitag"),
    ("saturday", "Samstag"),
    ("sunday", "Sonntag"),
]

MEAL_KEYS = [
    ("breakfast", "Frühstück"),
    ("lunch", "Mittagessen"),
    ("dinner", "Abendessen"),
]


@dataclass(slots=True)
class Ingredient:
    name: str
    quantity: float | None = None
    unit: str = ""
    category: str = ""
    note: str = ""


@dataclass(slots=True)
class Recipe:
    id: int
    name: str
    description: str
    servings: int
    created_at: str
    ingredients: list[Ingredient] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MealSlot:
    date: date
    day_key: str
    day_name: str
    meal_type: str
    meal_label: str


@dataclass(slots=True)
class PlannedMeal:
    date: str
    day_name: str
    meal_type: str
    meal_label: str
    recipe_name: str
    recipe_id: int


@dataclass(slots=True)
class WeeklyPlan:
    week_start: str
    meals: list[PlannedMeal]
    shopping_list: str

    def to_dict(self) -> dict:
        return {
            "week_start": self.week_start,
            "meals": [asdict(meal) for meal in self.meals],
            "shopping_list": self.shopping_list,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "WeeklyPlan":
        return cls(
            week_start=payload["week_start"],
            meals=[PlannedMeal(**meal) for meal in payload["meals"]],
            shopping_list=payload["shopping_list"],
        )
