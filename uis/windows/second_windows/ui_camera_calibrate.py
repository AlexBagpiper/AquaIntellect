# -*- coding: utf-8 -*-

from import_core import *

from core.functions import Functions

from core.json_settings import Settings

from core.json_themes import Themes

from widgets import *

from . functions_camera_calibrate import *

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


class UI_CameraCalibrate(QWidget):
    clicked = Signal(object)
    save = Signal(dict)

    def __init__(self, parent = None, current_camera=None):
        QWidget.__init__(self)

        self.setObjectName(u"CameraCalibrateWindow")
        self.parent = parent
        self.setParent(parent)
        self.setWindowModality(Qt.WindowModal)

        self.current_camera = current_camera

        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.CHECKERBOARD = (3, 3)
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0] * self.CHECKERBOARD[1], 3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0], 0:self.CHECKERBOARD[1]].T.reshape(-1, 2)
        self.threedpoints = []
        self.twodpoints = []
        self.corners = None

        settings = Settings()
        self.settings = settings.items

        themes = Themes()
        self.themes = themes.items

        self.resize(self.settings["calibrate_camera_size"][0], self.settings["calibrate_camera_size"][1])
        self.setMinimumSize(self.settings["calibrate_camera_size"][0], self.settings["calibrate_camera_size"][1])

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

        self.frame = QFrame(self)
        self.verticalLayout.addWidget(self.frame)
        self.frame_layout = QVBoxLayout(self.frame)

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
        self.l_title.setText(QCoreApplication.translate("CompileVolBiomassWindow", u"Калибровка камеры", None))
        self.frame_title_layout.addWidget(self.l_title)

        self.frame_bottom = QFrame(self)
        self.frame_bottom_layout = QVBoxLayout(self.frame_bottom)
        self.frame_background_layout.addWidget(self.frame_bottom)
        self.frame_bottom_layout.setContentsMargins(0,0,0,0)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)

        self.status_layout = QVBoxLayout()
        self.status_layout.setContentsMargins(10, 0, 0, 0)
        self.status_layout.setSpacing(20)
        self.content_layout.addLayout(self.status_layout)

        self.preview_layout = QVBoxLayout()
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(0)
        self.content_layout.addLayout(self.preview_layout)

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
        self.l_preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.l_preview.setStyleSheet(u"QLabel{"
                                     u"background: transparent;}")
        self.l_preview.setGeometry(0, 0, self.width() / 2, self.width() / 3)
        #self.l_preview.hide()

        self.wait_progress_camera = PyProgressBox()
        self.wait_progress_camera.hide()

        self.l_ungrabbed = QLabel()
        self.l_ungrabbed.setObjectName(u"l_ungrabbed")
        self.l_ungrabbed.setAlignment(Qt.AlignCenter)
        self.l_ungrabbed.setGeometry(0, 0, 200, 40)
        self.l_ungrabbed.setStyleSheet(u"QLabel{"
                                         u"background: transparent;"
                                         u"color: red;"
                                         u"font-family: 'Roboto';"
                                         u"font-size: 14px;"
                                         u"font-style: normal;"
                                         u"font-weight: 400;}")
        self.l_ungrabbed.setText('захват не выполнен\nповторите попытку')
        self.l_ungrabbed.hide()

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setScene(self.scene)
        self.scene.installEventFilter(self)
        self.preview_frame_layout.addWidget(self.view, 0, Qt.AlignHCenter)

        self.proxy_wid_preview = QGraphicsProxyWidget()
        self.proxy_wid_preview.setWidget(self.l_preview)
        self.scene.addItem(self.proxy_wid_preview)

        self.proxy_wid_wait_progress = QGraphicsProxyWidget()
        self.proxy_wid_wait_progress.setWidget(self.wait_progress_camera)
        self.proxy_wid_wait_progress.setPos(QPoint((self.scene.sceneRect().width() - self.wait_progress_camera.width())/2 - 15,
                                                   (self.scene.sceneRect().height() - self.wait_progress_camera.height())/2 - 5))
        self.scene.addItem(self.proxy_wid_wait_progress)

        self.proxy_wid_l_ungrabbed = QGraphicsProxyWidget()
        self.proxy_wid_l_ungrabbed.setWidget(self.l_ungrabbed)
        self.proxy_wid_l_ungrabbed.setPos(QPoint(self.scene.sceneRect().width() / 2 - 100, self.scene.sceneRect().height() / 2 - 20))
        self.scene.addItem(self.proxy_wid_l_ungrabbed)

        self.preview_layout.addWidget(self.preview_frame, alignment=Qt.AlignHCenter | Qt.AlignTop)

        self.l_chess_size = QLabel()
        self.l_chess_size.setText(QCoreApplication.translate("Label", u"Размер калибровочной доски", None))
        self.l_chess_size.setMinimumHeight(20)
        self.l_chess_size.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.l_chess_size.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_x = QLabel()
        self.l_x.setText(QCoreApplication.translate("Label", u"x", None))
        self.l_x.setMinimumHeight(20)
        self.l_x.setAlignment(Qt.AlignCenter)
        self.l_x.setStyleSheet(STYLE_FIELD_LABEL)

        self.ledit_side_0 = PyLineEdit(
            text = "",
            place_holder_text = "",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([0-9]+)"
        )
        self.ledit_side_0.setMinimumHeight(30)
        self.ledit_side_0.setMaximumWidth(50)
        self.ledit_side_0.setAlignment(Qt.AlignCenter)

        self.ledit_side_1 = PyLineEdit(
            text = "",
            place_holder_text = "",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([0-9]+)"
        )
        self.ledit_side_1.setMinimumHeight(30)
        self.ledit_side_1.setMaximumWidth(50)
        self.ledit_side_1.setAlignment(Qt.AlignCenter)

        self.chess_size_layout = QHBoxLayout()
        self.chess_size_layout.setSpacing(10)
        self.chess_size_layout.addWidget(self.l_chess_size)
        self.chess_size_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.chess_size_layout.addWidget(self.ledit_side_0)
        self.chess_size_layout.addWidget(self.l_x)
        self.chess_size_layout.addWidget(self.ledit_side_1)

        # BTN GRAB
        self.pbtn_grab = PyPushButton(
            btn_id = 'pbtn_grab',
            text = "Захват кадра",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_grab.setMinimumHeight(30)
        self.pbtn_grab.setMaximumHeight(30)
        self.pbtn_grab.setMinimumWidth(140)
        self.pbtn_grab.setMaximumHeight(140)
        self.pbtn_grab.clicked.connect(self.btn_clicked)

        # BTN ACCEPT
        self.pbtn_accept = PyPushButton(
            btn_id = 'pbtn_accept',
            text = "Принять",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_accept.setMinimumHeight(25)
        self.pbtn_accept.setMaximumHeight(15)
        self.pbtn_accept.setMinimumWidth(80)
        self.pbtn_accept.setMaximumHeight(80)
        self.pbtn_accept.clicked.connect(self.btn_clicked)
        self.pbtn_accept.hide()

        # BTN REJECT
        self.pbtn_reject = PyPushButton(
            btn_id = 'pbtn_reject',
            text = "Отклонить",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_reject.setMinimumHeight(25)
        self.pbtn_reject.setMaximumHeight(25)
        self.pbtn_reject.setMinimumWidth(80)
        self.pbtn_reject.setMaximumHeight(80)
        self.pbtn_reject.clicked.connect(self.btn_clicked)
        self.pbtn_reject.hide()

        self.grab_layout = QHBoxLayout()
        self.grab_layout.setSpacing(10)
        self.grab_layout.addWidget(self.pbtn_grab)
        self.grab_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.grab_layout.addWidget(self.pbtn_accept)
        self.grab_layout.addWidget(self.pbtn_reject)


        self.l_grab = QLabel()
        self.l_grab.setText(QCoreApplication.translate("Label", u"Захвачено кадров", None))
        self.l_grab.setMinimumHeight(20)
        self.l_grab.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.l_grab.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_grab_frames = QLabel()
        self.l_grab_frames.setMinimumHeight(20)
        self.l_grab_frames.setAlignment(Qt.AlignCenter)
        self.l_grab_frames.setMinimumWidth(100)
        self.l_grab_frames.setStyleSheet(STYLE_VALUE_LABEL)

        self.grab_frames_layout = QHBoxLayout()
        self.grab_frames_layout.addWidget(self.l_grab)
        self.grab_frames_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.grab_frames_layout.addWidget(self.l_grab_frames)

        self.l_fish_qty = QLabel()
        self.l_fish_qty.setText(QCoreApplication.translate("Label", u"Количество особей", None))
        self.l_fish_qty.setMinimumHeight(20)
        self.l_fish_qty.setAlignment(Qt.AlignVCenter)
        self.l_fish_qty.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_val_fish_qty = QLabel()
        self.l_val_fish_qty.setMinimumHeight(20)
        self.l_val_fish_qty.setMinimumWidth(100)
        self.l_val_fish_qty.setAlignment(Qt.AlignCenter)
        self.l_val_fish_qty.setStyleSheet(STYLE_VALUE_LABEL)

        # BTN COMPILE
        self.pbtn_compile = PyPushButton(
            btn_id = 'pbtn_compile',
            text = "Расчет",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_compile.setMinimumHeight(30)
        self.pbtn_compile.setMaximumHeight(30)
        self.pbtn_compile.clicked.connect(self.btn_clicked)
        self.pbtn_compile.hide()

        # BTN PREVIEW
        self.pbtn_preview = PyPushButton(
            btn_id = 'pbtn_preview',
            text = "Просмотр",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_preview.setMinimumHeight(30)
        self.pbtn_preview.setMaximumHeight(30)
        self.pbtn_preview.clicked.connect(self.btn_clicked)
        self.pbtn_preview.hide()

        # BTN SAVE
        self.pbtn_save = PyPushButton(
            btn_id = 'pbtn_save',
            text = "Сохранить",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_save.setMinimumHeight(30)
        self.pbtn_save.setMaximumHeight(30)
        self.pbtn_save.clicked.connect(self.btn_clicked)
        self.pbtn_save.hide()

        # BTN RESET
        self.pbtn_reset = PyPushButton(
            btn_id = 'pbtn_reset',
            text = "Сброс",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_reset.setMinimumHeight(30)
        self.pbtn_reset.setMaximumHeight(30)
        self.pbtn_reset.clicked.connect(self.btn_clicked)

        # BTN EXIT
        self.pbtn_exit_camera_calibrate = PyPushButton(
            btn_id = 'pbtn_exit_camera_calibrate',
            text = "Выход",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_exit_camera_calibrate.setMinimumHeight(30)
        self.pbtn_exit_camera_calibrate.setMaximumHeight(30)
        self.pbtn_exit_camera_calibrate.clicked.connect(self.btn_clicked)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setSpacing(10)
        self.btn_layout.addWidget(self.pbtn_preview)
        self.btn_layout.addWidget(self.pbtn_save)
        self.btn_layout.addWidget(self.pbtn_compile)
        self.btn_layout.addWidget(self.pbtn_reset)
        self.btn_layout.addWidget(self.pbtn_exit_camera_calibrate)

        self.frame_bottom_layout.addLayout(self.content_layout)
        self.frame_bottom_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.frame_bottom_layout.addLayout(self.btn_layout)

        self.status_layout.addItem(QSpacerItem(0, 30, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.status_layout.addLayout(self.chess_size_layout)
        self.status_layout.addLayout(self.grab_layout)
        self.status_layout.addLayout(self.grab_frames_layout)
        self.status_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))

        CameraCalibrateFunctions.setup_video_input(self)
        self.camera_connect_thread.current_camera = self.current_camera
        self.camera_connect_thread.cam_connect()

    def paintEvent(self, event):
        if self.parent.frameGeometry().center() != self.frameGeometry().center(): self.center()

    def closeEvent(self, event):
        CameraCalibrateFunctions.stop_video_processing_threads(self)
        super().closeEvent(event)

    def btn_clicked(self):
        if self.sender().objectName() == 'pbtn_exit_camera_calibrate':
            self.clicked.emit(self.sender())
            self.close()
        if self.sender().objectName() == 'pbtn_grab':
            CameraCalibrateFunctions.grab_frame(self)
        if self.sender().objectName() == 'pbtn_reject':
            CameraCalibrateFunctions.reject_grab(self)
        if self.sender().objectName() == 'pbtn_accept':
            CameraCalibrateFunctions.accept_grab(self)
        if self.sender().objectName() == 'pbtn_compile':
            CameraCalibrateFunctions.compile_param(self)
        if self.sender().objectName() == 'pbtn_reset':
            CameraCalibrateFunctions.reset(self)
        if self.sender().objectName() == 'pbtn_preview':
            CameraCalibrateFunctions.preview(self)
        if self.sender().objectName() == 'pbtn_save':
            CameraCalibrateFunctions.save(self)