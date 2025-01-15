# -*- coding: utf-8 -*-

from import_core import *

from core.functions import Functions

from core.json_settings import Settings

from core.json_themes import Themes

from widgets import *


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


class UI_PreviewCalibrate(QWidget):
    clicked = Signal(object)

    def __init__(self, parent = None,frame=None, params=None):
        QWidget.__init__(self)

        self.setObjectName(u"PreviewCalibrateWindow")
        self.parent = parent
        self.setParent(parent)
        self.setWindowModality(Qt.WindowModal)

        self.frame = frame
        self.params = params

        settings = Settings()
        self.settings = settings.items

        themes = Themes()
        self.themes = themes.items

        self.resize(self.settings["preview_calibrate_camera_size"][0], self.settings["preview_calibrate_camera_size"][1])
        self.setMinimumSize(self.settings["preview_calibrate_camera_size"][0], self.settings["preview_calibrate_camera_size"][1])

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
        self.l_title.setText(QCoreApplication.translate("CompileVolBiomassWindow", u"Результат калибровки камеры", None))
        self.frame_title_layout.addWidget(self.l_title)

        self.frame_bottom = QFrame(self)
        self.frame_bottom_layout = QVBoxLayout(self.frame_bottom)
        self.frame_background_layout.addWidget(self.frame_bottom)
        self.frame_bottom_layout.setContentsMargins(0,0,0,0)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)

        self.preview_layout = QHBoxLayout()
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(0)
        self.content_layout.addLayout(self.preview_layout)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(self.shadow)

        self.old_preview_frame = QFrame(self)
        self.old_preview_frame_layout = QVBoxLayout(self.old_preview_frame)
        self.old_preview_frame_layout.setContentsMargins(5,5,5,5)

        # ADD VIEWFINDER
        self.old_view = QGraphicsView()
        self.old_scene = QGraphicsScene()

        self.l_old_preview = QLabel()
        self.l_old_preview.setObjectName('preview')
        self.l_old_preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.l_old_preview.setStyleSheet(u"QLabel{"
                                     u"background: transparent;}")
        self.l_old_preview.setGeometry(0, 0, self.width() / 2, self.width() / 3)


        self.l_old = QLabel()
        self.l_old.setObjectName(u"l_ungrabbed")
        self.l_old.setAlignment(Qt.AlignCenter)
        self.l_old.setGeometry(0, 0, 200, 40)
        self.l_old.setStyleSheet(u"QLabel{"
                                         u"background: transparent;"
                                         u"color: #B1E856;"
                                         u"font-family: 'Roboto';"
                                         u"font-size: 14px;"
                                         u"font-style: normal;"
                                         u"font-weight: 400;}")
        self.l_old.setText('до калибровки')

        self.old_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.old_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.old_view.setScene(self.old_scene)
        self.old_scene.installEventFilter(self)
        self.old_preview_frame_layout.addWidget(self.old_view, 0, Qt.AlignHCenter)

        self.proxy_wid_old_preview = QGraphicsProxyWidget()
        self.proxy_wid_old_preview.setWidget(self.l_old_preview)
        self.old_scene.addItem(self.proxy_wid_old_preview)

        self.proxy_wid_l_old = QGraphicsProxyWidget()
        self.proxy_wid_l_old.setWidget(self.l_old)
        self.proxy_wid_l_old.setPos(QPoint(self.old_scene.sceneRect().width() / 2 - 100, self.old_scene.sceneRect().height() / 2 - 20))
        self.old_scene.addItem(self.proxy_wid_l_old)

        self.preview_layout.addWidget(self.old_preview_frame, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        self.new_preview_frame = QFrame(self)
        self.new_preview_frame_layout = QVBoxLayout(self.new_preview_frame)
        self.new_preview_frame_layout.setContentsMargins(5,5,5,5)

        # ADD VIEWFINDER
        self.new_view = QGraphicsView()
        self.new_scene = QGraphicsScene()

        self.l_new_preview = QLabel()
        self.l_new_preview.setObjectName('preview')
        self.l_new_preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.l_new_preview.setStyleSheet(u"QLabel{"
                                     u"background: transparent;}")
        self.l_new_preview.setGeometry(0, 0, self.width() / 2, self.width() / 3)


        self.l_new = QLabel()
        self.l_new.setObjectName(u"l_ungrabbed")
        self.l_new.setAlignment(Qt.AlignCenter)
        self.l_new.setGeometry(0, 0, 200, 40)
        self.l_new.setStyleSheet(u"QLabel{"
                                         u"background: transparent;"
                                         u"color: #B1E856;"
                                         u"font-family: 'Roboto';"
                                         u"font-size: 14px;"
                                         u"font-style: normal;"
                                         u"font-weight: 400;}")
        self.l_new.setText('после калибровки')

        self.new_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.new_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.new_view.setScene(self.new_scene)
        self.new_scene.installEventFilter(self)
        self.new_preview_frame_layout.addWidget(self.new_view, 0, Qt.AlignHCenter)

        self.proxy_wid_new_preview = QGraphicsProxyWidget()
        self.proxy_wid_new_preview.setWidget(self.l_new_preview)
        self.new_scene.addItem(self.proxy_wid_new_preview)

        self.proxy_wid_l_new = QGraphicsProxyWidget()
        self.proxy_wid_l_new.setWidget(self.l_new)
        self.proxy_wid_l_new.setPos(QPoint(self.new_scene.sceneRect().width() / 2 - 100, self.new_scene.sceneRect().height() / 2 - 20))
        self.new_scene.addItem(self.proxy_wid_l_new)

        self.preview_layout.addWidget(self.new_preview_frame, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # BTN EXIT
        self.pbtn_exit_preview_camera_calibrate = PyPushButton(
            btn_id = 'pbtn_exit_preview_camera_calibrate',
            text = "Выход",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_exit_preview_camera_calibrate.setMinimumHeight(30)
        self.pbtn_exit_preview_camera_calibrate.setMaximumHeight(30)
        self.pbtn_exit_preview_camera_calibrate.clicked.connect(self.btn_clicked)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setSpacing(10)
        self.btn_layout.addWidget(self.pbtn_exit_preview_camera_calibrate)

        self.frame_bottom_layout.addLayout(self.content_layout)
        self.frame_bottom_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.frame_bottom_layout.addLayout(self.btn_layout)
        self.update_preview()

    def update_preview(self):
        h, w, _ = self.frame.shape
        frame_ratio = w / h
        self.l_old_preview.setPixmap(self.convert_cv_to_pixmap(self.frame).scaled(self.old_scene.sceneRect().width(), self.old_scene.sceneRect().width() / frame_ratio, Qt.KeepAspectRatio))
        dst = cv2.undistort(self.frame, np.array(self.params['old_matrix']), np.array(self.params['old_distortion']), None, np.array(self.params['new_matrix']))
        x, y, w, h = self.params['roi']
        dst = dst[y:y+h, x:x+w].copy()
        h, w, _ = dst.shape
        frame_ratio = w / h
        self.l_new_preview.setPixmap(self.convert_cv_to_pixmap(dst).scaled(self.new_scene.sceneRect().width(), self.new_scene.sceneRect().width() / frame_ratio, Qt.KeepAspectRatio))

    def convert_cv_to_pixmap(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame, w, h,bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        return pixmap

    def paintEvent(self, event):
        if self.parent.frameGeometry().center() != self.frameGeometry().center(): self.center()

    def closeEvent(self, event):
        super().closeEvent(event)

    def btn_clicked(self):
        if self.sender().objectName() == 'pbtn_exit_preview_camera_calibrate':
            self.clicked.emit(self.sender())
            self.close()