import sys
import os

import cv2

from PyQt6.QtCore import QTimer 
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication

from models.face_recognizer import FaceRecognizer
from ui_webcam_viewer import Ui_MainWindow

LOCAL_DIR = os.getcwd()

class WebcamViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        with open(os.path.join(LOCAL_DIR, "style.qss"), "r") as style_file:
            style_config = style_file.read()
        self.setStyleSheet(style_config)

        self.detection = False
        self.face_recognizer = FaceRecognizer(root=LOCAL_DIR)
        self.setup_face_reg()
    
    def setup_face_reg(self):
        DEFAULT_CAMERA = 0
        self.capture = cv2.VideoCapture(DEFAULT_CAMERA)
        self.ui.button.clicked.connect(self.detection_on)
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_frame(self.detection))
        self.timer.start(30)

    def update_frame(self, detection):
        """
        RECOGNIZER
        """
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
    
    def detection_on(self):
        self.detection = True
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamViewer()
    window.show()
    sys.exit(app.exec())
