# -*- coding: utf-8 -*-

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from import_core import *

from widgets.py_table_widget.py_table_widget import PyTableWidget
from . functions_main_window import *
from . functions_video import *
from core.json_settings import Settings
from core.json_themes import Themes
from widgets import *

from . ui_main import *

from . functions_main_window import *

# PY WINDOW
# ///////////////////////////////////////////////////////////////
class SetupMainWindow:
    def __init__(self):
        super().__init__()
        # SETUP MAIN WINDOw
        # Load widgets from "uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

    # ADD LEFT MENUS
    # ///////////////////////////////////////////////////////////////
    add_left_menus = [
        {
            "btn_icon" : "icon_monitoring.svg",
            "btn_id" : "btn_monitoring",
            "btn_text" : "Мониторинг",
            "btn_tooltip" : "Мониторинг",
            "show_top" : True,
            "is_active" : False
        },
        {
            "btn_icon" : "icon_journal.svg",
            "btn_id" : "btn_journal",
            "btn_text" : "Журнал данных",
            "btn_tooltip" : "Журнал данных",
            "show_top" : True,
            "is_active" : False
        },
        {
            "btn_icon" : "icon_settings.svg",
            "btn_id" : "btn_settings",
            "btn_text" : "Настройки",
            "btn_tooltip" : "Настройки",
            "show_top" : False,
            "is_active" : False
        }
    ]


    # SETUP CUSTOM BTNs OF CUSTOM WIDGETS
    # Get sender() function when btn is clicked
    # ///////////////////////////////////////////////////////////////
    def setup_btns(self):
        if self.ui.title_bar.sender() != None:
            return self.ui.title_bar.sender()
        elif self.ui.left_menu.sender() != None:
            return self.ui.left_menu.sender()
        elif self.ui.left_column.sender() != None:
            return self.ui.left_column.sender()
        elif self.left_menu_page_1.sender() != None:
            return self.left_menu_page_1.sender()
        else:
            return self.sender()

    # SETUP MAIN WINDOW WITH CUSTOM PARAMETERS
    # ///////////////////////////////////////////////////////////////
    def setup_gui(self):
        # APP TITLE
        # ///////////////////////////////////////////////////////////////
        self.setWindowTitle(f'{self.settings["app_name"]} {self.settings["version"]}')
        
        # REMOVE TITLE BAR
        # ///////////////////////////////////////////////////////////////
        if self.settings["custom_title_bar"]:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

        # ADD GRIPS
        # ///////////////////////////////////////////////////////////////
        if self.settings["custom_title_bar"]:
            self.left_grip = PyGrips(self, "left", self.hide_grips)
            self.right_grip = PyGrips(self, "right", self.hide_grips)
            self.top_grip = PyGrips(self, "top", self.hide_grips)
            self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
            self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
            self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
            self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
            self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)

        # LEFT MENUS / GET SIGNALS WHEN LEFT MENU BTN IS CLICKED / RELEASED
        # ///////////////////////////////////////////////////////////////
        # ADD MENUS
        self.ui.left_menu.add_menus(SetupMainWindow.add_left_menus)

        # SET SIGNALS
        self.ui.left_menu.clicked.connect(self.btn_clicked)
        self.ui.left_menu.released.connect(self.btn_released)


        # SET SIGNALS
        self.ui.title_bar.clicked.connect(self.btn_clicked)
        self.ui.title_bar.released.connect(self.btn_released)

        #self.ui.title_bar.set_title(f'{self.settings["version"]}')

        # LEFT COLUMN SET SIGNALS
        # ///////////////////////////////////////////////////////////////
        self.ui.left_column.clicked.connect(self.btn_clicked)
        self.ui.left_column.released.connect(self.btn_released)

        # SET INITIAL PAGE / SET LEFT AND RIGHT COLUMN MENUS
        # ///////////////////////////////////////////////////////////////
        MainFunctions.set_page(self, self.ui.load_pages.page_0)
        MainFunctions.set_left_column_menu(
            self,
            menu = self.ui.left_column.menus.menu_1,
            title = "Наcтройки",
            icon_path = Functions.set_svg_icon("icon_settings.svg")
        )
        MainFunctions.set_right_column_menu(self, self.ui.right_column.menu_1)



        # ///////////////////////////////////////////////////////////////
        # EXAMPLE CUSTOM WIDGETS
        # Here are added the custom widgets to pages and columns that
        # were created using Qt Designer.
        # This is just an example and should be deleted when creating
        # your application.
        #
        # OBJECTS FOR LOAD PAGES, LEFT AND RIGHT COLUMNS
        # You can access objects inside Qt Designer projects using
        # the objects below:
        #
        # <OBJECTS>
        # LEFT COLUMN: self.ui.left_column.menus
        # RIGHT COLUMN: self.ui.right_column
        # LOAD PAGES: self.ui.load_pages
        # </OBJECTS>
        # ///////////////////////////////////////////////////////////////

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        themes = Themes()
        self.themes = themes.items

        # LEFT COLUMN
        # ///////////////////////////////////////////////////////////////

        # SETTINGS BTN 1
        self.btn_pools = PyPushButton(
            btn_id='btn_pools',
            text="Бассейны",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon = QIcon(Functions.set_svg_icon("icon_pool.svg"))
        self.btn_pools.setIcon(self.icon)
        self.btn_pools.setIconSize(QSize(30, 30))
        self.btn_pools.setMaximumHeight(40)
        self.ui.left_column.menus.btn_1_layout.addWidget(self.btn_pools)
        self.btn_pools.clicked.connect(self.btn_clicked)

        # SETTINGS BTN 2
        self.btn_sensors = PyPushButton(
            text="Датчики",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon = QIcon(Functions.set_svg_icon("icon_sensor.svg"))
        self.btn_sensors.setIcon(self.icon)
        self.btn_sensors.setIconSize(QSize(30, 30))
        self.btn_sensors.setMaximumHeight(40)
        self.ui.left_column.menus.btn_2_layout.addWidget(self.btn_sensors)
        self.btn_sensors.clicked.connect(self.btn_clicked)

        # SETTINGS BTN 3
        self.btn_logging = PyPushButton(
            text="Логирование",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon = QIcon(Functions.set_svg_icon("icon_logging.svg"))
        self.btn_logging.setIcon(self.icon)
        self.btn_logging.setIconSize(QSize(30, 30))
        self.btn_logging.setMaximumHeight(40)
        self.ui.left_column.menus.btn_3_layout.addWidget(self.btn_logging)
        self.btn_logging.clicked.connect(self.btn_clicked)


        # PAGES
        # ///////////////////////////////////////////////////////////////

        # PAGE 0 - ADD LOGO TO MAIN PAGE
        self.logo_svg = QSvgWidget(Functions.set_svg_image("logo_home.svg"))
        self.ui.load_pages.logo_layout.addWidget(self.logo_svg, Qt.AlignCenter, Qt.AlignCenter)

        # PAGE 1
        # ADD FRAME LEFT MENU PAGE 1
        left_menu_margin = self.settings["left_menu_content_margins"]
        left_menu_minimum = self.settings["left_menu_size"]["minimum"]
        self.left_menu_frame_page_1 = QFrame(self)
        self.left_menu_frame_page_1.setMaximumSize(left_menu_minimum + (left_menu_margin * 2), 17280)
        self.left_menu_frame_page_1.setMinimumSize(left_menu_minimum + (left_menu_margin * 2), 0)

        # LEFT MENU LAYOUT
        self.left_menu_frame_page_1_layout = QVBoxLayout(self.left_menu_frame_page_1)
        self.left_menu_frame_page_1_layout.setContentsMargins(left_menu_margin,
                                                 left_menu_margin,
                                                 left_menu_margin,
                                                 left_menu_margin)
        self.left_menu_frame_page_1_layout.setContentsMargins(0,0,0,0)
        self.left_menu_frame_page_1_layout.setSpacing(20)

        # ADD LEFT MENU
        self.left_menu_page_1 = PyLeftMenu1(
            parent = self.left_menu_frame_page_1,
            app_parent = self.ui.central_widget, # For tooltip parent
            dark_one = self.themes["app_color"]["dark_one"],
            dark_three = self.themes["app_color"]["dark_three"],
            dark_four = self.themes["app_color"]["dark_four"],
            bg_one = self.themes["app_color"]["bg_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["icon_hover"],
            icon_color_pressed = self.themes["app_color"]["icon_pressed"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            context_color = self.themes["app_color"]["context_color"],
            minimum_width = self.settings["left_menu_size"]["minimum"],
            maximum_width = self.settings["left_menu_size"]["maximum"]
        )
        self.left_menu_page_1.bg.setStyleSheet(f"background: {self.themes['app_color']['bg_three']};"
                                               f"border-radius: 8px;")
        self.left_menu_page_1.clicked.connect(self.btn_clicked)
        self.left_menu_frame_page_1_layout.addWidget(self.left_menu_page_1)

        self.left_menu_page_1.add_menus(MainFunctions.update_pools_list(self))
        self.current_pool = MainFunctions.get_first_pool(self)
        MainFunctions.set_current_pool(self, self.current_pool['id'])

        self.preview_frame = QFrame(self)
        #self.preview_frame.setMaximumSize(600, 600)

        self.preview_frame_layout = QVBoxLayout(self.preview_frame)
        self.preview_frame_layout.setContentsMargins(0,0,0,0)


        '''self.chart_frame = QFrame(self)
        self.chart_frame.setObjectName('chart_frame')
        self.chart_frame.setStyleSheet(u"#chart_frame{"
                                       u"background: #FFFFFF;"
                                       u"border: none;"
                                       u"border-radius: 10px;}")
        self.chart_frame.setMaximumSize(self.preview_size[0] - 9, 180)
        self.chart_frame.setMinimumSize(self.preview_size[0] - 9, 180)

        self.chart_frame_layout = QVBoxLayout(self.chart_frame)
        self.chart_frame_layout.setContentsMargins(0,0,0,0)
        self.right_top_layout.addWidget(self.chart_frame, alignment=Qt.AlignHCenter | Qt.AlignVCenter)'''

        '''self.chart = QChart()
        self.chart.layout().setContentsMargins(0,0,0,0)
        self.chart_view = TaskChartView(self.chart)
        self.chart_view.setRubberBand(TaskChartView.ClickThroughRubberBand)
        self.chart_view.setRenderHint(QPainter.Antialiasing, True)
        self.chart_view.dataArea.connect(lambda: TaskWindowFunctions.insert_selected_chart_data(self, self.chart_view.data_area))
        self.chart_frame_layout.addWidget(self.chart_view)'''

        '''# ADD SPACER
        self.top_layout.addItem(QSpacerItem(0, 800, QSizePolicy.Minimum, QSizePolicy.Fixed))'''

        # ADD VIEWFINDER
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()

        self.l_preview = QLabel()
        self.l_preview.setObjectName('preview')
        self.l_preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.l_preview.setStyleSheet(u"QLabel{"
                                     u"background: transparent;}")
        self.l_preview.setGeometry(0, 0, self.width() / 2, self.width() / 2)

        self.l_camera_fps = QLabel()
        self.l_camera_fps.setObjectName(u"l_camera_fps")
        self.l_camera_fps.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.l_camera_fps.setGeometry(0, 0, 50, 25)
        self.l_camera_fps.setStyleSheet(u"QLabel{"
                                         u"background: transparent;"
                                         u"color: #B1E856;"
                                         u"font-family: 'Roboto';"
                                         u"font-size: 14px;"
                                         u"font-style: normal;"
                                         u"font-weight: 400;}")

        self.view.setMouseTracking(True)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setScene(self.scene)
        self.scene.installEventFilter(self)
        self.preview_frame_layout.addWidget(self.view, 0, Qt.AlignHCenter)
        self.proxy_wid_preview = QGraphicsProxyWidget()
        self.proxy_wid_preview.setWidget(self.l_preview)
        self.scene.addItem(self.proxy_wid_preview)

        VideoFunctions.setup_video_processing(self)

        self.proxy_wid_l_camera_fps = QGraphicsProxyWidget()
        self.proxy_wid_l_camera_fps.setWidget(self.l_camera_fps)
        self.proxy_wid_l_camera_fps.setPos(QPoint(self.scene.sceneRect().width() - self.l_camera_fps.width() - 10, 5))
        self.scene.addItem(self.proxy_wid_l_camera_fps)


        # TABLE WIDGETS
        self.sensors_table_widget = PyTableWidget(
            radius = 8,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["context_color"],
            bg_color = self.themes["app_color"]["bg_two"],
            header_horizontal_color = self.themes["app_color"]["dark_two"],
            header_vertical_color = self.themes["app_color"]["bg_three"],
            bottom_line_color = self.themes["app_color"]["bg_three"],
            grid_line_color = self.themes["app_color"]["bg_one"],
            scroll_bar_bg_color = self.themes["app_color"]["bg_one"],
            scroll_bar_btn_color = self.themes["app_color"]["dark_four"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.sensors_table_widget.setColumnCount(2)
        self.sensors_table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.sensors_table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sensors_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.sensors_table_widget.setColumnWidth(1, 120)
        self.sensors_table_widget.verticalHeader().setVisible(False)
        self.sensors_table_widget.horizontalHeader().setMaximumHeight(25)

        # Columns / Header
        self.column_1 = QTableWidgetItem()
        self.column_1.setTextAlignment(Qt.AlignCenter)
        self.column_1.setText("Наименование датчика")

        self.column_2 = QTableWidgetItem()
        self.column_2.setTextAlignment(Qt.AlignCenter)
        self.column_2.setText("Значение")

        # Set column
        self.sensors_table_widget.setHorizontalHeaderItem(0, self.column_1)
        self.sensors_table_widget.setHorizontalHeaderItem(1, self.column_2)


        for x in range(10):
            row_number = self.sensors_table_widget.rowCount()
            self.sensors_table_widget.insertRow(row_number) # Insert row
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            item.setText(f"Датчик {x}")
            item1 = QTableWidgetItem()
            item1.setTextAlignment(Qt.AlignCenter)
            item1.setText(f"{x}")
            self.sensors_table_widget.setItem(row_number, 0, item)
            self.sensors_table_widget.setItem(row_number, 1, item1)
            self.sensors_table_widget.setRowHeight(row_number, 22)


        # PAGE 2
        # CIRCULAR PROGRESS 1
        self.circular_progress_1 = PyCircularProgress(
            value = 80,
            progress_color = self.themes["app_color"]["context_color"],
            text_color = self.themes["app_color"]["text_title"],
            font_size = 14,
            bg_color = self.themes["app_color"]["dark_four"]
        )
        self.circular_progress_1.setFixedSize(200,200)

        # CIRCULAR PROGRESS 2
        self.circular_progress_2 = PyCircularProgress(
            value = 45,
            progress_width = 4,
            progress_color = self.themes["app_color"]["context_color"],
            text_color = self.themes["app_color"]["context_color"],
            font_size = 14,
            bg_color = self.themes["app_color"]["bg_three"]
        )
        self.circular_progress_2.setFixedSize(160,160)

        # CIRCULAR PROGRESS 3
        self.circular_progress_3 = PyCircularProgress(
            value = 75,
            progress_width = 2,
            progress_color = self.themes["app_color"]["pink"],
            text_color = self.themes["app_color"]["white"],
            font_size = 14,
            bg_color = self.themes["app_color"]["bg_three"]
        )
        self.circular_progress_3.setFixedSize(140,140)

        # PY SLIDER 1
        self.vertical_slider_1 = PySlider(
            margin=8,
            bg_size=10,
            bg_radius=5,
            handle_margin=-3,
            handle_size=16,
            handle_radius=8,
            bg_color = self.themes["app_color"]["dark_three"],
            bg_color_hover = self.themes["app_color"]["dark_four"],
            handle_color = self.themes["app_color"]["context_color"],
            handle_color_hover = self.themes["app_color"]["context_hover"],
            handle_color_pressed = self.themes["app_color"]["context_pressed"]
        )
        self.vertical_slider_1.setMinimumHeight(100)

        # PY SLIDER 2
        self.vertical_slider_2 = PySlider(
            bg_color = self.themes["app_color"]["dark_three"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            handle_color = self.themes["app_color"]["context_color"],
            handle_color_hover = self.themes["app_color"]["context_hover"],
            handle_color_pressed = self.themes["app_color"]["context_pressed"]
        )
        self.vertical_slider_2.setMinimumHeight(100)

        # PY SLIDER 3
        self.vertical_slider_3 = PySlider(
            margin=8,
            bg_size=10,
            bg_radius=5,
            handle_margin=-3,
            handle_size=16,
            handle_radius=8,
            bg_color = self.themes["app_color"]["dark_three"],
            bg_color_hover = self.themes["app_color"]["dark_four"],
            handle_color = self.themes["app_color"]["context_color"],
            handle_color_hover = self.themes["app_color"]["context_hover"],
            handle_color_pressed = self.themes["app_color"]["context_pressed"]
        )
        self.vertical_slider_3.setOrientation(Qt.Horizontal)
        self.vertical_slider_3.setMaximumWidth(200)

        # PY SLIDER 4
        self.vertical_slider_4 = PySlider(
            bg_color = self.themes["app_color"]["dark_three"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            handle_color = self.themes["app_color"]["context_color"],
            handle_color_hover = self.themes["app_color"]["context_hover"],
            handle_color_pressed = self.themes["app_color"]["context_pressed"]
        )
        self.vertical_slider_4.setOrientation(Qt.Horizontal)
        self.vertical_slider_4.setMaximumWidth(200)

        # ICON BUTTON 1
        self.icon_button_1 = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_heart.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "Icon button - Heart",
            width = 40,
            height = 40,
            radius = 20,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["icon_hover"],
            icon_color_pressed = self.themes["app_color"]["icon_active"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["pink"]
        )

        # ICON BUTTON 2
        self.icon_button_2 = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_add_user.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "BTN with tooltip",
            width = 40,
            height = 40,
            radius = 8,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["icon_hover"],
            icon_color_pressed = self.themes["app_color"]["white"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["green"],
        )

        # ICON BUTTON 3
        self.icon_button_3 = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_add_user.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "BTN actived! (is_actived = True)",
            width = 40,
            height = 40,
            radius = 8,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["icon_hover"],
            icon_color_pressed = self.themes["app_color"]["white"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["context_color"],
            is_active = True
        )

        # PUSH BUTTON 1
        self.push_button_1 = PyPushButton(
            text = "Button Without Icon",
            radius  =8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.push_button_1.setMinimumHeight(40)

        # PUSH BUTTON 2
        self.push_button_2 = PyPushButton(
            text = "Button With Icon",
            radius = 8,
            color = self.themes["app_color"]["text_foreground"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["dark_four"]
        )
        self.icon_2 = QIcon(Functions.set_svg_icon("icon_settings.svg"))
        self.push_button_2.setMinimumHeight(40)
        self.push_button_2.setIcon(self.icon_2)

        # PY LINE EDIT
        self.line_edit = PyLineEdit(
            text = "",
            place_holder_text = "Place holder text",
            radius = 8,
            border_size = 2,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.line_edit.setMinimumHeight(30)

        # TOGGLE BUTTON
        self.toggle_button = PyToggle(
            width = 50,
            bg_color = self.themes["app_color"]["dark_two"],
            circle_color = self.themes["app_color"]["icon_color"],
            active_color = self.themes["app_color"]["context_color"]
        )

        # TABLE WIDGETS
        self.table_widget = PyTableWidget(
            radius = 8,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["context_color"],
            bg_color = self.themes["app_color"]["bg_two"],
            header_horizontal_color = self.themes["app_color"]["dark_two"],
            header_vertical_color = self.themes["app_color"]["bg_three"],
            bottom_line_color = self.themes["app_color"]["bg_three"],
            grid_line_color = self.themes["app_color"]["bg_one"],
            scroll_bar_bg_color = self.themes["app_color"]["bg_one"],
            scroll_bar_btn_color = self.themes["app_color"]["dark_four"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.table_widget.setColumnCount(3)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Columns / Header
        self.column_1 = QTableWidgetItem()
        self.column_1.setTextAlignment(Qt.AlignCenter)
        self.column_1.setText("NAME")

        self.column_2 = QTableWidgetItem()
        self.column_2.setTextAlignment(Qt.AlignCenter)
        self.column_2.setText("NICK")

        self.column_3 = QTableWidgetItem()
        self.column_3.setTextAlignment(Qt.AlignCenter)
        self.column_3.setText("PASS")

        # Set column
        self.table_widget.setHorizontalHeaderItem(0, self.column_1)
        self.table_widget.setHorizontalHeaderItem(1, self.column_2)
        self.table_widget.setHorizontalHeaderItem(2, self.column_3)

        for x in range(10):
            row_number = self.table_widget.rowCount()
            self.table_widget.insertRow(row_number) # Insert row
            self.table_widget.setItem(row_number, 0, QTableWidgetItem(str("Wanderson"))) # Add name
            self.table_widget.setItem(row_number, 1, QTableWidgetItem(str("vfx_on_fire_" + str(x)))) # Add nick
            self.pass_text = QTableWidgetItem()
            self.pass_text.setTextAlignment(Qt.AlignCenter)
            self.pass_text.setText("12345" + str(x))
            self.table_widget.setItem(row_number, 2, self.pass_text) # Add pass
            self.table_widget.setRowHeight(row_number, 22)

        # ADD WIDGETS
        self.ui.load_pages.column_1_layout.addWidget(self.left_menu_frame_page_1)
        self.ui.load_pages.column_2_layout.addWidget(self.preview_frame, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.ui.load_pages.column_3_layout.addWidget(self.sensors_table_widget)
        '''self.ui.load_pages.column_3_layout.addWidget(self.circular_progress_1)
        self.ui.load_pages.column_3_layout.addWidget(self.circular_progress_2)
        self.ui.load_pages.column_3_layout.addWidget(self.circular_progress_3)
        self.ui.load_pages.column_3_layout.addWidget(self.vertical_slider_1)
        self.ui.load_pages.column_3_layout.addWidget(self.vertical_slider_2)
        self.ui.load_pages.column_3_layout.addWidget(self.vertical_slider_3)
        self.ui.load_pages.column_3_layout.addWidget(self.vertical_slider_4)
        self.ui.load_pages.column_3_layout.addWidget(self.icon_button_1)
        self.ui.load_pages.column_3_layout.addWidget(self.icon_button_2)
        self.ui.load_pages.column_3_layout.addWidget(self.icon_button_3)
        self.ui.load_pages.column_3_layout.addWidget(self.push_button_1)
        self.ui.load_pages.column_3_layout.addWidget(self.push_button_2)
        self.ui.load_pages.column_3_layout.addWidget(self.toggle_button)
        self.ui.load_pages.column_3_layout.addWidget(self.line_edit)
        self.ui.load_pages.column_3_layout.addWidget(self.table_widget)'''

        # RIGHT COLUMN
        # ///////////////////////////////////////////////////////////////

        # BTN 1
        self.right_btn_1 = PyPushButton(
            text="Show Menu 2",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon_right = QIcon(Functions.set_svg_icon("icon_arrow_right.svg"))
        self.right_btn_1.setIcon(self.icon_right)
        self.right_btn_1.setMaximumHeight(40)
        self.right_btn_1.clicked.connect(lambda: MainFunctions.set_right_column_menu(
            self,
            self.ui.right_column.menu_2
        ))
        self.ui.right_column.btn_1_layout.addWidget(self.right_btn_1)

        # BTN 2
        self.right_btn_2 = PyPushButton(
            text="Show Menu 1",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon_left = QIcon(Functions.set_svg_icon("icon_arrow_left.svg"))
        self.right_btn_2.setIcon(self.icon_left)
        self.right_btn_2.setMaximumHeight(40)
        self.right_btn_2.clicked.connect(lambda: MainFunctions.set_right_column_menu(
            self,
            self.ui.right_column.menu_1
        ))
        self.ui.right_column.btn_2_layout.addWidget(self.right_btn_2)

        # ///////////////////////////////////////////////////////////////
        # END - EXAMPLE CUSTOM WIDGETS
        # ///////////////////////////////////////////////////////////////

    # RESIZE GRIPS AND CHANGE POSITION
    # Resize or change position when window is resized
    # ///////////////////////////////////////////////////////////////
    def resize_grips(self):
        if self.settings["custom_title_bar"]:
            self.left_grip.setGeometry(5, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
            self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
            self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
            self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
            self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)