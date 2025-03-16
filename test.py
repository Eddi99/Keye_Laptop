import numpy as np
import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # DirectShow verwenden
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # MJPEG-Format erzwingen
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler: Kein gültiges Frame erhalten!")
        break

    avg_brightness = np.mean(frame)  # Durchschnittliche Helligkeit berechnen
    print(f"Durchschnittliche Helligkeit: {avg_brightness}")

    cv2.imshow("Externe Kamera - DirectShow", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
