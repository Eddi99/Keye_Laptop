import cv2
from ultralytics import YOLO


class ObjectDetection:
    def __init__(self, model_path="yolo11s.pt"):
        self.cap = cv2.VideoCapture(1)      # Hierher kommt das Bild der Webcam. Die Integrierte hat in der Regel den Index 0, je nachdem wie viele Geräte angeschlossen sind, muss man hier evenutell änderungen für die richtige Webcam vornehmen.
        self.cap.set(3, 1280)  # Set width
        self.cap.set(4, 720)  # Set height
        self.model = YOLO(model_path)
        self.target_object = "person"
        self.zone_x_min, self.zone_x_max = 0.4, 0.6
        self.zone_y_min, self.zone_y_max = 0.3, 0.7
        self.in_zone_frames = 0
        self.out_zone_frames = 0
        self.is_active = False

    def detect_objects(self, frame):
        results = self.model(frame, imgsz=320)
        detections = results[0].boxes.data.cpu().numpy()
        object_in_zone = False

        for det in detections:
            x_min, y_min, x_max, y_max, confidence, class_id = det
            center_x = (x_min + x_max) / 2 / frame.shape[1]
            center_y = (y_min + y_max) / 2 / frame.shape[0]

            if self.zone_x_min <= center_x <= self.zone_x_max and self.zone_y_min <= center_y <= self.zone_y_max:
                object_in_zone = True

        if object_in_zone:
            self.in_zone_frames += 1
            self.out_zone_frames = 0
            if self.in_zone_frames >= 4 and not self.is_active:
                self.is_active = True
                print("Person detected in ROI - Alarm triggered!")
        else:
            self.out_zone_frames += 1
            self.in_zone_frames = 0
            if self.out_zone_frames >= 5 and self.is_active:
                self.is_active = False
                print("No person in ROI - Alarm deactivated!")

        return results

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Couldn't retrieve frame.")
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detect_objects(frame_rgb)
            annotated_frame = results[0].plot()

            inference_time = results[0].speed['inference']
            fps = 1000 / inference_time
            cv2.putText(annotated_frame, f'FPS: {fps:.1f}', (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Webcam YOLO", cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(1) == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = ObjectDetection()
    detector.run()