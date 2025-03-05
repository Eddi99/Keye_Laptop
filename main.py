import sys  # Für die Steuerung des Programms
import threading  # Für paralleles Ausführen der Objekterkennung
from PyQt6.QtWidgets import QApplication  # Für die GUI
from decision_logic import DecisionLogic  # Steuerung der Erkennung & Relais
from GUI import GUIApp  # Die grafische Benutzeroberfläche

if __name__ == "__main__":
    logic = DecisionLogic()

    # Startet die GUI direkt im Hauptthread (wichtig für PyQt)
    app = QApplication(sys.argv)
    window = GUIApp(logic)
    window.show()

    # Startet die Erkennung als separaten Thread, aber erst nach ROI-Setzung!
    detection_thread = threading.Thread(target=logic.start_detection)
    detection_thread.start()

    sys.exit(app.exec())  # Startet die GUI-Eventloop
