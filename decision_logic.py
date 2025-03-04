import threading  # Für parallele Threads
from keye_detection import ObjectDetection  # Import der Objekterkennung
from relaiscontrol import RelaisControl  # Import der Relaissteuerung

class DecisionLogic:
    def __init__(self):
        self.detector = ObjectDetection()
        self.relais = RelaisControl()
        self.detector.set_callback(self.handle_detection)

    def handle_detection(self, detected):
        if not detected:
            self.relais.on_all()  # Schaltet das Relais ein

        else:
            self.relais.off_all()  # Schaltet das Relais aus

    def start(self):
        detection_thread = threading.Thread(target=self.detector.run)
        detection_thread.start()