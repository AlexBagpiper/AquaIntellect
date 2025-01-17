# -*- coding: utf-8 -*-

from import_core import *

from core.functions import Functions

from core.json_settings import Settings

from core.json_themes import Themes

from widgets import *

from . functions_preview_roi import *


STYLE_FIELD_LABEL = '''
    QLabel {
        font-family: 'Segoe UI';
        font-style: normal;
        font-weight: 500;
        font-size: 12px;
        line-height: 16px;
        color: #8a95aa;
    }
    '''

STYLE_VALUE_LABEL = '''
    QLabel {
        background-color: #1e2229;
        color: #8a95aa;
        border-radius: 8px;
        font-family: 'Segoe UI';
        font-style: normal;
        font-weight: 700;
        font-size: 12px;
        line-height: 16px;
    }
    '''

class UI_PreviewRoi(QWidget):
    clicked = Signal(object)

    def __init__(self, parent = None, camera=None, calib_en=None):
        QWidget.__init__(self)

        self.setObjectName(u"PreviewRoiWindow")
        self.parent = parent
        self.setParent(parent)
        self.setWindowModality(Qt.WindowModal)

        self.current_camera = camera
        self.calib_en = calib_en

        settings = Settings()
        self.settings = settings.items

        themes = Themes()
        self.themes = themes.items

        self.resize(self.settings["preview_roi_camera_size"][0], self.settings["preview_roi_camera_size"][1])
        #self.setMinimumSize(self.settings["preview_roi_camera_size"][0], self.settings["preview_roi_camera_size"][1])

        self.setup_gui()

        self.center()


    def center(self):
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(self.parent.frameGeometry().center())
        self.move(frame_geometry.topLeft())


    def setup_gui(self):
        self.setWindowFlag(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

        self.frm = QFrame(self)
        self.verticalLayout.addWidget(self.frm)
        self.frame_layout = QVBoxLayout(self.frm)

        self.frame_background = QFrame(self)
        self.frame_background.setStyleSheet(u"QFrame{"
                                     u"background: #343b48;"
                                     u"border-radius: 8px;}")
        self.frame_background_layout = QVBoxLayout(self.frame_background)
        self.frame_background_layout.setContentsMargins(5, 5, 5, 5)
        self.frame_background_layout.setStretch(1,2)
        self.frame_layout.addWidget(self.frame_background)

        self.frame_title = QFrame(self)
        self.frame_title.setMaximumHeight(40)
        self.frame_title.setStyleSheet(u"QFrame{"
                                     u"background: #1e2229;"
                                     u"border-radius: 8px;}")
        self.frame_background_layout.addWidget(self.frame_title)
        self.frame_title_layout = QVBoxLayout(self.frame_title)
        self.frame_title_layout.setContentsMargins(5, 5, 5, 5)

        self.l_title = QLabel(self.frame_background)
        self.l_title.setObjectName(u"l_title")
        self.l_title.setStyleSheet(u"QLabel{"
                                   u"color: #8a95aa;"
                                   u"border-radius: 8px;"
                                   u"font-family: 'Segoe UI';"
                                   u"font-style: normal;"
                                   u"font-weight: 400;"
                                   u"font-size: 14px;"
                                   u"line-height: 16px;}")
        self.l_title.setAlignment(Qt.AlignCenter)
        self.l_title.setWordWrap(True)
        self.l_title.setText(QCoreApplication.translate("CompileVolBiomassWindow", u"Предварительный просмотр камеры", None))
        self.frame_title_layout.addWidget(self.l_title)

        self.frame_bottom = QFrame(self)
        self.frame_bottom_layout = QVBoxLayout(self.frame_bottom)
        self.frame_background_layout.addWidget(self.frame_bottom)
        self.frame_bottom_layout.setContentsMargins(0,0,0,0)

        self.preview_layout = QVBoxLayout()
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(0)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(self.shadow)

        self.preview_frame = QFrame(self)
        self.preview_frame_layout = QVBoxLayout(self.preview_frame)
        self.preview_frame_layout.setContentsMargins(5,5,5,5)

        # ADD VIEWFINDER
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()

        self.l_preview = QLabel()
        self.l_preview.setObjectName('preview')
        self.l_preview.setAlignment(Qt.AlignCenter)
        self.l_preview.setStyleSheet(u"QLabel{"
                                     u"background: transparent;}")
        self.l_preview.setGeometry(0, 0, self.width() / 1.1, self.width() / 1.1)


        self.wait_progress_camera = PyProgressBox()
        self.wait_progress_camera.hide()

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.view.setScene(self.scene)
        self.preview_frame_layout.addWidget(self.view, 0, Qt.AlignCenter)

        self.proxy_wid_preview = QGraphicsProxyWidget()
        self.proxy_wid_preview.setWidget(self.l_preview)
        self.scene.addItem(self.proxy_wid_preview)

        self.proxy_wid_wait_progress = QGraphicsProxyWidget()
        self.proxy_wid_wait_progress.setWidget(self.wait_progress_camera)
        self.proxy_wid_wait_progress.setPos(QPoint((self.scene.sceneRect().width() - self.wait_progress_camera.width())/2 - 15,
                                                   (self.scene.sceneRect().height() - self.wait_progress_camera.height())/2 - 5))
        self.scene.addItem(self.proxy_wid_wait_progress)

        self.preview_layout.addWidget(self.preview_frame, alignment=Qt.AlignCenter)

        # BTN EXIT
        self.pbtn_exit = PyPushButton(
            btn_id = 'pbtn_exit',
            text = "Выход",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_exit.setMinimumHeight(30)
        self.pbtn_exit.setMaximumHeight(30)
        self.pbtn_exit.clicked.connect(self.btn_clicked)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setSpacing(10)
        self.btn_layout.addWidget(self.pbtn_exit)

        self.frame_bottom_layout.addLayout(self.preview_layout)
        self.frame_bottom_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.frame_bottom_layout.addLayout(self.btn_layout)

        PreviewRoiFunctions.setup_video_input(self)
        self.camera_connect_thread.cam_connect()

    def paintEvent(self, event):
        if self.parent.frameGeometry().center() != self.frameGeometry().center(): self.center()

    def closeEvent(self, event):
        PreviewRoiFunctions.stop_video_processing_threads(self)
        super().closeEvent(event)

    def btn_clicked(self):
        if self.sender().objectName() == 'pbtn_exit':
            self.clicked.emit(self.sender())
            self.close()