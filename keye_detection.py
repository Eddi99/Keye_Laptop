import cv2  # OpenCV für Bildverarbeitung
from ultralytics import YOLO  # YOLO für Objekterkennung


class ObjectDetection:
    def __init__(self, model_path="yolo11s.pt"):
        self.cap = cv2.VideoCapture(1)  # Öffnet die Kamera mit Index 1
        self.cap.set(3, 1280)  # Setzt die Breite des Kamera-Frames auf 1280 Pixel
        self.cap.set(4, 720)  # Setzt die Höhe des Kamera-Frames auf 720 Pixel
        self.model = YOLO(model_path)  # Lädt das YOLO-Modell für Objekterkennung
        self.target_object = "person"  # Definiert das Zielobjekt als "Person"
        self.running = True  # Kontrollvariable für das Hauptprogramm

        # Erste ROI (Region of Interest)
        self.zone1_x_min, self.zone1_x_max = 0.4, 0.6  # X-Bereich der ersten ROI
        self.zone1_y_min, self.zone1_y_max = 0.3, 0.7  # Y-Bereich der ersten ROI

        # Zweite ROI
        self.zone2_x_min, self.zone2_x_max = 0.1, 0.3  # X-Bereich der zweiten ROI
        self.zone2_y_min, self.zone2_y_max = 0.2, 0.5  # Y-Bereich der zweiten ROI

        self.in_zone1_frames = 0  # Anzahl erkannter Frames in der ersten ROI
        self.out_zone1_frames = 0  # Anzahl der nicht erkannten Frames in der ersten ROI
        self.in_zone2_frames = 0  # Anzahl erkannter Frames in der zweiten ROI
        self.out_zone2_frames = 0  # Anzahl der nicht erkannten Frames in der zweiten ROI
        self.is_active = False  # Gibt an, ob aktuell eine Person erkannt wurde
        self.callback = None  # Speichert die Callback-Funktion

    def set_callback(self, callback):
        self.callback = callback  # Setzt die externe Callback-Funktion

    def detect_objects(self, frame):
        results = self.model(frame, imgsz=320, verbose=False)  # Führt die Objekterkennung aus, durch verbose werden bei jedem Frame die Daten zur Objekterkennung ausgegeben
        detections = results[0].boxes.data.cpu().numpy()  # Extrahiert die erkannten Objekte

        object_in_zone1 = any(
            self.zone1_x_min <= (det[0] + det[2]) / 2 / frame.shape[1] <= self.zone1_x_max and
            self.zone1_y_min <= (det[1] + det[3]) / 2 / frame.shape[0]
            for det in detections)  # Prüft, ob ein Objekt in der ersten ROI ist

        object_in_zone2 = any(
            self.zone2_x_min <= (det[0] + det[2]) / 2 / frame.shape[1] <= self.zone2_x_max and
            self.zone2_y_min <= (det[1] + det[3]) / 2 / frame.shape[0]
            for det in detections)  # Prüft, ob ein Objekt in der zweiten ROI ist

        if object_in_zone1 or object_in_zone2:
            if object_in_zone1:
                self.in_zone1_frames += 1
                self.out_zone1_frames = 0
            if object_in_zone2:
                self.in_zone2_frames += 1
                self.out_zone2_frames = 0

            if (self.in_zone1_frames >= 4 or self.in_zone2_frames >= 4) and not self.is_active:
                self.is_active = True
                print("Person detected in ROI - Alarm triggered!")
                if self.callback:
                    self.callback(True)
        else:
            self.out_zone1_frames += 1
            self.in_zone1_frames = 0
            self.out_zone2_frames += 1
            self.in_zone2_frames = 0

            if (self.out_zone1_frames >= 5 and self.out_zone2_frames >= 5) and self.is_active:
                self.is_active = False
                print("No person in ROI - Alarm deactivated!")
                if self.callback:
                    self.callback(False)

    def run(self):
        while self.cap.isOpened() and self.running:  # Prüft, ob die Kamera geöffnet ist und das Programm läuft
            ret, frame = self.cap.read()  # Liest einen Frame aus der Kamera
            if not ret:  # Falls kein Frame verfügbar ist, beenden
                break
            frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)  # Spiegelt das Bild und wandelt es in RGB um
            self.detect_objects(frame_rgb)  # Führt die Objekterkennung aus
            #cv2.imshow("Webcam YOLO", cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))  # Zeigt das bearbeitete Bild an
        self.cap.release()  # Gibt die Kamera frei
        cv2.destroyAllWindows()  # Schließt alle OpenCV-Fenster

    def stop(self):
        self.running = False  # Setzt die Kontrollvariable, um die Schleife zu beenden
