import cv2


def test_webcam_live():
    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), "Webcam konnte nicht gestartet werden!"

    for _ in range(10):  # 10 Frames testen
        ret, frame = cap.read()
        assert ret, "Kamera gibt kein Bild zurück!"

    cap.release()


test_webcam_live()
print("✅ Integrationstest bestanden!")
