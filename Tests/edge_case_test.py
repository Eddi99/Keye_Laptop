import cv2
from ultralytics import YOLO

#Test mit einem leeren Bild
def test_empty_scene():
    model = YOLO("yolo11s_ncnn")
    img = cv2.imread("leeres_bild.jpg")  # Ein Bild ohne Objekte

    results = model(img, imgsz=640)
    assert len(results[0].boxes.xyxy) == 0, "Fehler: YOLO erkennt Geister-Objekte!"

# Test mit einem gemusterten Bild ohne Objekt
def test_random_scene():
    model = YOLO("yolo11s_ncnn")
    img = cv2.imread("gemustertes_bild.jpg")  # Ein Bild ohne Objekte

    results = model(img, imgsz=640)
    assert len(results[0].boxes.xyxy) == 0, "Fehler: YOLO erkennt Geister-Objekte!"

    