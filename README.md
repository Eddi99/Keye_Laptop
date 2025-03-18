# Sicherheitssystem für Hochspannungslabore
Keye - ein YOLO-basiertes Sicherheitssystem welches mit Hilfe von Echtzeit Bildauswertung eine Abschaltung von Prüfständen auslöst

## Installation
### Voraussetzungen
Core i5 oder besser
USB Webcam
HID fähige USB-Relaiskarte

### Setup
Zum Starten Ordner entpacken, setup.sh ausführen und exe starten (keye_Laptop\dist\Keye.exe)

### Fehlerbehebung:
- Wenn die anwendung nicht startet, ggf. über Konsole zunächst mit Keye_venv\Scripts\activate die virtuelle Umgebung
  starten und dann main.py ausführen.
- Bei schwarzem Bild ggf. Webcam Treiber deinstallieren und standard USB Treiber verwenden
- Bei Kamerafehler, wenn keine interne Webcam vorhanden ist ggf. im Skript keye_detection.py in der init bei self.cap = cv2.VideoCapture(0) 1 einsetzen.

### Autor
Erstellt von Edgar Coy im Rahmen der Bachelor-Thesis an der FH Kiel 2025.
