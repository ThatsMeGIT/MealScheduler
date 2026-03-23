from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Protocol

from backend.app.domain.models import WeeklyPlan
from backend.app.infrastructure.repository import MealRepository


class MailDeliveryError(RuntimeError):
    pass


class PlannerProtocol(Protocol):
    def create_or_refresh_current_plan(self, force: bool = False) -> WeeklyPlan:
        ...


class MailService:
    def __init__(self, repository: MealRepository) -> None:
        self.repository = repository

    def send_test_email(self) -> None:
        settings = self.repository.get_settings()
        self._validate_mail_settings(settings)
        mail = EmailMessage()
        mail["From"] = settings["mail_from"]
        mail["To"] = settings["mail_to"]
        mail["Subject"] = "MealScheduler Testmail"
        mail.set_content(
            "Dies ist eine Testmail von MealScheduler.\n\n"
            "Wenn diese Nachricht angekommen ist, funktioniert der SMTP-Versand."
        )
        self._send_message(mail, settings)

    def send_weekly_plan_email(self, planner: PlannerProtocol, force: bool = False) -> None:
        settings = self.repository.get_settings()
        self._validate_mail_settings(settings)
        plan = planner.create_or_refresh_current_plan(force=force)
        mail = EmailMessage()
        mail["From"] = settings["mail_from"]
        mail["To"] = settings["mail_to"]
        mail["Subject"] = settings.get("mail_subject", "Dein Wochenplan")
        mail.set_content(self._build_mail_body(plan))
        self._send_message(mail, settings)
        self.repository.mark_current_week_sent()

    @staticmethod
    def _validate_mail_settings(settings: dict[str, str]) -> None:
        required = ["smtp_host", "smtp_port", "smtp_username", "smtp_password", "mail_from", "mail_to"]
        missing = [key for key in required if not settings.get(key)]
        if missing:
            raise MailDeliveryError(f"Fehlende Einstellungen: {', '.join(missing)}")

    @staticmethod
    def _send_message(mail: EmailMessage, settings: dict[str, str]) -> None:
        smtp_host = settings["smtp_host"]
        smtp_port = int(settings["smtp_port"])
        smtp_username = settings["smtp_username"]
        smtp_password = settings["smtp_password"]
        use_ssl = settings.get("use_ssl", "1") == "1"
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                    server.login(smtp_username, smtp_password)
                    server.send_message(mail)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(mail)
        except (OSError, smtplib.SMTPException) as exc:
            raise MailDeliveryError(str(exc)) from exc

    @staticmethod
    def _build_mail_body(plan: WeeklyPlan) -> str:
        lines = ["Dein Wochenplan", ""]
        for meal in plan.meals:
            lines.append(f"- {meal.day_name} {meal.meal_label}: {meal.recipe_name}")
        lines.extend(["", "Einkaufszettel", "", plan.shopping_list])
        return "\n".join(lines)
