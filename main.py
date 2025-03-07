import sys  # Für die Steuerung des Programms
from PyQt6.QtWidgets import QApplication  # Für die GUI
from decision_logic import DecisionLogic  # Steuerung der Erkennung & Relais
from GUI import GUIApp  # Die grafische Benutzeroberfläche

if __name__ == "__main__":
    logic = DecisionLogic()

    # Startet die GUI direkt im Hauptthread (wichtig für PyQt)
    app = QApplication(sys.argv)
    window = GUIApp(logic)
    window.show()
    sys.exit(app.exec())  # Startet die GUI-Eventloop