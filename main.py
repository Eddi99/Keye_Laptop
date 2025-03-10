import sys  # Für die Steuerung des Programms und Zugriff auf Systemargumente
from PyQt6.QtWidgets import QApplication  # Importiert die Hauptklasse für die GUI-Anwendung
from decision_logic import DecisionLogic  # Importiert die Steuerlogik für Objekterkennung & Relaissteuerung
from GUI import GUIApp  # Importiert die grafische Benutzeroberfläche

def log_errors():
    """Schreibt error- und debug-log einträge"""
    sys.stdout = open("debug_log.txt", "w", buffering=1)  # Sofortiges Schreiben erzwingen
    sys.stderr = open("error_log.txt", "w", buffering=1)


if __name__ == "__main__":
    """Prüft, ob das Skript direkt ausgeführt wird"""
    log_errors()  # Log-Dateien aktivieren
    logic = DecisionLogic()  # Erstellt eine Instanz der Entscheidungslogik

    app = QApplication(sys.argv)  # Erstellt eine QApplication-Instanz für die GUI-Steuerung

    window = GUIApp(logic)  # Erstellt das Hauptfenster der GUI und übergibt die Steuerlogik
    window.showMaximized()  # Zeigt die GUI maximiert an
    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Anwendung wurde normal beendet.")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        input("Drücke Enter zum Beenden...")

    input("Drücke Enter zum Beenden...")
