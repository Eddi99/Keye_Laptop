import cv2  # OpenCV für Bildverarbeitung
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QAbstractButton  # PyQt6 für GUI-Elemente
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen  # PyQt6 für Bildverarbeitung und Zeichnen
from PyQt6.QtCore import Qt  # PyQt6 für Fenstersteuerung und Punktkoordinaten

class GUIApp(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic  # Speichert die Referenz zur Entscheidungslogik

        # Initialisierung aller Instanzvariablen vor UI-Aufbau
        self.roi_points = []  # Liste zum Speichern der gesetzten ROI-Punkte
        self.temp_roi = None  # Temporäres Rechteck während des Aufziehens
        self.image = None  # Variable zum Speichern des aktuellen Kamerabilds
        self.drawing = False  # Flag zum Zeichnen der ROIs
        self.current_roi = 1  # Speichert, welche ROI aktuell gesetzt wird
        self.label = None  # GUI-Element zur Anzeige des Kamerabilds
        self.confirm_button = None  # Button zum Bestätigen der ROIs

        self.initUI()  # Initialisiert die Benutzeroberfläche

    def initUI(self):
        self.setWindowTitle("ROI Auswahl")  # Setzt den Fenstertitel
        self.setGeometry(100, 100, 900, 700)  # Erhöht die Fenstergröße für bessere Anpassung

        self.label = QLabel(self)  # Erstellt ein Label für das Bild
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)  # Setzt das Bild an den oberen Rand
        self.label.setFixedSize(800, 600)  # Setzt eine feste Größe für das Bild

        self.confirm_button = QPushButton("Bestätigen und Starten", self)  # Erstellt einen Bestätigungsbutton
        self.confirm_button.setEnabled(False)  # Deaktiviert den Button initial
        self.confirm_button.clicked.connect(self.confirm_rois)  # Verbindet den Button mit der Bestätigungsfunktion

        layout = QVBoxLayout()  # Erstellt ein vertikales Layout
        layout.addWidget(self.label)  # Fügt das Bildlabel zum Layout hinzu
        layout.addWidget(self.confirm_button)  # Fügt den Bestätigungsbutton zum Layout hinzu
        self.setLayout(layout)  # Setzt das Layout für das Fenster

        self.capture_frame()  # Nimmt ein Standbild von der Kamera auf

    def capture_frame(self):
        cap = cv2.VideoCapture(1)  # Öffnet die Kamera mit Index 1
        ret, frame = cap.read()  # Nimmt ein Einzelbild auf
        cap.release()  # Schließt die Kamera

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Konvertiert das Bild in RGB
            self.image = cv2.resize(frame, (800, 600))  # Skaliert das Bild auf die Fenstergröße
            self.show_frame()  # Zeigt das Bild im GUI-Fenster an
        else:
            print("Kamerabild konnte nicht geladen werden")  # Fehlerausgabe, falls kein Bild aufgenommen werden konnte

    def show_frame(self):
        if self.image is not None:
            height, width, channel = self.image.shape  # Bestimmt Bildhöhe, -breite und Kanäle
            bytes_per_line = 3 * width  # Berechnet die Byte-Anzahl pro Zeile
            q_img = QImage(self.image.data, width, height, bytes_per_line,
                           QImage.Format.Format_RGB888)  # Erstellt ein QImage aus dem Kamerabild
            pixmap = QPixmap.fromImage(q_img)  # Wandelt das QImage in ein QPixmap um

            if len(self.roi_points) >= 2 or self.temp_roi:
                pixmap = self.draw_rois(pixmap)  # Zeichnet gesetzte ROIs ein

            self.label.setPixmap(pixmap)  # Zeigt das Bild mit ROIs im Label an

    def draw_rois(self, pixmap):
        """Zeichnet die gesetzten ROIs auf das Bild."""
        painter = QPainter(pixmap)  # Erstellt einen Painter für das Bild
        pen = QPen(Qt.GlobalColor.red)  # Setzt die Zeichenfarbe auf Rot
        pen.setWidth(2)  # Setzt die Stiftbreite auf 2 Pixel
        painter.setPen(pen)  # Übernimmt den Stift in den Painter

        for i in range(0, len(self.roi_points), 2):  # Iteriert über die ROI-Punkte in Zweierschritten
            if i + 1 < len(self.roi_points):  # Prüft, ob ein vollständiges Rechteck vorhanden ist
                x1, y1 = self.roi_points[i]  # Erstes Eckpunktpaar
                x2, y2 = self.roi_points[i + 1]  # Zweites Eckpunktpaar
                painter.drawRect(x1, y1, x2 - x1, y2 - y1)  # Zeichnet das Rechteck

        if self.temp_roi:
            x1, y1, x2, y2 = self.temp_roi
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)

        painter.end()  # Beendet den Painter
        return pixmap  # Gibt das geänderte Bild zurück

    def mousePressEvent(self, event):
        """Erfasst die Mausposition, speichert die ROI-Punkte und zeigt ein temporäres Rechteck an."""
        if len(self.roi_points) < 4:
            x = int(event.position().x() - self.label.geometry().x())
            y = int(event.position().y() - self.label.geometry().y())  # Korrigiert die Mausposition relativ zum Bild
            x = max(0, min(x, self.label.width() - 1))
            y = max(0, min(y, self.label.height() - 1))
            self.roi_points.append((x, y))
            self.temp_roi = (x, y, x, y)  # Setzt das temporäre Rechteck
            print(f"ROI {self.current_roi}: Punkt {len(self.roi_points) % 2 + 1} gesetzt: {x}, {y}")
            self.show_frame()

        else:
            self.confirm_button.setEnabled(True) # aktiviert den confrim_button, falls die ROI gesetzt wurden

    def confirm_rois(self):
        """Bestätigt die gesetzten ROIs und übergibt sie an die Entscheidungslogik."""
        width, height, _ = self.image.shape
        roi1 = (self.roi_points[0][0] / width, self.roi_points[0][1] / height,
                self.roi_points[1][0] / width, self.roi_points[1][1] / height)
        roi2 = (self.roi_points[2][0] / width, self.roi_points[2][1] / height,
                self.roi_points[3][0] / width, self.roi_points[3][1] / height)
        self.logic.set_rois(roi1, roi2)
        print("ROIs gespeichert:", roi1, roi2)
        self.close()
