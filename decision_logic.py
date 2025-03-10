import threading  # Für parallele Threads
import time
from keye_detection import ObjectDetection  # Import der Objekterkennung
from relaiscontrol import RelaisControl  # Import der Relaissteuerung

class DecisionLogic:
    def __init__(self):
        """Initialisiert die Steuerlogik, Objekterkennung und Relaissteuerung."""
        self.is_active = None # kontrollvariable für das nur einmalige Aufrufen der Handle_detection
        self.detector = ObjectDetection()  # Erstellt ein Objekt für die Objekterkennung
        self.relais = RelaisControl()  # Erstellt ein Objekt für die Relaissteuerung
        self.detector.set_detection_callback(self.handle_detection)  # Setzt die Callback-Funktion für die Erkennung
        self.roi1 = None  # Speichert die erste ROI (Region of Interest)
        self.roi2 = None  # Speichert die zweite ROI (Region of Interest)
        self.detection_thread = None  # Speichert den Thread für die Erkennung

    def set_rois(self, roi1, roi2):
        """Speichert die definierten ROIs und übergibt sie an die Objekterkennung."""
        self.roi1 = roi1  # Setzt die erste ROI
        self.roi2 = roi2  # Setzt die zweite ROI
        self.detector.set_rois(roi1, roi2)  # Übergibt die ROIs an die Objekterkennung
        #print("Decision_logic.set_rois:", roi1, roi2)  # Gibt eine Bestätigung aus

    def start_detection(self):
        """Startet die Objekterkennung in einem separaten Thread, wenn ROIs gesetzt sind."""
        if self.roi1 and self.roi2:
            if not self.detection_thread or not self.detection_thread.is_alive():
                print("🚀 Starte Erkennung...")
                self.detection_thread = threading.Thread(target=self._run_detection, daemon=True)
                self.detection_thread.start()
                print("Erkennung läuft!")

    def _run_detection(self):
        """Läuft dauerhaft und überprüft, ob die Erkennung noch aktiv ist."""
        while True:
            if not self.detector.running:
                print("Erkennung gestoppt! Starte neu...")
                self.detector.run()  # Falls gestoppt, neu starten
            time.sleep(5)  # Alle 5 Sekunden prüfen

    def stop_detection(self):
        """Beendet die laufende Objekterkennung sicher."""
        if self.detector.running:  # Prüft, ob die Erkennung läuft
            self.detector.stop()  # Setzt die Steuerungsvariable auf False
            if self.detection_thread:
                self.detection_thread.join()  # Wartet auf das Beenden des Threads

    def handle_detection(self, detected):
        """Callback-Funktion, die von der Objekterkennung aufgerufen wird."""
        try:
            print(f"Detection Callback aufgerufen: detected={detected}, self.is_active={self.is_active}")

            if detected and self.is_active is not True:  # Sicherstellen, dass wir nur einmal schalten
                print("Person erkannt, schalte Relais AUS")
                self.relais.off_all()
                self.is_active = True  # Setzt Status auf aktiv

            elif not detected and self.is_active is not False:  # Sicherstellen, dass wir nur einmal schalten
                print("Keine Person mehr erkannt, schalte Relais EIN")
                self.relais.on_all()
                self.is_active = False  # Setzt Status auf inaktiv

        except Exception as e:
            print(f"Fehler in handle_detection: {e}")
            import traceback
            traceback.print_exc()

    def shutdown(self):
        """Beendet das gesamte System sicher."""
        print("System wird heruntergefahren...")
        self.stop_detection()  # Beendet die Erkennung
        self.relais.close_device() # Beendet die Verbindung zum Relais