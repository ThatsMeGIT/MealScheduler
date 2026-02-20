# db_watcher.py
# Gibt Auskunft über Elemente der Datenbank und der Tabellen

from abc import ABC, abstractmethod

class Watcher(ABC):

    @abstractmethod
    def get(self, id):
        pass

    @abstractmethod
    def db_sum(self):
        pass
    