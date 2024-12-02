# -*- coding: utf-8 -*-

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.json_settings import Settings
from uis.windows.main_window.functions_main_window import *
from uis.windows.main_window import *
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
        self.current_pool = {'id': None, 'name': None}

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # SETUP MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.hide_grips = True # Show/Hide resize grips
        SetupMainWindow.setup_gui(self)

        # SHOW MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.show()

    # LEFT MENU BTN IS CLICKED
    # Run function when btn is clicked
    # Check funtion by object name / btn_id
    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self):
        # GET BT CLICKED
        btn = SetupMainWindow.setup_btns(self)

        # Remove Selection If Clicked By "btn_close_left_column"
        '''if btn.objectName() != "btn_settings":
            self.ui.left_menu.deselect_all_tab()
            btn.set_active(False)'''

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
        
        if 'pool_' in btn.objectName():
            MainFunctions.set_current_pool(self, btn.objectName())

        if btn.objectName() == "btn_pools":
            if self.current_pool['id']:
                msg = PyMessageBox(self,
                                   mode='question',
                                   text_message='Вы действительно хотите удалить запись?',
                                   button_yes_text='Да',
                                   button_no_text='Нет',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
                msg.yes.connect(lambda: MainFunctions.delete_pool(self, self.current_pool['id']))
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
        #print(f"Button {btn.objectName()}, released!")

    # RESIZE EVENT
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        SetupMainWindow.resize_grips(self)


    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()


# SETTINGS WHEN TO START
# Set the initial class and also additional parameters of the "QApplication" class
# ///////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # APPLICATION
    # ///////////////////////////////////////////////////////////////
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()

    # EXEC APP
    # ///////////////////////////////////////////////////////////////
    sys.exit(app.exec())