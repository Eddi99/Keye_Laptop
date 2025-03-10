import sys  # Für die Steuerung des Programms und Zugriff auf Systemargumente
from PyQt6.QtWidgets import QApplication  # Importiert die Hauptklasse für die GUI-Anwendung
from decision_logic import DecisionLogic  # Importiert die Steuerlogik für Objekterkennung & Relaissteuerung
from GUI import GUIApp  # Importiert die grafische Benutzeroberfläche
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QSplashScreen
import time


def show_splash():
    """Zeigt ein Splashscreen für den Ladevorgang."""
    splash_pix = QPixmap("loading.png")  # Ladebild
    splash = QSplashScreen(splash_pix)
    splash.show()
    app.processEvents()  # Erzwingt das Rendern des Splashscreens
    time.sleep(30)  # Simuliert eine Ladezeit
    splash.close()

if __name__ == "__main__":  # Prüft, ob das Skript direkt ausgeführt wird
    logic = DecisionLogic()  # Erstellt eine Instanz der Entscheidungslogik

    # Startet die GUI direkt im Hauptthread (wichtig für PyQt)
    app = QApplication(sys.argv)  # Erstellt eine QApplication-Instanz für die GUI-Steuerung
    show_splash()  # Ladebildschirm anzeigen
    window = GUIApp(logic)  # Erstellt das Hauptfenster der GUI und übergibt die Steuerlogik
    window.showMaximized()  # Zeigt die GUI maximiert an
    sys.exit(app.exec())  # Startet die GUI-Eventloop und hält das Programm am Laufen
