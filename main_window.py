import os

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

class NoteApp(QDialog):
    def __init__(self, name):
        super(NoteApp, self).__init__()
        self.ui = uic.loadUi("noteApps.ui", self)
        self.ui.user_msg.setText(f"Hello, {name}!")
        self.show()
