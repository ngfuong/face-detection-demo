import sys
import os
import copy
import cv2

from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap, QColorConstants
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QGraphicsDropShadowEffect

from models.face_recognizer import FaceRecognizer
from ui_webcam_viewer import Ui_MainWindow

LOCAL_DIR = os.getcwd()
DEFAULT_PAGE_IDX = 0    # Empty Page
LOGIN_PAGE_IDX = 1       # Login and Register
REGISTER_PAGE_IDX = 2   # Register 
SUCCESSFUL_PAGE_IDX = 3 # Register Success
LOGIN_SUCCESS_PAGE_IDX = 4

class WebcamViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            self.ui = uic.loadUi(os.path.join(LOCAL_DIR, "webcam_viewer.ui"), self)
        except FileNotFoundError:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

        with open(os.path.join(LOCAL_DIR, "style.qss"), "r") as style_file:
            style_config = style_file.read()
        self.setStyleSheet(style_config)

        self.timer = QTimer(self)
        self.detect_timer = QTimer(self)

        self.DETECT_MSG = None

        self.ui.stackedWidget.setCurrentIndex(DEFAULT_PAGE_IDX)
        self.ui.topStackedWidget.setCurrentIndex(0)
        self.ui.next_button.clicked.connect(self.setup_login_page)

        self.ui.name_input.hide()
        self.ui.save_button.hide()
        self.ui.back_button.hide()
        self.ui.back_button.clicked.connect(self.back_to_login)

        self.drop_shadow(self.ui.webcam)

        self.ui.register_button.clicked.connect(self.capture_face)
        self.ui.ok_button.clicked.connect(self.ok_button_clicked)
        
        self.detection = False
    
    def setup_login_page(self):
        self.ui.stackedWidget.setCurrentIndex(LOGIN_PAGE_IDX)
        self.ui.topStackedWidget.setCurrentIndex(1)
        self.face_recognizer = FaceRecognizer(root=LOCAL_DIR)
        self.setup_webcam()
    
    def back_to_login(self):
        self.ui.stackedWidget.setCurrentIndex(LOGIN_PAGE_IDX)
        self.ui.topStackedWidget.setCurrentIndex(1)
        self.timer.start(120)

    def capture_face(self):
        self.ui.stackedWidget.setCurrentIndex(REGISTER_PAGE_IDX)
        ret, frame = self.capture.read()
        self.timer.stop()
        if ret:
            frame = cv2.flip(frame, 1)
            captured_frame = copy.deepcopy(frame)
            num_faces, faces = self.face_recognizer.detect_faces(frame)

            if faces is None or num_faces == 0:
                msg = "No face detected"
            elif num_faces == 1:
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
                self.ui.name_input.show()
                self.ui.save_button.show()
                msg = "Face captured"
            else:
                msg = "Too many faces"
            
            self.ui.back_button.show()
            self.ui.capture_msg.setText(msg)
            

    def save_data(self, image):
        label = self.ui.name_input.text().strip()
        if label:
            cv2.imwrite(f"images/{len(self.face_recognizer.face_data)}_{label}.jpg", image)
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

        self.ui.login_button.clicked.connect(self.detection_toggle)
        self.ui.msg_button.hide()

        self.timer.timeout.connect(lambda: self.update_frame(detection=self.detection))
        self.timer.start(120)
        self.detect_timer.timeout.connect(lambda:self.update_detect_text(detection=self.detection))
        self.detect_timer.start(2000)

    def update_detect_text(self, detection):
        if detection:
            self.ui.msg_button.setText(self.DETECT_MSG)

    def update_frame(self, detection=False):
        ret, frame = self.capture.read()
        frame = cv2.flip(frame, 1)

        id_name = None
        if ret:
            # Convert BGR to RGB
            if detection:
                frame, id_name, _ = self.face_recognizer.run(frame)
            rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape

            # Create QImage
            qt_img = QImage(rgb_img.data, w, h, ch*w, QImage.Format.Format_RGB888)
            self.ui.webcam.setPixmap(QPixmap.fromImage(qt_img))

            if id_name is None:
                self.DETECT_MSG = f"Position your face in the camera frame."
                self.ui.msg_button.show()
                self.ui.msg_button.setDisabled(True)
            elif id_name.startswith("unknown"):
                self.DETECT_MSG = "Are you new? Click Register Button."
                self.ui.msg_button.show()
                self.ui.msg_button.setDisabled(True)
            else:
                id_name = id_name.split("_")[1]
                self.DETECT_MSG = f"Click to login as {id_name}"
                self.ui.msg_button.clicked.connect(lambda: self.login_successful(name=id_name))
                self.ui.msg_button.setDisabled(False)
                self.ui.msg_button.setStyleSheet("""
                                                QPushButton {
                                                 font-size: 24px;
                                                }
                                                QPushButton:hover {
                                                 text-decoration: underline;
                                                }
                                                """)

        else:
            # print("Error capturing frame")
            pass
        
    def closeEvent(self, event):
        self.capture.release()
        event.accept()
    
    def detection_toggle(self):
        if self.detection is False:
            self.detection = True
            self.ui.login_button.setText("Stop Detection")
        else:
            self.detection = False
            self.ui.login_button.setText("Detect")
            self.ui.msg_button.hide()
    
    def login_successful(self, name):
        self.timer.stop()
        self.ui.stackedWidget.setCurrentIndex(LOGIN_SUCCESS_PAGE_IDX)
        self.ui.topStackedWidget.setCurrentIndex(2)
        self.ui.welcome_user.setText(f"Hello, {name}")

    def ok_button_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(LOGIN_PAGE_IDX)
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
