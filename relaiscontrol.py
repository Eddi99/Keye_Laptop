import pywinusb.hid as hid  # Bibliothek für USB-HID-Kommunikation


class RelaisControl:
    def __init__(self, vendor_id=0x16C0, device_id=0x05DF):
        """Initialisiert die Relais-Steuerung. Sucht nach einem passenden USB-HID-Relaisgerät und öffnet die Verbindung."""
        self.vendor_id = vendor_id  # Speichert die Vendor ID des Geräts
        self.device_id = device_id  # Speichert die Device ID des Geräts
        self.device = None  # Initialisiert das Gerät als None, bevor es erkannt wird
        self.report = None  # Initialisiert das Report-Objekt als None, bevor es geladen wird

        self.relais_bool = False # gibt der GUI auskunft über den derzeitigen Schaltstatus des Relais

        try:
            self.get_hid_usb_relay()  # Sucht nach dem passenden HID-Relaisgerät
            self.open_device()  # Öffnet die Verbindung zum gefundenen Gerät
        except Exception as e:
            print(
                f"init: Fehler bei der Initialisierung des Relais: {e}")  # Gibt eine Fehlermeldung aus, falls die Initialisierung fehlschlägt

    def get_hid_usb_relay(self):
        """Sucht nach einem USB-Relais mit den gegebenen Vendor- und Device-IDs."""
        try:
            filter = hid.HidDeviceFilter(vendor_id=self.vendor_id,
                                         product_id=self.device_id)  # Erstellt einen Filter für das gewünschte Gerät
            devices = filter.get_devices()  # Sucht nach verfügbaren Geräten
            if devices:
                self.device = devices[0]  # Speichert das erste gefundene Gerät in der Variablen
            else:
                raise RuntimeError("get_hid_usb_relay: Kein passendes USB-Relaisgerät gefunden.")  # Falls kein Gerät gefunden wird, wird ein Fehler ausgegeben
        except Exception as e:
            print(f"get_hid_usb_relay: Fehler bei der Relaissuche: {e}")  # Gibt eine Fehlermeldung aus

    def open_device(self):
        """Öffnet die Verbindung zum USB-Relais, falls es verfügbar ist."""
        try:
            if self.device and not self.device.is_opened():  # Prüft, ob das Gerät existiert und noch nicht geöffnet ist
                self.device.open()  # Öffnet die Verbindung zum HID-Gerät
                print("open_device: Relais erfolgreich verbunden!")
                self.get_report()  # Lädt das Report-Objekt des Geräts
            else:
                raise RuntimeError("open_device: Relais nicht verfügbar oder bereits geöffnet.")  # Fehler, falls das Gerät nicht vorhanden oder bereits offen ist
        except Exception as e:
            print(f"open_device: Fehler beim Öffnen des Relais-Gerätes: {e}")  # Gibt eine Fehlermeldung aus

    def close_device(self):
        """Schließt die Verbindung zum USB-Relais, falls es geöffnet ist."""
        try:
            if self.device and self.device.is_opened():  # Prüft, ob das Gerät existiert und geöffnet ist
                self.off_all()  # Schaltet das Relais aus, bevor es geschlossen wird
                self.device.close()  # Schließt die Verbindung zum Gerät
                self.device = None  # Setzt das Gerät auf None, um weitere Aufrufe zu verhindern
                print("close_device: Relais-Verbindung erfolgreich geschlossen.")  # Gibt eine Bestätigung aus
            else:
                print("close_device: Relais-Verbindung ist bereits geschlossen oder nicht verfügbar.")  # Falls das Gerät nicht offen ist, wird dies ausgegeben
        except Exception as e:
            print(f"close_device: Fehler beim Schließen der Relaisverbindung: {e}")  # Gibt eine Fehlermeldung aus

    def get_report(self):
        """Liest das Report-Objekt des Geräts aus, um es für Steuerbefehle nutzen zu können."""
        try:
            if self.device:  # Prüft, ob ein Gerät vorhanden ist
                reports = self.device.find_output_reports() + self.device.find_feature_reports()  # Sammelt alle Output- und Feature-Reports
                if reports:
                    self.report = reports[0]  # Speichert das erste gefundene Report-Objekt
                else:
                    raise RuntimeError(
                        "get_report: Kein gültiger Output-Report gefunden.")  # Falls kein Report gefunden wird, wird ein Fehler ausgegeben
        except Exception as e:
            print(f"get_report: Fehler beim Abrufen des Reports: {e}")  # Gibt eine Fehlermeldung aus

    def write_row_data(self, buffer):
        """Sendet ein Steuerkommando an das Relais. Das Kommando wird als Byte-Array übergeben und an das Gerät gesendet."""
        try:
            if self.report is not None:  # Prüft, ob ein gültiges Report-Objekt vorhanden ist
                self.report.send(raw_data=buffer)  # Sendet das Steuerkommando an das Relais
                return True  # Gibt True zurück, falls das Kommando erfolgreich gesendet wurde
            else:
                raise RuntimeError(
                    "write_row_data: Kann nicht schreiben: Kein gültiges Report-Objekt.")  # Falls kein Report-Objekt vorhanden ist, wird ein Fehler ausgegeben
        except Exception as e:
            print(f"write_row_data: Fehler beim Schreiben des Relais-Befehls: {e}")  # Gibt eine Fehlermeldung aus
            return False  # Gibt False zurück, falls das Schreiben fehlgeschlagen ist

    def on_all(self):
        """Schaltet alle Relais ein. Falls der Befehl nicht gesendet werden kann, wird eine Fehlermeldung ausgegeben."""
        try:
            if self.write_row_data([0, 0xFE, 0, 0, 0, 0, 0, 0, 1]):  # Sendet den Steuerbefehl zum Einschalten
                self.relais_bool = True # GUI kann ablesen, dass das Relais eingeschaltet ist
                print("on_all: Relais wurde eingeschaltet.")  # Gibt eine Bestätigung aus
                return True
            else:
                raise RuntimeError(
                    "on_all: Fehler beim Einschalten der Relais.")  # Fehler, falls das Einschalten nicht funktioniert
        except Exception as e:
            print(f"Fehler in on_all(): {e}")  # Gibt eine Fehlermeldung aus
            return False  # Gibt False zurück, falls das Einschalten fehlgeschlagen ist

    def off_all(self):
        """Schaltet alle Relais aus. Falls der Befehl nicht gesendet werden kann, wird eine Fehlermeldung ausgegeben."""
        try:
            if self.write_row_data([0, 0xFC, 0, 0, 0, 0, 0, 0, 1]):  # Sendet den Steuerbefehl zum Ausschalten
                self.relais_bool = False # GUI kann ablesen, dass das Relais ausgeschaltet ist
                print("off_all: Relais wurde ausgeschaltet.")  # Gibt eine Bestätigung aus
                return True
            else:
                raise RuntimeError(
                    "off_all: Fehler beim Ausschalten der Relais.")  # Fehler, falls das Ausschalten nicht funktioniert
        except Exception as e:
            print(f"Fehler in off_all(): {e}")  # Gibt eine Fehlermeldung aus
            return False  # Gibt False zurück, falls das Ausschalten fehlgeschlagen ist
