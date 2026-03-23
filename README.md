# MealScheduler

MealScheduler ist eine lokale Python-App mit kleiner Web-UI. Die Anwendung ist jetzt in klare Schichten und Unterordner getrennt: `core`, `domain`, `infrastructure`, `services` und `presentation`.

## Architektur

- `backend/app/core/config.py`: Laufzeitkonfiguration
- `backend/app/domain/models.py`: Domänenobjekte für Rezepte, Slots und Wochenpläne
- `backend/app/infrastructure/repository.py`: SQLite-Zugriff
- `backend/app/services/planning.py`: Wochenplanung und Scheduler
- `backend/app/services/mailing.py`: SMTP-Mailversand
- `backend/app/presentation/web.py`: HTTP-Server und UI
- `backend/app/config.py`, `backend/app/models.py`, `backend/app/repository.py`, `backend/app/services.py`, `backend/app/web.py`: schmale Kompatibilitäts-Wrapper
- `backend/api.py`, `backend/picker.py`, `backend/mailer.py`, `backend/conf_reader.py`: Legacy-Adapter

## Was die App kann

- Rezepte mit Zutaten, Kategorien und Tags speichern
- Für jeden Wochentag separat Frühstück, Mittagessen und Abendessen aktivieren
- Wochenplan passend zu den aktivierten Mahlzeiten automatisch erzeugen
- Zutaten mengenbasiert zu einem Einkaufszettel zusammenfassen
- Wochenplan und Einkaufsliste per Mail senden
- SMTP-Verbindung per Testmail prüfen

## Start

1. Python 3.11+ verwenden
2. Im Projektordner starten:

```bash
python run.py
```

3. Im Browser öffnen:

```text
http://127.0.0.1:8080
```

## Einstellungen

Die SMTP-Daten werden direkt in der UI hinterlegt und lokal in der SQLite-Datenbank gespeichert. Für Gmail ist in der Regel ein App-Passwort nötig.

Wichtige Felder:

- `SMTP Host`: z. B. `smtp.gmail.com`
- `SMTP Port`: meist `465` mit SSL oder `587` mit STARTTLS
- `Absenderadresse` und `Empfängeradresse`
- `Versandtag`: standardmäßig Sonntag
- `Versandzeit`: Uhrzeit für den automatischen Versand
- `Mahlzeiten pro Tag`: hier steuerst du pro Wochentag Frühstück, Mittagessen und Abendessen einzeln

Mit `Testmail senden` kannst du prüfen, ob SMTP-Host, Login und Empfänger korrekt funktionieren, ohne dabei einen Wochenplan zu verschicken.

## Scheduler

Der Scheduler läuft im Prozess der Web-App. Das heißt:

- Die Anwendung muss aktiv laufen, damit der automatische Versand stattfindet.
- Beim manuellen Klick auf `Mail jetzt senden` wird der aktuelle Wochenplan sofort verschickt.
- Pro Kalenderwoche wird nur einmal automatisch versendet.

## Datenhaltung

- SQLite DB: `backend/data/mealscheduler.db`
- Einstieg: [run.py](/C:/Users/k.seitz-admin/PycharmProjects/MealScheduler/run.py)
- App-Paket: [backend/app](/C:/Users/k.seitz-admin/PycharmProjects/MealScheduler/backend/app)
