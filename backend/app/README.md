# App

Dieser Ordner enthält den eigentlichen Anwendungscode.

Schichten:

- `core/`: Konfiguration und grundlegende App-Einstiegspunkte
- `domain/`: fachliche Modelle
- `infrastructure/`: technische Anbindungen wie SQLite
- `services/`: Geschäftslogik wie Planung und Mailversand

Die Trennung hält UI, Fachlogik und Persistenz voneinander getrennt.
