import cv2  # OpenCV für Bildverarbeitung
from ultralytics import YOLO  # YOLO für Objekterkennung


class ObjectDetection:
    def __init__(self, model_path="yolo11s.pt"):
        self.cap = cv2.VideoCapture(1)  # Öffnet die Kamera mit Index 1
        self.cap.set(3, 1280)  # Setzt die Breite des Kamera-Frames auf 1280 Pixel
        self.cap.set(4, 720)  # Setzt die Höhe des Kamera-Frames auf 720 Pixel
        self.model = YOLO(model_path)  # Lädt das YOLO-Modell für Objekterkennung
        self.target_object = "person"  # Definiert das Zielobjekt als "Person"
        self.running = False  # Kontrollvariable für das Hauptprogramm (Start erst nach GUI-Klick)

        # ROIs als Platzhalter
        self.roi1 = None
        self.roi2 = None

        self.object_in_zone1 = False
        self.object_in_zone2 = False
        self.in_zone1_frames = 0  # Anzahl erkannter Frames in der ersten ROI
        self.out_zone1_frames = 0  # Anzahl der nicht erkannten Frames in der ersten ROI
        self.in_zone2_frames = 0  # Anzahl erkannter Frames in der zweiten ROI
        self.out_zone2_frames = 0  # Anzahl der nicht erkannten Frames in der zweiten ROI
        self.is_active = False  # Gibt an, ob aktuell eine Person erkannt wurde
        self.callback = None  # Speichert die Callback-Funktion

    def set_callback(self, callback):
        """Setzt eine externe Callback-Funktion für erkannte Objekte."""
        self.callback = callback

    def set_rois(self, roi1, roi2):
        """Speichert die ROIs für die Erkennung."""
        self.roi1 = roi1
        self.roi2 = roi2
        print("ROIs für die Erkennung aktualisiert:", roi1, roi2)

    def detect_objects(self, frame):
        """Führt die Objekterkennung mit YOLO durch, zeichnet Bounding Boxes und prüft, ob eine Person in den ROIs ist."""
        results = self.model(frame, imgsz=320, verbose=False)
        detections = results[0].boxes.data.cpu().numpy()  # Extrahiert erkannte Objekte

        if self.roi1 and self.roi2:
            for det in detections:
                x_min, y_min, x_max, y_max, conf, cls = det[:6]
                label = self.model.names[int(cls)]  # Klassenname des Objekts

                if label == self.target_object:  # Prüfe, ob das erkannte Objekt eine Person ist
                    print("ROI1-X: ",self.roi1[0], " <= ", (det[0] + det[2]) / 2 / frame.shape[1], " <= ", self.roi1[2])
                    #print("ROI1-Y: ", self.roi1[1], " <= ", (det[1] + det[3]) / 2 / frame.shape[0], " <= ", self.roi1[3])
                    #print("ROI2-X: ", self.roi2[0], " <= ", (det[0] + det[2]) / 2 / frame.shape[1], " <= ", self.roi2[2])
                    #print("ROI2-Y: ", self.roi2[1], " <= ", (det[1] + det[3]) / 2 / frame.shape[0], " <= ", self.roi2[3])

                    self.object_in_zone1 = any(
                        self.roi1[0] <= (det[0] + det[2]) / 2 / frame.shape[1] <= self.roi1[2] and
                        self.roi1[1] <= (det[1] + det[3]) / 2 / frame.shape[0] <= self.roi1[3]
                        for det in detections if label == self.target_object
                    )
                    '''self.object_in_zone2 = any(
                        self.roi2[0] <= (det[0] + det[2]) / 2 / frame.shape[1] <= self.roi2[2] and
                        self.roi2[1] <= (det[1] + det[3]) / 2 / frame.shape[0] <= self.roi2[3]
                        for det in detections if label == self.target_object
                    )'''

            if self.object_in_zone1 or self.object_in_zone2:
                if self.object_in_zone1:
                    self.in_zone1_frames += 1
                    self.out_zone1_frames = 0
                '''if self.object_in_zone2:
                    self.in_zone2_frames += 1
                    self.out_zone2_frames = 0'''

                if (self.in_zone1_frames >= 3 or self.in_zone2_frames >= 3) and not self.is_active:
                    self.is_active = True
                    print("Person detected in ROI - Alarm triggered!")
                    if self.callback:
                        self.callback(True)
            else:
                self.out_zone1_frames += 1
                self.in_zone1_frames = 0
                self.out_zone2_frames += 1
                self.in_zone2_frames = 0

                if (self.out_zone1_frames >= 3 and self.out_zone2_frames >= 3) and self.is_active:
                    self.is_active = False
                    print("No person in ROI - Alarm deactivated!")
                    if self.callback:
                        self.callback(False)

        # Zeichne Bounding Boxes auf dem Kamerabild
        for det in detections:
            x_min, y_min, x_max, y_max, conf, cls = det[:6]
            label = f"{self.model.names[int(cls)]}: {conf:.2f}"
            cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Zeichne die ROIs als Rechtecke
        height, width, _ = frame.shape
        roi1_px = (int(self.roi1[0] * width), int(self.roi1[1] * height), int(self.roi1[2] * width),
                   int(self.roi1[3] * height))
        #roi2_px = (int(self.roi2[0] * width), int(self.roi2[1] * height), int(self.roi2[2] * width),
        #          int(self.roi2[3] * height))

        cv2.rectangle(frame, (roi1_px[0], roi1_px[1]), (roi1_px[2], roi1_px[3]), (255, 0, 0), 2)  # Blau für ROI 1
        #cv2.rectangle(frame, (roi2_px[0], roi2_px[1]), (roi2_px[2], roi2_px[3]), (0, 0, 255), 2)  # Rot für ROI 2

        return frame

    def run(self):
        """Startet die Objekterkennung in einer Schleife."""
        if not self.roi1 or not self.roi2:
            print("ROIs nicht gesetzt! Starte nicht.")
            return

        self.running = True
        print("Erkennung läuft...")

        while self.cap.isOpened() and self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            frame_annotated = self.detect_objects(frame_rgb)

            cv2.imshow("Erkennung", cv2.cvtColor(frame_annotated, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        print("Erkennung gestoppt.")

    def stop(self):
        """Stoppt die Objekterkennung sicher."""
        self.running = False
        print("Erkennung wird gestoppt...")