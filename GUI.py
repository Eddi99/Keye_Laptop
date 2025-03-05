import time
import threading
from decision_logic import DecisionLogic  # Import der Hauptsteuerlogik


def test_logic():
    print("Starte den Test...")
    logic = DecisionLogic()  # Erstellt ein Objekt der DecisionLogic-Klasse

    # Definierte Beispiel-ROIs (x_min, y_min, x_max, y_max)
    roi1 = (0.0, 0.0, 0.3, 1.0)
    roi2 = (0.8, 0.0, 1.0, 1.0)

    print("Setze ROIs...")
    logic.set_rois(roi1, roi2)  # Setzt die ROIs für die Objekterkennung

    print("Starte die Objekterkennung...")
    detection_thread = threading.Thread(target=logic.start_detection)
    detection_thread.start()  # Startet die Erkennung in einem separaten Thread

    print("Lasse das System 40 Sekunden laufen...")
    time.sleep(40)  # Lässt die Erkennung für 10 Sekunden laufen

    print("Stoppe die Objekterkennung...")
    logic.stop_detection()  # Stoppt die Erkennung sicher

    print("Beende das System...")
    logic.shutdown()  # Beendet das System und schaltet das Relais aus

    print("Test abgeschlossen.")


if __name__ == "__main__":
    test_logic()
