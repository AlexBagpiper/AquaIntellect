# -*- coding: utf-8 -*-

from import_core import *

from core.functions import Functions

from core.json_settings import Settings

from core.json_themes import Themes

from widgets import *

from . functions_add_pool import *
from . ui_camera_calibrate import *
from . ui_preview_roi import *

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

class UI_AddPool(QWidget):
    clicked = Signal(object)

    def __init__(self, parent = None, mode = 'add', camera = None):
        QWidget.__init__(self)

        self.setObjectName(u"AddPoolWindow")
        self.parent = parent
        self.mode = mode
        self.setParent(parent)
        self.setWindowModality(Qt.WindowModal)

        self.current_camera = camera
        self.calib_params = ''

        settings = Settings()
        self.settings = settings.items

        themes = Themes()
        self.themes = themes.items

        self.resize(self.settings["add_pool_size"][0], self.settings["add_pool_size"][1])
        self.setMinimumSize(self.settings["add_pool_size"][0], self.settings["add_pool_size"][1])

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
        self.l_title.setText(QCoreApplication.translate("AddPoolWindow", u"Добавить бассейн", None))
        self.frame_title_layout.addWidget(self.l_title)

        self.frame_bottom = QFrame(self)
        self.frame_bottom_layout = QVBoxLayout(self.frame_bottom)
        self.frame_background_layout.addWidget(self.frame_bottom)
        self.frame_bottom_layout.setContentsMargins(0,0,0,0)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(self.shadow)

        self.l_name = QLabel()
        self.l_name.setText(QCoreApplication.translate("Label", u"Название", None))
        self.l_name.setAlignment(Qt.AlignBottom)
        self.l_name.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_comments = QLabel()
        self.l_comments.setText(QCoreApplication.translate("Label", u"Комментарии", None))
        self.l_comments.setMinimumHeight(20)
        self.l_comments.setAlignment(Qt.AlignBottom)
        self.l_comments.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_koef_v = QLabel()
        self.l_koef_v.setText(QCoreApplication.translate("Label", u"Обьемный коэффициент преобразования", None))
        self.l_koef_v.setMinimumHeight(20)
        self.l_koef_v.setAlignment(Qt.AlignBottom)
        self.l_koef_v.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_name_video_source = QLabel()
        self.l_name_video_source.setText(QCoreApplication.translate("Label", u"Источник видеопотока", None))
        self.l_name_video_source.setMinimumHeight(20)
        self.l_name_video_source.setAlignment(Qt.AlignBottom)
        self.l_name_video_source.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_video_source = QLabel()
        self.l_video_source.setText(QCoreApplication.translate("Label", u"Адрес источника видеопотока", None))
        self.l_video_source.setMinimumHeight(20)
        self.l_video_source.setAlignment(Qt.AlignBottom)
        self.l_video_source.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_roi = QLabel()
        self.l_roi.setText(QCoreApplication.translate("Label", u"ROI камеры", None))
        self.l_roi.setMinimumHeight(20)
        self.l_roi.setAlignment(Qt.AlignBottom)
        self.l_roi.setStyleSheet(STYLE_FIELD_LABEL)

        #ADD NAME FIELD
        self.ledit_name = PyLineEdit(
            text = "",
            place_holder_text = "Введите название бассейна",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.ledit_name.setMinimumHeight(30)


        #ADD COMMENTS FIELD
        self.ledit_comments = PyPlainTextEdit(
            text = "",
            place_holder_text = "Введите дополнительную информацию при необходимости",
            border_size = 1,
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.ledit_comments.setMinimumHeight(30)

        #ADD KOEF FIELD
        self.ledit_koef_v = PyLineEdit(
            text = "",
            place_holder_text = "Введите обьемный коэффициент преобразования для бассейна",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([.0-9]+)"
        )
        self.ledit_koef_v.setMinimumHeight(30)

        #ADD VIDEO SOURCE NAME FIELD
        self.ledit_name_video_source = PyLineEdit(
            text = "",
            place_holder_text = "Введите названия источника видеопотока",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.ledit_name_video_source.setMinimumHeight(30)

        #ADD VIDEO SOURCE FIELD
        self.ledit_video_source = PyLineEdit(
            text = "",
            place_holder_text = "Введите адрес источника видеопотока",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.ledit_video_source.setMinimumHeight(30)

        self.l_calib = QLabel()
        self.l_calib.setText(QCoreApplication.translate("Label", u"Калибровка камеры", None))
        self.l_calib.setMinimumHeight(20)
        self.l_calib.setAlignment(Qt.AlignBottom)
        self.l_calib.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_calib_en = QLabel()
        self.l_calib_en.setText(QCoreApplication.translate("Label", u"Активировать калибровку камеры", None))
        self.l_calib_en.setMinimumHeight(20)
        self.l_calib_en.setAlignment(Qt.AlignCenter)
        self.l_calib_en.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_calib_status = QLabel()
        self.l_calib_status.setMinimumHeight(20)
        self.l_calib_status.setAlignment(Qt.AlignCenter)

        # BTN PREVIEW
        self.pbtn_calib = PyPushButton(
            btn_id = 'pbtn_calib',
            text = "Калибровка",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_calib.setMinimumHeight(30)
        self.pbtn_calib.setMaximumHeight(30)
        self.pbtn_calib.setMinimumWidth(100)
        self.pbtn_calib.clicked.connect(self.btn_clicked)

        # TOGGLE CALIB ENABLE BUTTON
        self.tbtn_calib_en = PyToggle(
            width = 50,
            bg_color = self.themes["app_color"]["dark_two"],
            circle_color = self.themes["app_color"]["icon_color"],
            active_color = self.themes["app_color"]["context_color"]
        )
        self.tbtn_calib_en.stateChanged.connect(self.btn_clicked)

        self.calib_layout = QHBoxLayout(self.frame_bottom)
        self.calib_layout.setContentsMargins(0, 0, 0, 0)
        self.calib_layout.setSpacing(10)
        self.calib_layout.addWidget(self.pbtn_calib)
        self.calib_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.calib_layout.addWidget(self.l_calib_status)
        self.calib_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.calib_layout.addWidget(self.l_calib_en)
        self.calib_layout.addWidget(self.tbtn_calib_en)


        #ADD ROI X
        self.ledit_roi_x = PyLineEdit(
            text = "",
            place_holder_text = "начальный X",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([0-9]+)"
        )
        self.ledit_roi_x.setMinimumHeight(30)

        #ADD ROI Y
        self.ledit_roi_y = PyLineEdit(
            text = "",
            place_holder_text = "начальный Y",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([0-9]+)"
        )
        self.ledit_roi_y.setMinimumHeight(30)

        #ADD ROI W
        self.ledit_roi_w = PyLineEdit(
            text = "",
            place_holder_text = "ширина W",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([0-9]+)"
        )
        self.ledit_roi_w.setMinimumHeight(30)

        #ADD ROI H
        self.ledit_roi_h = PyLineEdit(
            text = "",
            place_holder_text = "высота H",
            radius = 8,
            border_size = 1,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"],
            reg_line = "([0-9]+)"
        )
        self.ledit_roi_h.setMinimumHeight(30)

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
        self.pbtn_preview.setMinimumWidth(120)
        self.pbtn_preview.clicked.connect(self.btn_clicked)

        if self.mode == 'add':
            # BTN ADD
            self.pbtn_add = PyPushButton(
                btn_id = 'pbtn_add_pool',
                text = "Добавить",
                radius  = 8,
                color = self.themes["app_color"]["text_foreground"],
                bg_color = self.themes["app_color"]["dark_one"],
                bg_color_hover = self.themes["app_color"]["dark_three"],
                bg_color_pressed = self.themes["app_color"]["dark_four"]
            )
            self.pbtn_add.setMinimumHeight(30)
            self.pbtn_add.setMaximumHeight(30)
            self.pbtn_add.clicked.connect(self.btn_clicked)

        if self.mode == 'edit':
            # BTN EDIT
            self.pbtn_edit = PyPushButton(
                btn_id = 'pbtn_edit_pool',
                text = "Сохранить",
                radius  = 8,
                color = self.themes["app_color"]["text_foreground"],
                bg_color = self.themes["app_color"]["dark_one"],
                bg_color_hover = self.themes["app_color"]["dark_three"],
                bg_color_pressed = self.themes["app_color"]["dark_four"]
            )
            self.pbtn_edit.setMinimumHeight(30)
            self.pbtn_edit.setMaximumHeight(30)
            self.pbtn_edit.clicked.connect(self.btn_clicked)

        self.roi_layout = QHBoxLayout(self.frame_bottom)
        self.roi_layout.setContentsMargins(0, 0, 0, 0)
        self.roi_layout.setSpacing(10)
        self.roi_layout.addWidget(self.ledit_roi_x)
        self.roi_layout.addWidget(self.ledit_roi_y)
        self.roi_layout.addWidget(self.ledit_roi_w)
        self.roi_layout.addWidget(self.ledit_roi_h)
        self.roi_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.roi_layout.addWidget(self.pbtn_preview)

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
        if self.mode == 'add':
            self.btn_layout.addWidget(self.pbtn_add)
        elif self.mode == 'edit':
            self.btn_layout.addWidget(self.pbtn_edit)
        self.btn_layout.addWidget(self.pbtn_exit)

        self.frame_bottom_layout.addWidget(self.l_name)
        self.frame_bottom_layout.addWidget(self.ledit_name)
        self.frame_bottom_layout.addWidget(self.l_comments)
        self.frame_bottom_layout.addWidget(self.ledit_comments)
        self.frame_bottom_layout.addWidget(self.l_koef_v)
        self.frame_bottom_layout.addWidget(self.ledit_koef_v)
        self.frame_bottom_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.frame_bottom_layout.addWidget(self.l_name_video_source)
        self.frame_bottom_layout.addWidget(self.ledit_name_video_source)
        self.frame_bottom_layout.addWidget(self.l_video_source)
        self.frame_bottom_layout.addWidget(self.ledit_video_source)
        self.frame_bottom_layout.addWidget(self.l_calib)
        self.frame_bottom_layout.addLayout(self.calib_layout)
        self.frame_bottom_layout.addWidget(self.l_roi)
        self.frame_bottom_layout.addLayout(self.roi_layout)
        self.frame_bottom_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.frame_bottom_layout.addLayout(self.btn_layout)

        if self.mode == 'edit':
            AddPoolFunctions.fill_edit_data(self)

        AddPoolFunctions.update_calib_status(self)


    def paintEvent(self, event):
        if self.parent.frameGeometry().center() != self.frameGeometry().center(): self.center()


    def closeEvent(self, event):
        super().closeEvent(event)


    def btn_clicked(self):
        def save_signal(params):
            AddPoolFunctions.update_calib_params(self, params)

        if self.sender().objectName() == 'pbtn_exit':
                self.close()
        if self.sender().objectName() == 'pbtn_add_pool':
            if AddPoolFunctions.add_pool(self):
                self.clicked.emit(self.sender())
                self.close()
        if self.sender().objectName() == 'pbtn_edit_pool':
            if AddPoolFunctions.edit_pool(self):
                self.clicked.emit(self.sender())
                self.close()
        if self.sender().objectName() == 'pbtn_calib':
            while(self.parent.camera_thread.isStreamming):
                self.parent.preview_stopped = True
                self.parent.camera_thread.stop_stream()
            self.parent.camera_connect_thread.cam_disconnect()
            self.parent.l_preview.clear()
            if self.mode == 'add':
                self.camera_calibrate_ui = UI_CameraCalibrate(self, {'camera_address': self.ledit_video_source.text(), 'camera_roi': ''})
            elif self.mode == 'edit':
                self.camera_calibrate_ui = UI_CameraCalibrate(self, self.current_camera)
            self.camera_calibrate_ui.clicked.connect(self.btn_clicked)
            self.camera_calibrate_ui.save.connect(save_signal)
            self.camera_calibrate_ui.show()
        if self.sender().objectName() == 'pbtn_preview':
            camera_roi = ''
            if self.ledit_roi_x.text() and self.ledit_roi_y.text() and self.ledit_roi_w.text() and self.ledit_roi_h.text():
                camera_roi = json.dumps({"x": int(self.ledit_roi_x.text()),
                                         "y": int(self.ledit_roi_y.text()),
                                         "w": int(self.ledit_roi_w.text()),
                                         "h": int(self.ledit_roi_h.text())})
            self.preview_roi_ui = UI_PreviewRoi(self, {'camera_address': self.ledit_video_source.text(), 'calib_params': self.calib_params, 'camera_roi': camera_roi}, self.tbtn_calib_en.isChecked())
            self.preview_roi_ui.clicked.connect(self.btn_clicked)
            self.preview_roi_ui.show()



