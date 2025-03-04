from decision_logic import DecisionLogic
import keyboard  # Import für Tastaturerkennung
import threading  # Für parallele Threads

if __name__ == "__main__":
    logic = DecisionLogic()
    detection_thread = threading.Thread(target=logic.start)
    detection_thread.start()

    print("Drücke ESC, um das Programm zu beenden.")
    keyboard.wait("esc")  # Wartet, bis die Escape-Taste gedrückt wird

    print("Beende das Programm...")
    logic.detector.stop()  # Stoppt die Objekterkennung
    detection_thread.join()  # Wartet auf das Beenden des Threads