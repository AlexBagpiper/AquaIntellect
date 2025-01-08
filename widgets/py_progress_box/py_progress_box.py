# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.functions import Functions

# IMPORT STYLES
# ///////////////////////////////////////////////////////////////
from . styles import Styles

# PY PUSH BUTTON
# ///////////////////////////////////////////////////////////////
class PyProgressBox(QWidget):
    def __init__(
        self,
        parent = None,
        obj_name = None,
        mode = None,
        modal = True,
        delete_on_close = False,
        gif = 'loader_default.gif',
        width = 30,
        height = 30
    ):
        QWidget.__init__(self)

        self.setParent(parent)
        self.parent = parent
        if obj_name:
            self.setObjectName(obj_name)
        if delete_on_close:
            self.setAttribute(Qt.WA_DeleteOnClose)

        self.mode = mode
        self.gif = gif

        self.main_layout = QHBoxLayout()
        self.movie = QMovie(Functions.set_gif_icon(self.gif))
        self.label_loading = QLabel()
        self.label_loading.setMovie(self.movie)
        self.label_loading.setAlignment(Qt.AlignCenter)

        self.label_loading.setAttribute(Qt.WA_OpaquePaintEvent)
        self.main_layout.addWidget(self.label_loading)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setLayout(self.main_layout)
        self.resize(width, height)

    def start_animation(self):
        self.movie.start()

    def stop_animation(self):
        self.movie.stop()

    def showEvent(self, event):
        event.accept()
        self.start_animation()

    def hideEvent(self, event):
        self.stop_animation()
        event.accept()

    def closeEvent(self, event):
        self.stop_animation()
        event.accept()

    def __del__(self):
        pass

