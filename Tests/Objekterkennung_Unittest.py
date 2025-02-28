import cv2
from ultralytics import YOLO
import os


# Test: Ist das Modell korrekt geladen?
def test_model_loading():
    model = YOLO("yolo11s.pt")
    assert model is not None, "Modell konnte nicht geladen werden!"
    print("Verfügbare Klassen im Modell: ", model.names)


# Test: Funktioniert die Webcam?
def test_webcam():
    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), "Kamera konnte nicht geöffnet werden!"
    cap.release()


# Test: Kann YOLO ein Testbild verarbeiten?
def test_yolo_inference():
    model = YOLO("yolo11s.pt")
    img_path = "testbild.jpg"
    assert os.path.exists(img_path), "Testbild fehlt!"

    img = cv2.imread(img_path)
    results = model(img, imgsz=640, conf=0.3)

    assert results is not None, "YOLO liefert keine Ergebnisse!"
    assert len(results[0].boxes.xyxy) > 0, "Keine Objekte erkannt!"


# Test: Ist die FPS-Berechnung sinnvoll?
def test_fps_calculation():
    import time
    model = YOLO("yolo11s.pt")
    img = cv2.imread("testbild.jpg")

    start_time = time.time()
    results = model(img, imgsz=320)
    end_time = time.time()

    fps = 1 / (end_time - start_time)
    assert fps > 5, "FPS ist zu niedrig!"  # Falls FPS < 5, läuft YOLO sehr langsam


# Test: Funktioniert die ROI-Erkennung mit Video?
def test_roi_video():
    model = YOLO("yolo11s.pt")
    cap = cv2.VideoCapture("testvideo.mp4")
    assert cap.isOpened(), "Testvideo konnte nicht geöffnet werden!"

    zone_x_min, zone_x_max = 0.4, 0.6
    zone_y_min, zone_y_max = 0.3, 0.7
    object_detected = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, imgsz=640, conf=0.3)
        detections = results[0].boxes.data.cpu().numpy()

        for det in detections:
            x_min, y_min, x_max, y_max, confidence, class_id = det
            center_x = (x_min + x_max) / 2 / frame.shape[1]
            center_y = (y_min + y_max) / 2 / frame.shape[0]

            if zone_x_min <= center_x <= zone_x_max and zone_y_min <= center_y <= zone_y_max:
                object_detected = True
                break

        if object_detected:
            break

    cap.release()
    assert object_detected, "Keine Person in der definierten ROI im Video erkannt!"
