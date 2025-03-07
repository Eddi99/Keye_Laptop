import pywinusb.hid as hid  # Bibliothek für USB-HID-Kommunikation
from time import sleep  # Für Wartezeiten
import keyboard  # Für Tastatureingaben

class RelaisControl:
    def __init__(self, vendor_id=0x16c0, device_id=0x05DF):
        self.vendor_id = vendor_id  # Speichert die Vendor ID
        self.device_id = device_id  # Speichert die Device ID
        self.device = None  # Initialisiert das Gerät als None
        self.report = None  # Initialisiert das Report-Objekt als None
        self.get_hid_usb_relay()  # Ruft die Geräteerkennung auf
        self.open_device()  # Öffnet das Gerät

    def get_hid_usb_relay(self): #Sucht nach einem USB-Relais mit den gegebenen Vendor und Device IDs."""
        filter = hid.HidDeviceFilter(vendor_id=self.vendor_id, product_id=self.device_id)
        devices = filter.get_devices()
        if devices:
            self.device = devices[0]  # Speichert das erste gefundene Gerät

    def open_device(self): #Öffnet die Verbindung zum USB-Relais, falls es verfügbar ist.
        if self.device and not self.device.is_opened():
            self.device.open()
            self.get_report()
            self.on_all() # schaltet das Relais zu anfang direkt an, damit der Sicherheitskreis geschlossen ist

    def close_device(self): #Schließt die Verbindung zum USB-Relais, falls es geöffnet ist.
        if self.device and self.device.is_opened():
            self.device.close()

    def get_report(self): #Liest das Report-Objekt des Geräts aus.
        if self.device:
            reports = self.device.find_output_reports() + self.device.find_feature_reports()
            if reports:
                self.report = reports[0]  # Speichert das erste gefundene Report-Objekt

    def read_status_row(self): #Liest den aktuellen Status des Relais aus.
        if self.report is None:
            print("Cannot read report")
            return [0, 1, 0, 0, 0, 0, 0, 0, 3]
        return self.report.get()

    def write_row_data(self, buffer): #Sendet ein Steuerkommando an das Relais.
        if self.report is not None:
            self.report.send(raw_data=buffer)
            return True
        else:
            print("Cannot write to the report. Check if your device is still plugged in.")
            return False

    def on_all(self): #Schaltet alle Relais ein.
        if self.write_row_data([0, 0xFE, 0, 0, 0, 0, 0, 0, 1]):
            return self.read_relay_status(3)
        else:
            print("Cannot turn ON all relays")
            return False

    def off_all(self): #Schaltet alle Relais aus.
        if self.write_row_data([0, 0xFC, 0, 0, 0, 0, 0, 0, 1]):
            return self.read_relay_status(3)
        else:
            print("Cannot turn OFF all relays")
            return False

    def read_relay_status(self, relay_number): #Überprüft, ob ein bestimmtes Relais eingeschaltet ist.
        buffer = self.read_status_row()
        return relay_number & buffer[8]

    def is_relay_on(self, relay_number): #Gibt zurück, ob ein bestimmtes Relais aktiv ist.
        return self.read_relay_status(relay_number) > 0
