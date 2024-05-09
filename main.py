import sys
from PyQt6.QtWidgets import QApplication
from login_window import WebcamViewer
from main_window import NoteApp 

def launch_main(parent, app, name):
    main_window = NoteApp(name)
    parent.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = WebcamViewer()
    login_window.login_signal.connect(lambda name: launch_main(login_window, app, name))
    login_window.show()
    sys.exit(app.exec())