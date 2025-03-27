import cv2  # OpenCV für Bildverarbeitung
import threading  # Für paralleles Ausführen der Objekterkennung
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, \
	QComboBox, QListView  # PyQt5 für GUI-Elemente
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen  # PyQt6 für Bildverarbeitung und Zeichnen
from PyQt5.QtCore import Qt, QTimer  # PyQt6 für Fenstersteuerung und Punktkoordinaten

class GUIApp(QWidget):
	def __init__(self, logic):
		super().__init__()
		self.logic = logic  # Speichert die Referenz zur Entscheidungslogik

		# Initialisierung aller Instanzvariablen vor UI-Aufbau
		self.image_width = 0  # Speichert die Breite des im Fenster angezeigten Bildes
		self.image_height = 0  # Speichert die Höhe des im Fenster angezeigten Bildes
		self.roi_points = []  # Liste zum Speichern der gesetzten ROI-Punkte
		self.temp_roi = None  # Temporäres Rechteck während des Aufziehens
		self.image = None  # Variable zum Speichern des aktuellen Kamerabilds
		self.current_roi = 1  # Speichert, welche ROI aktuell gesetzt wird
		self.label = None  # GUI-Element zur Anzeige des Kamerabilds
		self.banner_label = None # Banner, zur Anzeige von Nutzer-Infos
		self.camera_selector = None  # Dropdown für Kameraauswahl
		self.retake_picture_button = None  # Button zum Wiederholen des Fotos
		self.confirm_button = None  # Button zum Bestätigen der ROIs
		self.roi_reset_button = None  # Button zum Zurücksetzen der ROIs
		self.relais_on_button = None  # Button zum Einschalten des Relais
		self.relais_off_button = None  # Button zum Ausschalten des Relais
		self.exit_button = None # Button zum Beenden des Programms
		self.start_detection_bool = True  # Überprüfungsvariable zum nur einmaligen Abschicken der ROI
		self.last_relais_state = self.logic.relais.relais_bool # Speichert den letzten bekannten Status des Relais
		self.set_index_once = True # Variable verhindert, dass bei keiner angeschlossenen Kamera Endlosschleife entsteht

		self.initUI()  # Initialisiert die Benutzeroberfläche

		self.relais_timer = QTimer(self) # Überwacht den Relaisstatus regelmäßig alle 200ms
		self.relais_timer.timeout.connect(self.check_relais_state)
		self.relais_timer.start(200)  # 200 Millisekunden

	def initUI(self):
		"""Initialisiert die UI mit Button-Anordnung und Bildgröße"""
		self.setWindowTitle("Keye UI") # Fenstertitel setzen

		screen_size = QApplication.primaryScreen().size()  # Bildschirmgröße abrufen
		screen_width = screen_size.width() # Bildschirmbreite speichern
		screen_height = screen_size.height()# Bildschirmhöhe speichern

		self.setGeometry(0, 0, int(screen_width * 0.9), int(screen_height * 0.9))  # Fenstergröße anpassen
		self.image_width = int(screen_width * 0.75)
		self.image_height = int(screen_height * 0.75)

		self.banner_label = QLabel("Willkommen! Bitte spannen Sie zwei Sicherheitszonen auf, indem Sie jeweils zwei Eckpunkte anklicken oder nehmen Sie das Bild erneut auf.",self)  # Info-Banner initialisieren
		self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.banner_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")

		self.label = QLabel(self)  # Bildanzeige-Fenster (Label) im Layout
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Fenster mittig im Layout platzieren
		self.label.setFixedSize(self.image_width, self.image_height) # Fenstergröße setzen

		button_height = int(screen_height * 0.1)  # Button-Höhe berechnen (10% der Bildschirmhöhe)

		# Dropdown zur Auswahl der Kameraquelle
		self.camera_selector = QComboBox(self)
		self.camera_selector.setFixedWidth(int(screen_width * 0.1))
		self.camera_selector.setView(QListView())
		self.camera_selector.addItems(["Kamera 0", "Kamera 1", "Kamera 2"])
		self.camera_selector.setFixedHeight(button_height)
		# Stylesheet für das Aussehen des Dropdown-Menüs
		self.camera_selector.setStyleSheet("""
			QComboBox {
				background-color: gray;
				color: white;
				font-weight: bold;
				border: none;
				text-align: center;
			}
		""")
		view = QListView()
		view.setStyleSheet("""
		    QListView::item {
		        min-height: 70px;  /* Höhe jeder Auswahlzeile */
		        font-size: 24px;   /* größere Schrift für Touch */
		        padding-left: 10px;  /* etwas Abstand vom Rand */
		    }

		    QListView {
		        background-color: gray;
		        color: white;
		        outline: none;
		    }

		    QListView::item:selected {
		        background-color: darkgray;
		    }
		""")
		self.camera_selector.setView(view)

		self.camera_selector.activated.connect(self.set_camera_index)  # Direkt ausführen beim Klick

		# Buttons erstellen
		self.retake_picture_button = QPushButton("Bild erneut aufnehmen", self)  # Buttontext festlegen
		self.retake_picture_button.setFixedHeight(button_height)  # Buttonhöhe festsetzen
		self.retake_picture_button.setStyleSheet("background-color: gray; color: white; font-weight: bold; border: none;")  # Buttonoptik festlegen
		self.retake_picture_button.clicked.connect(self.capture_frame)  # Zuweisen der Buttonfunktion: Bild erneut aufnehmen

		self.roi_reset_button = QPushButton("Zonen-Reset", self)
		self.roi_reset_button.setFixedHeight(button_height)
		self.roi_reset_button.setStyleSheet("background-color: gray; color: white; font-weight: bold; border: none;")
		self.roi_reset_button.clicked.connect(self.roi_reset)  # Zuweisen der Buttonfunktion: ROI zurücksetzen

		self.confirm_button = QPushButton("Bestätigen und Starten", self)
		self.confirm_button.setFixedHeight(button_height)
		self.confirm_button.setStyleSheet("background-color: red; color: white; font-weight: bold; border: none;")
		self.confirm_button.setVisible(False)  # Anfangs unsichtbar
		self.confirm_button.clicked.connect(self.confirm_rois)  # Zuweisen der Buttonfunktion: ROIs bestätigen und starten

		self.relais_on_button = QPushButton("Einschalten", self)
		self.relais_on_button.setFixedHeight(button_height)
		self.relais_on_button.setStyleSheet("background-color: green; color: white; font-weight: bold; border: none;")
		self.relais_on_button.setVisible(False)  # Anfangs unsichtbar
		self.relais_on_button.clicked.connect(self.logic.relais.on_all)  # Zuweisen der Buttonfunktion: Relais einschalten

		self.relais_off_button = QPushButton("Ausschalten", self)
		self.relais_off_button.setFixedHeight(button_height)
		self.relais_off_button.setStyleSheet("background-color: red; color: white; font-weight: bold; border: none;")
		self.relais_off_button.setVisible(False)  # Anfangs unsichtbar
		self.relais_off_button.clicked.connect(self.logic.relais.off_all)  # Zuweisen der Buttonfunktion: Relais ausschalten

		self.exit_button = QPushButton("Beenden", self)
		self.exit_button.setFixedHeight(button_height)
		self.exit_button.setStyleSheet("background-color: gray; color: white; font-weight: bold; border: none;")
		self.exit_button.setFixedWidth(int(screen_width * 0.1))
		self.exit_button.clicked.connect(self.closeEvent)  # Zuweisen der Buttonfunktion: Programm sicher beenden

		button_layout = QHBoxLayout()  # Button-Anordnung horizontal
		button_layout.addWidget(self.camera_selector)
		button_layout.addWidget(self.retake_picture_button)
		button_layout.addWidget(self.confirm_button)
		button_layout.addWidget(self.roi_reset_button)
		button_layout.addWidget(self.relais_on_button)
		button_layout.addWidget(self.relais_off_button)
		button_layout.addWidget(self.exit_button)

		layout = QVBoxLayout()  # Hauptlayout vertikal angeordent
		layout.addStretch()  # Platz vor dem Bild für Zentrierung
		layout.addWidget(self.banner_label) # Infobanner ins Layout einfügen
		layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)  # Bild ins Layout einfügen
		layout.addStretch()  # Platz nach dem Bild
		layout.addLayout(button_layout)  # Button-Anordnung zur Hauptanordnung hinzufügen

		self.setLayout(layout)  # Anwenden des Layouts
		self.capture_frame()  # aufrufen der capture_frame, nimmt das Bild zur Festlegung der ROIs auf

	def set_camera_index(self):
		"""Ändert den Kameraindex zur Laufzeit"""
		try:
			self.logic.detector.cap.release() # Aktuelle Kamera schließen
			self.logic.detector.cap = cv2.VideoCapture(self.camera_selector.currentIndex(), cv2.CAP_DSHOW) # Neue Kamera öffnen
			self.logic.detector.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # MJPEG-Format erzwingen
			self.logic.detector.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
			self.logic.detector.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
			self.logic.detector.cap.set(cv2.CAP_PROP_FPS, 30)  # Versucht, die FPS auf 30 zu setzen
			print(f"Kameraindex erfolgreich auf {self.camera_selector.currentIndex()} gesetzt.")
			self.capture_frame()  # direkt neues Bild laden

		except Exception as e:
			print(f"Fehler beim Setzen des Kameraindex: {e}")

	def check_relais_state(self):
		"""Überwacht den Schaltzustand des Relais und reagiert auf Änderungen"""
		current_state = self.logic.relais.relais_bool
		if current_state != self.last_relais_state:
			self.last_relais_state = current_state
			self.on_relais_state_changed(current_state)

	def on_relais_state_changed(self, state):
		"""Führe hier deine gewünschte Reaktion auf den Zustandswechsel aus"""
		if not self.start_detection_bool: # Verhindert das Verändern der Buttons, solange das Programm noch nicht läuft
			if state: # Wenn das Relais eingeschaltet ist, ausschaltbutton aktiv setzen und einschaltbutton inaktiv
				self.relais_on_button.setVisible(False)
				self.relais_off_button.setVisible(True)

			else: # Wenn das Relais ausgeschaltet ist, einschaltbutton aktiv setzen und ausschaltbutton inaktiv
				self.relais_on_button.setVisible(True)
				self.relais_off_button.setVisible(False)

	def capture_frame(self):
		"""Nimmt Einzelbild zum Setzen der ROIs auf"""
		cap = self.logic.detector.cap  # Nutze das bereits geöffnete Kamera-Objekt aus keye_detection.py
		cap.set(3, 1280)  # Setzt die Breite des Kamera-Frames auf 1280 Pixel
		cap.set(4, 720)  # Setzt die Höhe des Kamera-Frames auf 720 Pixel
		for _ in range(3): # Kamera warmlaufen lassen, sonst blackscreen
			cap.read()
		ret, frame = cap.read()  # Nimmt ein Einzelbild auf

		if ret:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Konvertiert das Bild in RGB
			frame = cv2.flip(frame, 1)  # Spiegelt das Bild horizontal
			self.image = cv2.resize(frame,(self.image_width, self.image_height))  # Skaliert das Bild auf die Fenstergröße
			self.show_frame()  # Zeigt das Bild im GUI-Fenster an
			self.set_index_once = True

		else:
			if self.set_index_once:
				self.set_index_once = False
				self.camera_selector.setCurrentIndex(0)  # setzt automatisch "Kamera 0" wenn gewählte kamera nicht verfügbar
				self.set_camera_index()
				print("Kamerabild konnte nicht geladen werden")  # Fehlerausgabe, falls kein Bild aufgenommen werden konnte

	def show_frame(self):
		"""Zeigt das Bild aus capture_frame zum Setzen der ROIs in der UI an"""
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
			x1, y1, x2, y2 = self.temp_roi  # setzt Variablen zum berechnen der ROI-Koordinaten
			painter.drawRect(x1, y1, x2 - x1, y2 - y1)  # zeichnet die ROIs auf dem Bild ein

		painter.end()  # Beendet den Painter
		return pixmap  # Gibt das geänderte Bild zurück

	def mousePressEvent(self, event):
		"""Erfasst die Mausposition, speichert die ROI-Punkte und zeigt ein temporäres Rechteck an."""
		if len(self.roi_points) < 4:  # Solange noch nicht die beiden ROIs festgelegt sind können weitere Punkte festgelegt werden
			x = int(event.pos().x() - self.label.geometry().x())  # Ermittelt die x-Koordinate der Maus relativ zum Bild, indem der Abstand zum linken Rand des QLabel-Widgets subtrahiert wird
			y = int(event.pos().y() - self.label.geometry().y())  # Ermittelt die y-Koordinate der Maus relativ zum Bild, indem der Abstand zum oberen Rand des QLabel-Widgets subtrahiert wird
			x = max(0, min(x, self.label.width() - 1))  # Stellt sicher, dass x innerhalb der Bildgrenzen bleibt (0 bis Bildbreite - 1), um Fehler durch negative oder zu große Werte zu vermeiden
			y = max(0, min(y, self.label.height() - 1))  # Stellt sicher, dass y innerhalb der Bildgrenzen bleibt (0 bis Bildhöhe - 1)

			self.roi_points.append((x, y))  # Speichert den angepassten Mauspunkt als ROI-Koordinate in der Liste der ROI-Punkte
			self.temp_roi = (x, y, x, y)  # Initialisiert ein temporäres ROI-Rechteck mit einer Start- und Endposition, die zunächst identisch sind (dies wird später erweitert, wenn der zweite Punkt gesetzt wird)

			if len(self.roi_points) % 2 == 0: # Wenn zwei Punkte für ein Rechteck vorhanden sind, werden sie automatisiert den richtigen ROI-punkten zugeordnet, egal in welcher Reihenfolge sie gesetzt wurden
				x1, y1 = self.roi_points[-2]  # Erster gesetzter Punkt
				x2, y2 = self.roi_points[-1]  # Zweiter gesetzter Punkt

				# Berechnet den oberen linken und unteren rechten Punkt unabhängig von der Eingabereihenfolge
				x_tl = min(x1, x2)  # Oberste linke X-Koordinate
				y_tl = min(y1, y2)  # Oberste linke Y-Koordinate
				x_br = max(x1, x2)  # Unterste rechte X-Koordinate
				y_br = max(y1, y2)  # Unterste rechte Y-Koordinate

				self.roi_points[-2] = (x_tl, y_tl) # Ersetzt die letzten beiden ROI-Punkte durch die sortierten Werte
				self.roi_points[-1] = (x_br, y_br)

			print(f"mousePressEvent: ROI {self.current_roi}: Punkt {len(self.roi_points) % 2 + 1} gesetzt: {x}, {y}")
			self.show_frame()  # zeigt das Bild aktualisiert mit den aktuellen ROIs an, falls es welche gibt
			if len(self.roi_points) >= 4 and self.start_detection_bool:
				self.banner_label.setText("Sicherheitszonen gesetzt! Sie können das Programm starten oder die Zonen zurücksetzen.") # Nutzerinfo aktualisieren
				self.confirm_button.setVisible(True)  # aktiviert den confirm_button, falls die ROI gesetzt wurden
				self.retake_picture_button.setVisible(False)  # Blendet den Bild-wiederholen-Button aus
				self.camera_selector.setVisible(False)
			else:
				self.banner_label.setText("Bitte spannen Sie zwei Sicherheitszonen auf, indem Sie jeweils zwei Eckpunkte anklicken oder nehmen Sie das Bild erneut auf.") # Nutzerinfo aktualisieren
				self.retake_picture_button.setVisible(True)  # Blendet den Bild-wiederholen-Button ein
				self.camera_selector.setVisible(True)
				self.confirm_button.setVisible(False)  # deaktiviert den confirm_button, falls die ROI resettet wurden

	def confirm_rois(self):
		"""Bestätigt die gesetzten ROIs und übergibt sie an die Entscheidungslogik."""
		roi1 = (self.roi_points[0][0] / self.image_width, self.roi_points[0][1] / self.image_height,  # ROI Koordinaten in absolute Werte zwischen 0 und 1 umrechnen und speichern
				self.roi_points[1][0] / self.image_width, self.roi_points[1][1] / self.image_height)
		roi2 = (self.roi_points[2][0] / self.image_width, self.roi_points[2][1] / self.image_height,
				self.roi_points[3][0] / self.image_width, self.roi_points[3][1] / self.image_height)
		print("GUI.confirm_rois: ", roi1, roi2)

		# Ändert die Buttons von den ROI reset und Start zu Relais ein und aus
		self.camera_selector.setVisible(False) # Blendet das Dropdown aus
		self.confirm_button.setVisible(False)  # Blendet den Start-Button aus
		self.start_detection_bool = False  # deaktiviert den confirm_button dauerhaft
		self.roi_reset_button.setVisible(False)  # Blendet den ROI-Reset-Button aus
		self.retake_picture_button.setVisible(False)  # Blendet den Bild-wiederholen-Button aus
		self.relais_on_button.setVisible(True)  # Zeigt den Relais-EIN-Button an
		self.relais_off_button.setVisible(True)  # Zeigt den Relais-AUS-Button an

		self.banner_label.setText("Bitte spannen Sie zwei Sicherheitszonen auf, indem Sie jeweils zwei Eckpunkte anklicken oder nehmen Sie das Bild erneut auf.")  # Nutzerinfo aktualisieren

		self.logic.set_rois(roi1, roi2)  # ROI werte an die decision_logic übergeben

		self.logic.detector.set_frame_callback(self.update_frame)  # Setzt das Frame-Update-Callback für das Live-Bild der Erkennung
		detection_thread = threading.Thread(target=self.logic.start_detection)  # Startet die Personenerkennung als separaten Thread, damit andere Teile des Programms weiterlaufen können
		detection_thread.start()

	def roi_reset(self):
		self.banner_label.setText("Spannen Sie zwei Sicherheitszonen durch jeweils zwei Punkte auf oder nehmen Sie das Bild erneut auf.")  # Nutzerinfo aktualisieren
		self.roi_points.clear()  # leert die Liste der gesetzten ROI-punkte
		self.show_frame()  # zeigt das Bild aktualisiert ohne ROIs
		self.retake_picture_button.setVisible(True)  # aktiviert den Bild noch einmal aufnehmen Button
		self.camera_selector.setVisible(True) # aktiviert das Kamera-auswählen-Dropdown
		self.confirm_button.setVisible(False)  # deaktiviert den confirm_button

	def update_frame(self, frame):
		"""Aktualisiert das Bild in der GUI mit einem neuen Frame."""
		if frame is not None:
			frame_resized = cv2.resize(frame, (self.label.width(), self.label.height()), interpolation=cv2.INTER_AREA) # Bild auf die Größe des QLabel-Widgets skalieren
			height, width, channel = frame_resized.shape  # Bilddimensionen bestimmen
			bytes_per_line = 3 * width  # Byte-Anzahl pro Zeile berechnen (RGB = 3 Kanäle)
			q_img = QImage(frame_resized.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)  # QImage aus den Bilddaten erstellen
			pixmap = QPixmap.fromImage(q_img)  # QPixmap für PyQt erzeugen
			self.label.setPixmap(pixmap)  # Das Bild im GUI-Label aktualisieren

	def closeEvent(self, event):
			"""Führt die Funktion zum sicheren Beenden beim Schließen des Fensters aus"""
			self.logic.shutdown()  # beendet die decision_logic Instanz
			self.close()  # schließt das Fenster