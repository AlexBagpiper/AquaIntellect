# -*- coding: utf-8 -*-

from import_core import *

from core.functions import Functions

from core.json_settings import Settings

from core.json_themes import Themes

from widgets import *

from . functions_compile_vol_biomass import *

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


class UI_CompileVolBiomass(QWidget):
    clicked = Signal(object)

    def __init__(self, parent = None, current_camera=None, pool_id=None):
        QWidget.__init__(self)

        self.setObjectName(u"CompileVolBiomassWindow")
        self.parent = parent
        self.setParent(parent)
        self.setWindowModality(Qt.WindowModal)

        self.current_camera = current_camera
        self.pool_id = pool_id

        settings = Settings()
        self.settings = settings.items

        themes = Themes()
        self.themes = themes.items

        self.resize(self.settings["compile_vol_biomass_size"][0], self.settings["compile_vol_biomass_size"][1])
        self.setMinimumSize(self.settings["compile_vol_biomass_size"][0], self.settings["compile_vol_biomass_size"][1])

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
        self.l_title.setText(QCoreApplication.translate("CompileVolBiomassWindow", u"Расчет объема биомассы бассейна", None))
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
        self.status_layout.setSpacing(10)
        self.content_layout.addLayout(self.status_layout)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(self.shadow)

        self.preview_frame = QFrame(self)
        #self.preview_frame.setMaximumSize(600, 600)

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
        self.l_preview.setGeometry(0, 0, self.width() / 2.2, self.width() / 2.2)
        #self.l_preview.hide()

        self.wait_progress_camera = PyProgressBox()
        self.wait_progress_camera.hide()

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

        self.content_layout.addWidget(self.preview_frame, alignment=Qt.AlignHCenter | Qt.AlignTop)

        self.circular_progress = PyCircularProgress(
            value = 0,
            progress_width = 2,
            progress_color = self.themes["app_color"]["pink"],
            text_color = self.themes["app_color"]["white"],
            font_size = 14,
            bg_color = self.themes["app_color"]["bg_three"]
        )
        self.circular_progress.setFixedSize(140,140)

        self.l_time_remain = QLabel()
        self.l_time_remain.setText(QCoreApplication.translate("Label", u"Осталось 00:00", None))
        self.l_time_remain.setMinimumHeight(20)
        self.l_time_remain.setAlignment(Qt.AlignCenter)
        self.l_time_remain.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_relative_volume = QLabel()
        self.l_relative_volume.setText(QCoreApplication.translate("Label", u"Удельный обьем биомассы(см³/особь)", None))
        self.l_relative_volume.setMinimumHeight(20)
        self.l_relative_volume.setAlignment(Qt.AlignVCenter)
        self.l_relative_volume.setStyleSheet(STYLE_FIELD_LABEL)

        self.l_val_relative_volume = QLabel()
        self.l_val_relative_volume.setMinimumHeight(20)
        self.l_val_relative_volume.setAlignment(Qt.AlignCenter)
        self.l_val_relative_volume.setMinimumWidth(100)
        self.l_val_relative_volume.setStyleSheet(STYLE_VALUE_LABEL)

        self.relative_volume_layout = QHBoxLayout()
        self.relative_volume_layout.addWidget(self.l_relative_volume)
        self.relative_volume_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.relative_volume_layout.addWidget(self.l_val_relative_volume)

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

        self.fish_qty_layout = QHBoxLayout()
        self.fish_qty_layout.addWidget(self.l_fish_qty)
        self.fish_qty_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.fish_qty_layout.addWidget(self.l_val_fish_qty)

        # BTN START
        self.pbtn_start = PyPushButton(
            btn_id = 'pbtn_start',
            text = "Запуск",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_start.setMinimumHeight(30)
        self.pbtn_start.setMaximumHeight(30)
        self.pbtn_start.clicked.connect(self.btn_clicked)

        # BTN EXIT
        self.pbtn_exit_compile_vol_biomass = PyPushButton(
            btn_id = 'pbtn_exit_compile_vol_biomass',
            text = "Выход",
            radius  = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.pbtn_exit_compile_vol_biomass.setMinimumHeight(30)
        self.pbtn_exit_compile_vol_biomass.setMaximumHeight(30)
        self.pbtn_exit_compile_vol_biomass.clicked.connect(self.btn_clicked)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setSpacing(10)
        self.btn_layout.addWidget(self.pbtn_start)
        self.btn_layout.addWidget(self.pbtn_exit_compile_vol_biomass)

        self.frame_bottom_layout.addLayout(self.content_layout)
        self.frame_bottom_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.frame_bottom_layout.addLayout(self.btn_layout)

        self.status_layout.addItem(QSpacerItem(0, 30, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.status_layout.addWidget(self.circular_progress, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.status_layout.addWidget(self.l_time_remain)
        self.status_layout.addItem(QSpacerItem(0, 30, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.status_layout.addLayout(self.relative_volume_layout)
        self.status_layout.addLayout(self.fish_qty_layout)
        self.status_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))

        CompileVolBiomassFunctions.setup_video_input(self)
        self.camera_connect_thread.cam_connect()
        self.current_pool = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                          table='pools',
                                                          where='pool_id',
                                                          value=self.pool_id)[1][0]


    def paintEvent(self, event):
        if self.parent.frameGeometry().center() != self.frameGeometry().center(): self.center()

    def closeEvent(self, event):
        CompileVolBiomassFunctions.stop_video_processing_threads(self)
        super().closeEvent(event)


    def btn_clicked(self):
        if self.sender().objectName() == 'pbtn_exit_compile_vol_biomass':
            self.clicked.emit(self.sender())
            self.close()
        if self.sender().objectName() == 'pbtn_start':
            CompileVolBiomassFunctions.start_compile(self)
            #self.clicked.emit(self.sender())



