# -*- coding: utf-8 -*-

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.json_settings import Settings
from uis.windows.main_window.functions_main_window import *
from uis.windows.main_window.functions_video import *
from uis.windows.main_window import *
from uis.windows.second_windows import *
from widgets import *

# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # SETUP MAIN WINDOw
        # Load widgets from "uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

        # SETUP VALUES
        # ///////////////////////////////////////////////////////////////
        self.current_pool_page_1 = {'id': None, 'name': None}
        self.current_pool_page_3 = {'id': None, 'name': None}
        self.current_camera = None

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # SETUP MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.hide_grips = True # Show/Hide resize grips

        self.setup_starting()

        # SHOW MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.show()

    # LEFT MENU BTN IS CLICKED
    # Run function when btn is clicked
    # Check funtion by object name / btn_id
    # ///////////////////////////////////////////////////////////////
    def setup_starting(self):
        SetupMainWindow.setup_gui(self)
        self.current_pool_page_1 = MainFunctions.get_first_pool(self)
        MainFunctions.set_current_pool(self, f"page_1__{self.current_pool_page_1['id']}")
        self.current_pool_page_3 = MainFunctions.get_first_pool(self)
        MainFunctions.set_current_pool(self, f"page_3__{self.current_pool_page_3['id']}", page=3)
        VideoFunctions.setup_video_input(self)
        VideoFunctions.change_camera(self)

    def btn_clicked(self):
        # GET BT CLICKED
        btn = SetupMainWindow.setup_btns(self)

        # LEFT MENU
        # ///////////////////////////////////////////////////////////////
        
        # HOME BTN
        if btn.objectName() == "btn_monitoring":
            if MainFunctions.left_column_is_visible(self):
                MainFunctions.toggle_left_column(self)
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())

            # Load Page 1
            MainFunctions.set_page(self, self.ui.load_pages.page_1)

        # WIDGETS BTN
        if btn.objectName() == "btn_journal":
            if MainFunctions.left_column_is_visible(self):
                MainFunctions.toggle_left_column(self)
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())

            # Load Page 2
            MainFunctions.set_page(self, self.ui.load_pages.page_2)


        # SETTINGS LEFT
        if btn.objectName() == "btn_settings" or btn.objectName() == "btn_close_left_column":
            # CHECK IF LEFT COLUMN IS VISIBLE
            if not MainFunctions.left_column_is_visible(self):
                # Show / Hide
                MainFunctions.toggle_left_column(self)
                self.ui.left_menu.select_only_one(btn.objectName())
                self.ui.left_menu.select_only_one_tab(btn.objectName())
            else:
                if btn.objectName() == "btn_close_left_column":
                    self.ui.left_menu.deselect_all_tab()
                    # Show / Hide
                    MainFunctions.toggle_left_column(self)
                self.ui.left_menu.select_only_one(btn.objectName())
                self.ui.left_menu.select_only_one_tab(btn.objectName())

            # Change Left Column Menu
            if btn.objectName() != "btn_close_left_column":
                MainFunctions.set_left_column_menu(
                    self, 
                    menu = self.ui.left_column.menus.menu_1,
                    title = "Настройки",
                    icon_path = Functions.set_svg_icon("icon_settings.svg")
                )
        
        if 'page_1__pool_' in btn.objectName():
            self.l_preview.hide()
            self.btn_camera_preview.show()
            MainFunctions.set_current_pool(self, btn.objectName())
            VideoFunctions.change_camera(self)

        if 'page_2__pool_' in btn.objectName():
            pass

        if 'page_3__pool_' in btn.objectName():
            pass

        if btn.objectName() == 'page_3__add_pool':
            self.add_pool_ui = UI_AddPool(self)
            self.add_pool_ui.clicked.connect(self.btn_clicked)
            self.add_pool_ui.show()

        if btn.objectName() == 'pbtn_add_pool':
            data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                 table='pools')
            if data[0] and data[1]:
                self.left_menu_page_1.add_menus(MainFunctions.get_add_menu_parameters(self, data[1][-1]['pool_id']))
                self.left_menu_page_3.add_menus(MainFunctions.get_add_menu_parameters(self, data[1][-1]['pool_id'], page=3))


        if btn.objectName() == 'page_3__delete_pool':
            if self.current_pool_page_3['id']:
                msg = PyMessageBox(self,
                                   mode='question',
                                   text_message='Вы действительно хотите удалить запись?',
                                   button_yes_text='Да',
                                   button_no_text='Нет',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
                msg.yes.connect(lambda: MainFunctions.delete_pool(self, self.current_pool_page_3['id']))
                msg.l_message.setWordWrap(False)
                msg.show()
            else:
                msg = PyMessageBox(self,
                                   mode='information',
                                   text_message='Нет записей для удаления!',
                                   button_yes_text='Ok',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
                msg.l_message.setWordWrap(False)
                msg.show()

        if btn.objectName() == "btn_pools":
            MainFunctions.set_page(self, self.ui.load_pages.page_3)


        if btn.objectName() == "btn_camera_preview":
            self.l_preview.clear()
            self.l_preview.show()
            self.camera_connect_thread.cam_connect()

        # DEBUG
        print(f"Button {btn.objectName()}, clicked!")

    # LEFT MENU BTN IS RELEASED
    # Run function when btn is released
    # Check funtion by object name / btn_id
    # ///////////////////////////////////////////////////////////////
    def btn_released(self):
        # GET BT CLICKED
        btn = SetupMainWindow.setup_btns(self)

        # DEBUG
        print(f"Button {btn.objectName()}, released!")

    # RESIZE EVENT
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        SetupMainWindow.resize_grips(self)

    def closeEvent(self, event):
        VideoFunctions.stop_video_processing_threads(self)
        self.camera_thread.terminate()
        self.camera_connect_thread.terminate()
        event.accept()

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition().toPoint()


    '''def paintEvent(self, event):
        if not self.view.sceneRect().isNull() and self.resize_flag:
            self.view.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)
            self.resize_flag = False
        path = QPainterPath()
        # the rectangle must be translated and adjusted by 1 pixel in order to
        # correctly map the rounded shape
        rect = QRectF(self.view.rect()).adjusted(4.5, 4.5, -4.5, -4.5)
        path.addRoundedRect(rect, self.view_finder_radius, self.view_finder_radius, Qt.AbsoluteSize)
        # QRegion is bitmap based, so the returned QPolygonF (which uses float
        # values must be transformed to an integer based QPolygon
        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.view.setMask(region)
        if self.frameGeometry().center() != self.frameGeometry().center(): self.center()'''


# SETTINGS WHEN TO START
# Set the initial class and also additional parameters of the "QApplication" class
# ///////////////////////////////////////////////////////////////
if __name__ == "__main__":
    '''# APPLICATION
    # ///////////////////////////////////////////////////////////////
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()

    # EXEC APP
    # ///////////////////////////////////////////////////////////////
    sys.exit(app.exec())'''

    app = qasync.QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    window = MainWindow()
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())