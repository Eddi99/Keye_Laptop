import pywinusb.hid as hid  # Bibliothek für USB-HID-Kommunikation

class RelaisControl:
    def __init__(self, vendor_id=0x16c0, device_id=0x05DF):
        self.vendor_id = vendor_id  # Speichert die Vendor ID
        self.device_id = device_id  # Speichert die Device ID
        self.device = None  # Initialisiert das Gerät als None
        self.report = None  # Initialisiert das Report-Objekt als None
        self.get_hid_usb_relay()  # Ruft die Geräteerkennung auf
        self.open_device()  # Öffnet das Gerät

    def get_hid_usb_relay(self):  # Sucht nach einem USB-Relais mit den gegebenen Vendor- und Device-IDs.
        device_filter = hid.HidDeviceFilter(vendor_id=self.vendor_id, product_id=self.device_id)  # Erstellt einen Filter für das gewünschte Gerät anhand der Vendor- und Produkt-ID
        devices = device_filter.get_devices()  # Sucht nach passenden Geräten
        if devices:  # Falls mindestens ein Gerät gefunden wurde
            self.device = devices[0]  # Speichert das erste gefundene Gerät in der Instanzvariable

    def open_device(self):
        """Öffnet die Verbindung zum USB-Relais, falls es verfügbar ist."""
        if self.device is None:
            print("Kein USB-Relais gefunden! Stelle sicher, dass es angeschlossen ist.")
            return

        if not self.device.is_opened():
            try:
                self.device.open()
                self.get_report()
                self.on_all()
            except Exception as e:
                print(f"Fehler beim Öffnen des Geräts: {e}")
                import traceback
                traceback.print_exc()

    def close_device(self):  # Schließt die Verbindung zum USB-Relais, falls es geöffnet ist.
        if self.device and self.device.is_opened():  # Prüft, ob das Gerät existiert und aktuell geöffnet ist
            self.off_all()  # Schaltet alle Relais aus, bevor die Verbindung geschlossen wird
            self.device.close()  # Schließt die Verbindung zum Gerät

    def get_report(self):  # Liest das Report-Objekt des Geräts aus.
        if self.device:  # Prüft, ob ein Gerät vorhanden ist
            reports = self.device.find_output_reports() + self.device.find_feature_reports()  # Sucht nach Output- und Feature-Reports
            if reports:  # Falls mindestens ein Report gefunden wurde
                self.report = reports[0]  # Speichert das erste gefundene Report-Objekt

    def write_row_data(self, buffer):
        """Sendet ein Steuerkommando an das Relais."""
        if self.report is not None:
            print(f"Sende Daten an Relais: {buffer}")
            try:
                self.report.send(raw_data=buffer)
                print("Relais erfolgreich geschaltet!")
                return True
            except Exception as e:
                print(f"Fehler beim Senden an das Relais: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("Kein gültiges Report-Objekt. Ist das Relais noch verbunden?")
            return False

    def on_all(self):
        """Schaltet alle Relais ein."""
        try:
            print("Versuche, Relais EINzuschalten...")
            if self.write_row_data([0, 0xFE, 0, 0, 0, 0, 0, 0, 1]):
                print("Relaiskreislauf eingeschaltet!")
                return True
            else:
                print("Fehler: Relais konnten nicht eingeschaltet werden!")
                return False
        except Exception as e:
            print(f"Fehler in on_all: {e}")
            import traceback
            traceback.print_exc()
            return False

    def off_all(self):
        """Schaltet alle Relais aus."""
        try:
            print("Versuche, Relais AUSzuschalten...")
            if self.write_row_data([0, 0xFC, 0, 0, 0, 0, 0, 0, 1]):
                print("Relaiskreislauf ausgeschaltet!")
                return True
            else:
                print("Fehler: Relais konnten nicht ausgeschaltet werden!")
                return False
        except Exception as e:
            print(f"Fehler in off_all: {e}")
            import traceback
            traceback.print_exc()
            return False
