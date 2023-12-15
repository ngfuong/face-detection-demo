import sys
import os
import copy
import cv2

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap, QColorConstants
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QGraphicsDropShadowEffect

from models.face_recognizer import FaceRecognizer
from ui_webcam_viewer import Ui_MainWindow

LOCAL_DIR = os.getcwd()
DEFAULT_PAGE_IDX = 0
CAPTURE_PAGE_IDX = 1
SUCCESSFUL_PAGE_IDX = 2

class WebcamViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        with open(os.path.join(LOCAL_DIR, "style.qss"), "r") as style_file:
            style_config = style_file.read()
        self.setStyleSheet(style_config)

        self.timer = QTimer(self)

        self.ui.stackedWidget.setCurrentIndex(DEFAULT_PAGE_IDX)
        self.drop_shadow(self.ui.webcam)

        self.ui.capture_button.clicked.connect(self.capture_face)
        self.ui.ok_button.clicked.connect(self.ok_button_clicked)
        
        self.detection = False
        self.face_recognizer = FaceRecognizer(root=LOCAL_DIR)
        self.setup_webcam()
    
    def capture_face(self):
        self.ui.stackedWidget.setCurrentIndex(CAPTURE_PAGE_IDX)
        ret, frame = self.capture.read()
        self.timer.stop()
        if ret:
            frame = cv2.flip(frame, 1)
            captured_frame = copy.deepcopy(frame)
            num_faces, faces = self.face_recognizer.detect_faces(frame)
            if num_faces == 1:
                self.ui.save_button.clicked.connect(lambda: self.save_data(captured_frame))
                # Add box for faces
                for face in faces:
                    box = list(map(int, face[:4]))
                    color = (0, 0, 255)
                    thickness = 2
                    detected_frame = cv2.rectangle(frame, box, color, thickness, cv2.LINE_AA)
                # Display captured image with detected box
                img = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = img.shape
                qt_img = QImage(img.data, w, h, ch*w, QImage.Format.Format_RGB888)
                self.ui.webcam.setPixmap(QPixmap.fromImage(qt_img))
                msg = "Face captured"
            elif num_faces == 0:
                msg = "No face detected"
            else:
                msg = "Too many faces"

    def save_data(self, image):
        label = self.ui.name_input.text().strip()
        if label:
            cv2.imwrite(f"images\{len(self.face_recognizer.face_data)}_{label}.jpg", image)
            msg = "Saved succesfully!"
            # Update data
            self.face_recognizer.face_data = self.face_recognizer.load_faces()
        else:
            msg = "Empty label!"
        self.ui.stackedWidget.setCurrentIndex(SUCCESSFUL_PAGE_IDX)
        self.ui.message.setText(msg)
    
    def setup_webcam(self):
        DEFAULT_CAMERA = 0
        self.capture = cv2.VideoCapture(DEFAULT_CAMERA)
        self.ui.detect_button.clicked.connect(self.detection_toggle)
        self.timer.timeout.connect(lambda: self.update_frame(detection=self.detection))
        self.timer.start(30)

    def update_frame(self, detection=False):
        ret, frame = self.capture.read()
        frame = cv2.flip(frame, 1)

        if ret:
            # Convert BGR to RGB
            if detection:
                frame = self.face_recognizer.run(frame)
            rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape

            # Create QImage
            qt_img = QImage(rgb_img.data, w, h, ch*w, QImage.Format.Format_RGB888)
            self.ui.webcam.setPixmap(QPixmap.fromImage(qt_img))
        else:
            # print("Error capturing frame")
            pass
        
    def closeEvent(self, event):
        self.capture.release()
        event.accept()
    
    def detection_toggle(self):
        if self.detection is False:
            self.detection = True
            self.ui.detect_button.setText("Stop Detection")
        else:
            self.detection = False
            self.ui.detect_button.setText("Detect")
    
    def ok_button_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(DEFAULT_PAGE_IDX)
        self.timer.start(30)
    
    def drop_shadow(self, target_widget:QWidget):
        """
        Drop Shadow effect
        """
        effect = QGraphicsDropShadowEffect(target_widget)
        effect.setColor(QColorConstants.Black)
        effect.setOffset(0,5)
        effect.setBlurRadius(30)
        target_widget.setGraphicsEffect(effect)
        target_widget.setContentsMargins(0,0,0,0)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamViewer()
    window.show()
    sys.exit(app.exec())
