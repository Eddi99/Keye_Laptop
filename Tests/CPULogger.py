import psutil
import wmi
import time
import csv

# WMI-Objekt für Sensordaten erstellen
w = wmi.WMI(namespace="root\wmi")

def get_cpu_usage():
    """Liest die aktuelle CPU-Auslastung (%) aus"""
    return psutil.cpu_percent(interval=1)


def get_ram_usage():
    """Liest die aktuelle RAM-Nutzung (MB) aus"""
    ram = psutil.virtual_memory()
    return ram.used / (1024 * 1024)  # In MB


# CSV-Datei zum Loggen erstellen
with open("system_log.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Zeit", "CPU-Auslastung (%)", "RAM-Nutzung (MB)"])

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cpu = get_cpu_usage()
        ram = get_ram_usage()

        writer.writerow([timestamp, cpu, ram])
        print(f"{timestamp}  und Ram-| CPU: {cpu}% | RAM: {ram} MB")

        time.sleep(5)  # Logge alle 5 Sekunden
