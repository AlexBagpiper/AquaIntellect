# -*- coding: utf-8 -*-

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
import asyncio

from uis.windows.main_window.functions_main_window import *
from uis.windows.main_window.functions_patient_page import *
from uis.windows.main_window.functions_reseption_page import *
from uis.windows.main_window.functions_test_task_page import *
from uis.windows.main_window.functions_setting_page import *
from uis.windows.main_window.functions_calendar_page import *


# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

# IMPORT SETTINGS
# ///////////////////////////////////////////////////////////////
from core.json_settings import Settings
from core.function_server import *

# IMPORT WINDOWS
# ///////////////////////////////////////////////////////////////
# MAIN WINDOW
from uis.windows.main_window import *

# SECOND WINDOWS
from uis.windows.second_windows import *

# IMPORT WIDGETS
# ///////////////////////////////////////////////////////////////
from widgets import *


# AUTH WINDOW
# ///////////////////////////////////////////////////////////////
class AuthWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.auth = UI_Auth(parent)
        self.auth.clicked.connect(self.open_main)
        self.parent = parent
        self.auth.show()

    def open_main(self, str_signal):
        # SHOW MAIN WINDOW
        if str_signal == 'exit':
            self.parent.close()
        else:
            self.parent.staff_id = str_signal
            MainFunctions.toggle_login_window(self.parent, True)
            self.parent.ui.left_menu.toggle_animation()
            QTimer.singleShot(700, lambda: self.parent.btn_clicked(btn = self.parent.findChild(QPushButton, 'mbtn_patient')))


# LOGIN WINDOW
# ///////////////////////////////////////////////////////////////
class StartLoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.login = UI_LoginMain(parent)
        self.login.clicked.connect(self.open_main)
        self.parent = parent
        QTimer.singleShot(1000, lambda: self.login.show())

    def open_main(self, str_signal):
        # SHOW MAIN WINDOW
        if str_signal == 'exit':
            self.parent.close()
        else:
            self.parent.staff_id = str_signal
            MainFunctions.toggle_login_window(self.parent, True)
            self.parent.ui.left_menu.toggle_animation()
            QTimer.singleShot(700, lambda: self.parent.btn_clicked(btn = self.parent.findChild(QPushButton, 'mbtn_patient')))


# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # SETUP MAIN WINDOw
        # Load widgets from "gui\uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # SETUP MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.hide_grips = True # Show/Hide resize grips
        SetupMainWindow.setup_gui(self)
        SetupStarting.setup_start(self)
        MainFunctions.toggle_login_window(self, True)
        self.ui.left_menu.toggle_animation()
        self.show()

        # SHOW MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='companies')
        if data[1][0]['company_id'] == 'empty':
            self.auth_window = AuthWindow(self)
            self.save_flag = True
        else:
            if not self.check_lic_on_start():
                self.save_flag = True
                msg = PyMessageBox(self,
                               mode = 'warning',
                               text_message='Ошибка лицензии!\nРабота программы будет завершена.',
                               button_yes_text='Ok',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
                msg.yes.connect(lambda: self.close())
                QTimer.singleShot(1100, lambda: msg.show())
            if not Functions.server_available(self.settings['server_settings']['ip'], self.settings['server_settings']['port']) and self.settings['server_settings']['check_available']:
                self.save_flag = True
                msg = PyMessageBox(self,
                                   mode = 'warning',
                                   text_message='Отсутствует связь с сервером!\nРабота программы будет завершена.',
                                   button_yes_text='Да',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
                msg.yes.connect(lambda: self.close())
                QTimer.singleShot(1100, lambda: msg.show())


        #self.center()
        self.login_main = StartLoginWindow(self)


        # PROGRAM VARIABLES
        # ///////////////////////////////////////////////////////////////
        self.staff_id = None
        self.access_token = None
        self.refresh_token = None
        # DEBUG VARIABLE
        # DEL AFTER DEBUG

        # DEBUG VARIABLE
        # DEL AFTER DEBUG


    def check_lic_on_start(self):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='companies')
        try:
            url = f"{self.settings['server_settings']['protocol']}{self.settings['server_settings']['ip']}:{self.settings['server_settings']['port']}/api/verify"
            payload = json.dumps({"licenseNumber": data[1][0]['license_number'],
                                  "deviceId": Functions.get_hwid(),
                                  "companyId": data[1][0]['company_id']})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                return True
            else:
                self.logger.info(f'ошибка проверки лицензии код: {response.status_code} {response.text}')
                return False
        except Exception as e:
            self.logger.exception(f'ошибка проверки лицензии: {e}')
            return False


    def center(self):
        frame_geo = self.frameGeometry()
        screen = self.window().windowHandle().screen()
        center_loc = screen.geometry().center()
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.topLeft())


    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self, btn = None):
        # GET BT CLICKED
        btn = SetupMainWindow.setup_btns(self, btn)

        # Remove Selection If Clicked By "btn_close_left_column"
        if btn.objectName() != "btn_settings":
            self.ui.left_menu.deselect_all_tab()

        # Get Title Bar Btn And Reset Active         
        top_settings = MainFunctions.get_title_bar_btn(self, "btn_top_help")
        top_settings.set_active(False)

        # LEFT MENU
        # ///////////////////////////////////////////////////////////////
        
        # PATIENTS BTN
        if btn.objectName() == "mbtn_patient":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            # Load Page 1
            MainFunctions.set_page(self, self.ui.load_pages.page_1)
            self.ledit_search_patient.setFocus()
        # SETTING BTN
        if btn.objectName() == "mbtn_setting":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            # Load Page 2
            SettingPageFunctions.prepare_page(self)
            MainFunctions.set_page(self, self.ui.load_pages.page_2)
            MainFunctions.set_subpage_page_2(self, self.ui.load_pages.page_2_subpage_1)
        # PROFILE BTN
        if btn.objectName() == "mbtn_profile":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            # Load Page 3 
            MainFunctions.set_page(self, self.ui.load_pages.page_3)
        # ANALITIK BTN
        if btn.objectName() == "mbtn_analitik":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            # Load Page 3
            MainFunctions.set_page(self, self.ui.load_pages.page_3)
        
        # TITLE BAR MENU
        # ///////////////////////////////////////////////////////////////
        
        # HELP BUTTON
        if btn.objectName() == "btn_top_help":
            '''self.task_window_ui = UI_TaskWindow(self,
                cur_session_id = '187a942a-5107-11ed-9650-9cb6d00af772',
                tasks_list = [{'task_id': 'task_1', 'task_solution': 'hand_left', 'result_task_id': False, 'is_current_task': False},
                              {'task_id': 'task_2', 'task_solution': 'hand_right', 'result_task_id': False, 'is_current_task': True},
                              {'task_id': 'task_3', 'task_solution': 'hand_left', 'result_task_id': '111', 'is_current_task': False},
                              {'task_id': 'task_5', 'task_solution': 'hand_left', 'result_task_id': False, 'is_current_task': False},
                              {'task_id': 'task_11', 'task_solution': 'pose', 'result_task_id': False, 'is_current_task': False},
                              {'task_id': 'task_7', 'task_solution': 'hand_left', 'result_task_id': False, 'is_current_task': False},
                              {'task_id': 'task_9', 'task_solution': 'hand_left', 'result_task_id': False, 'is_current_task': False},
                              {'task_id': 'task_8', 'task_solution': 'hand_right', 'result_task_id': False, 'is_current_task': False}])
            self.task_window_ui.clicked.connect(self.btn_clicked)
            self.task_window_ui.show()'''

            #MainFunctions.update_token(self)
            #MainFunctions.upload_video_tests(self, 9, '4b37ce7d-a062-11ee-97e0-9cb6d00af772')
            #FunctionServer.update_token(self)
            FunctionServer.add_session(self, '0ee2e368-31ce-11ef-8d01-9cb6d00af772')


            pass

        # PAGE 1 SUBPAGE 1
        # ///////////////////////////////////////////////////////////////

        # New patient btn
        if btn.objectName() == "pbtn_new_patient":
            PatientPageFunctions.new_patient(self, 1)
        # New patient btn
        if btn.objectName() == "pbtn_edit_patient":
            PatientPageFunctions.edit_patient(self, 1)
        # Start session btn
        if btn.objectName() == "pbtn_start_session":
            ReseptionPageFunctions.prepare_to_session(self)
            PatientPageFunctions.set_subpage_page_1(self, self.ui.load_pages.page_1_subpage_3)
        # Calendar btn
        if btn.objectName() == "pbtn_calendar":
            CalendarPageFunctions.prepare_calendar_page(self)
            PatientPageFunctions.set_subpage_page_1(self, self.ui.load_pages.page_1_subpage_6)


        # PAGE 1 SUBPAGE 2
        # ///////////////////////////////////////////////////////////////

        # Patient page save create btn
        if btn.objectName() == "pbtn_save_create_patient":
            PatientPageFunctions.save_new_patient(self)
        # Patient page save edit btn
        if btn.objectName() == "pbtn_save_edit_patient":
            PatientPageFunctions.save_edit_patient(self)
        # Cancel new/edit patient btn
        if btn.objectName() == "pbtn_cancel_patient":
            PatientPageFunctions.set_subpage_page_1(self, self.previous_page)
        # Back btn
        if btn.objectName() == "btn_back_to_page_1_subpage_1":
            PatientPageFunctions.set_subpage_page_1(self, self.previous_page)
        # Link PN Expert account btn
        if btn.objectName() == "link_get_pnexpert_account":
            pass
        # Link open and print btn
        if btn.objectName() == "link_open_and_print":
            PatientPageFunctions.generate_agreement(self)
        # Attach personal data path btn
        if btn.objectName() == "btn_attach_personal_data_path":
            PatientPageFunctions.attach_personal_data(self)
        # View attached personal data path btn
        if btn.objectName() == "btn_view_personal_data_path":
            PatientPageFunctions.view_attached_personal_data(self)


        # PAGE 1 SUBPAGE 3
        # ///////////////////////////////////////////////////////////////

        # Reseption page create document btn
        if btn.objectName() == "pbtn_create_document":
            if hasattr(self, 'create_document_window_ui'):
                self.create_document_window_ui.hide()
                del self.create_document_window_ui
            self.create_document_window_ui = UI_CreateDocument(self)
            self.create_document_window_ui.show()
        # Reseption page tests and tasks btn
        if btn.objectName() == "pbtn_test_and_task":
            TestTaskPageFunctions.prepare_page(self)
            ReseptionPageFunctions.test_task_page(self)
        # Reseption page outpatient card btn
        if btn.objectName() == "pbtn_outpatient_card":
            pass
        # Close session btn
        if btn.objectName() == "pbtn_close_session_subpage_3":
            MainFunctions.start_window_animation(self)
            msg = PyMessageBox(self,
                               mode = 'question',
                               text_message='Вы действительно хотите завершить прием?',
                               button_yes_text='Да',
                               button_no_text='Нет',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
            msg.yes.connect(lambda: ReseptionPageFunctions.close_session(self))
            msg.show()
        # Edit patient link btn
        if btn.objectName() == "link_edit_patient_card_subpage_3":
            PatientPageFunctions.edit_patient(self, 3)
        # Result activity link btn
        if btn.objectName() == "link_go_to_result_day_activity_subpage_3":
            pass


        # PAGE 1 SUBPAGE 4
        # ///////////////////////////////////////////////////////////////

        # Back btn
        if btn.objectName() == "btn_back_to_page_1_subpage_4":
            PatientPageFunctions.set_subpage_page_1(self, self.ui.load_pages.page_1_subpage_3)
        # Close session btn
        if btn.objectName() == "pbtn_close_session_subpage_4":
            MainFunctions.start_window_animation(self)
            msg = PyMessageBox(self,
                               mode = 'question',
                               text_message='Вы действительно хотите завершить прием?',
                               button_yes_text='Да',
                               button_no_text='Нет',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
            msg.yes.connect(lambda: ReseptionPageFunctions.close_session(self))
            msg.show()
        # View screenplay link btn
        if btn.objectName() == "link_screenplay_subpage_4":
            TestTaskPageFunctions.view_screenplay(self, 4)
        # Edit screenplay link btn
        if btn.objectName() == "link_edit_scpeenplay_session_subpage_4":
            TestTaskPageFunctions.edit_screenplay(self, 4)
        # Edit patient link btn
        if btn.objectName() == "link_edit_patient_card_subpage_4":
            PatientPageFunctions.edit_patient(self, 4)
        # Result activity link btn
        if btn.objectName() == "link_go_to_result_day_activity_subpage_4":
            pass


        # PAGE 1 SUBPAGE 5
        # ///////////////////////////////////////////////////////////////

        # Back btn
        if btn.objectName() == "btn_back_to_page_1_subpage_5":
            if self.previous_page == self.findChild(QWidget, f'page_1_subpage_5'):
                self.previous_page = self.findChild(QWidget, f'page_1_subpage_4')
            TestTaskPageFunctions.fill_page(self)
            TestTaskPageFunctions.set_subpage_page_1(self, self.previous_page)
        # Edit screenplay btn
        if btn.objectName() == "pbtn_edit_screenplay":
            TestTaskPageFunctions.edit_screenplay(self, 5)
        # Save new screenplay btn
        elif btn.objectName() == "pbtn_save_new_screenplay":
            ScreenplayFunctions.save_new_screenplay(self)
        # Save edit screenplay btn
        elif btn.objectName() == "pbtn_save_edit_screenplay":
            ScreenplayFunctions.save_edit_screenplay(self)
        # Create screenplay btn
        if btn.objectName() == "pbtn_create_screenplay":
            ScreenplayFunctions.set_mode_page(self, 'new')
        # Cancel screenplay btn
        elif btn.objectName() == "pbtn_cancel_screenplay":
            if self.previous_page == self.findChild(QWidget, f'page_1_subpage_5'):
                TestTaskPageFunctions.view_screenplay(self, 4)
            else:
                TestTaskPageFunctions.fill_page(self)
                self.previous_page = self.findChild(QWidget, f'page_1_subpage_4')
                TestTaskPageFunctions.set_subpage_page_1(self, self.previous_page)
        # Delete screenplay btn
        if btn.objectName() == "pbtn_del_screenplay_subpage_5":
            ScreenplayFunctions.delete_screenplay(self, self.cur_screenplay_id)
            TestTaskPageFunctions.fill_page(self)
            TestTaskPageFunctions.set_subpage_page_1(self, self.findChild(QWidget, f'page_1_subpage_4'))


        # PAGE 1 SUBPAGE 6
        # ///////////////////////////////////////////////////////////////

        # Back btn
        if btn.objectName() == "btn_back_page_1_subpage_6":
            CalendarPageFunctions.update_calendar(self, "past")
        # Next btn
        elif btn.objectName() == "btn_next_page_1_subpage_6":
            CalendarPageFunctions.update_calendar(self, "next")
        # Save calendar btn
        elif btn.objectName() == "pbtn_save_calendar_page_1_subpage_6":
            ScreenplayFunctions.save_new_screenplay(self)
        # Cancel calendar btn
        elif btn.objectName() == "pbtn_cancel_calendar_page_1_subpage_6":
            #ScreenplayFunctions.save_edit_screenplay(self)
            ScreenplayFunctions.set_subpage_page_1(self, self.findChild(QWidget, f'page_1_subpage_1'))


        # PAGE 2 SUBPAGE 1
        # ///////////////////////////////////////////////////////////////

        # Save btn
        if btn.objectName() == "pbtn_save_setting_page_2_subpage_1":
            SettingPageFunctions.check_save_setting(self)


        # Cancel btn
        if btn.objectName() == "pbtn_cancel_setting_page_2_subpage_1":
            self.ui.left_menu.select_only_one(self.findChild(QPushButton, 'mbtn_patient').objectName())
            MainFunctions.set_page(self, self.ui.load_pages.page_1)


        # CAMERA SETTING BTN
        # ///////////////////////////////////////////////////////////////

        # Choose camera btn
        if btn.objectName() == "pbtn_choose_camera_setting":
            if hasattr(self, 'camera_setting'):
                self.current_camera_info = self.camera_setting.camera_setting_list
            SettingPageFunctions.close_camera_setting(self)
            SettingPageFunctions.save_camera_setting(self)
        # Cancel choose camera btn
        if btn.objectName() == "pbtn_cancel_camera_setting":
            SettingPageFunctions.close_camera_setting(self)


        # TASK WINDOW BTN
        # ///////////////////////////////////////////////////////////////

        # Close btns
        if btn.objectName() == "tasks_btn_exit" or btn.objectName() == "tasks_pbtn_exit":
            if hasattr(self, 'task_window_ui'):
                self.task_window_ui.hide()
                del self.task_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)


        # TEST WINDOW BTN
        # ///////////////////////////////////////////////////////////////

        # Close btns
        if btn.objectName() == "test_updrs_btn_exit" or btn.objectName() == "test_updrs_pbtn_exit":
            if hasattr(self, 'test_updrs_window_ui'):
                self.test_updrs_window_ui.hide()
                del self.test_updrs_window_ui
        if btn.objectName() == "test_updrs_pbtn_save":
            if hasattr(self, 'test_updrs_window_ui'):
                self.test_updrs_window_ui.hide()
                del self.test_updrs_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)

        if btn.objectName() == "test_pdq39_btn_exit" or btn.objectName() == "test_pdq39_pbtn_exit":
            if hasattr(self, 'test_pdq39_window_ui'):
                self.test_pdq39_window_ui.hide()
                del self.test_pdq39_window_ui
        if btn.objectName() == "test_pdq39_pbtn_save":
            if hasattr(self, 'test_pdq39_window_ui'):
                self.test_pdq39_window_ui.hide()
                del self.test_pdq39_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)

        if btn.objectName() == "test_hads_btn_exit" or btn.objectName() == "test_hads_pbtn_exit":
            if hasattr(self, 'test_hads_window_ui'):
                self.test_hads_window_ui.hide()
                del self.test_hads_window_ui
        if btn.objectName() == "test_hads_pbtn_save":
            if hasattr(self, 'test_hads_window_ui'):
                self.test_hads_window_ui.hide()
                del self.test_hads_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)

        if btn.objectName() == "test_swen_btn_exit" or btn.objectName() == "test_swen_pbtn_exit":
            if hasattr(self, 'test_swen_window_ui'):
                self.test_swen_window_ui.hide()
                del self.test_swen_window_ui
        if btn.objectName() == "test_swen_pbtn_save":
            if hasattr(self, 'test_swen_window_ui'):
                self.test_swen_window_ui.hide()
                del self.test_swen_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)

        if btn.objectName() == "test_hanyar_btn_exit" or btn.objectName() == "test_hanyar_pbtn_exit":
            if hasattr(self, 'test_hanyar_window_ui'):
                self.test_hanyar_window_ui.hide()
                del self.test_hanyar_window_ui
        if btn.objectName() == "test_hanyar_pbtn_save":
            if hasattr(self, 'test_hanyar_window_ui'):
                self.test_hanyar_window_ui.hide()
                del self.test_hanyar_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)

        if btn.objectName() == "test_fab_btn_exit" or btn.objectName() == "test_fab_pbtn_exit":
            if hasattr(self, 'test_fab_window_ui'):
                self.test_fab_window_ui.hide()
                del self.test_fab_window_ui
        if btn.objectName() == "test_fab_pbtn_save":
            if hasattr(self, 'test_fab_window_ui'):
                self.test_fab_window_ui.hide()
                del self.test_fab_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)

        if btn.objectName() == "test_psqi_btn_exit" or btn.objectName() == "test_psqi_pbtn_exit":
            if hasattr(self, 'test_psqi_window_ui'):
                self.test_psqi_window_ui.hide()
                del self.test_psqi_window_ui
        if btn.objectName() == "test_psqi_pbtn_save":
            if hasattr(self, 'test_psqi_window_ui'):
                self.test_psqi_window_ui.hide()
                del self.test_psqi_window_ui
            TestTaskPageFunctions.update_screenplay_list(self)


        #EMPTY BUTTONS
        if btn.objectName() in ["link_get_pnexpert_account",
                                "link_go_to_result_day_activity_subpage_3",
                                "pbtn_diagnostic_result",
                                "pbtn_therapy",
                                "pbtn_results",
                                "pbtn_outpatient_card",
                                "link_go_to_result_day_activity_subpage_4"]:
            msg = PyMessageBox(self,
                               mode = 'information',
                               text_message='Для данной кнопки пока нет функции.\nМы работаем над этим.',
                               button_yes_text='Ok',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
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

        #DEBUG
        #print(f"Button {btn.objectName()}, released!")


    # RESIZE EVENT
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        SetupMainWindow.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition().toPoint()


    def closeEvent(self, event):
        if hasattr(self, 'save_flag') and self.save_flag:
            if hasattr(self, 'login_main'):
                self.login_main.close()
            event.accept()
        else:
            msg = PyMessageBox(self,
                               mode = 'question',
                               text_message='Вы действительно хотите выйти?',
                               button_yes_text='Да',
                               button_no_text='Нет',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
            msg.yes.connect(lambda: SetupClosing.setup_close(self))
            msg.show()
            event.ignore()


    def eventFilter(self, source, event):
        if hasattr(self, 'ledit_patient_date_of_birth') and source == self.ledit_patient_date_of_birth.line_edit and event.type() == QEvent.MouseButtonPress:
            self.ledit_patient_date_of_birth.line_edit.setFocus(Qt.MouseFocusReason)
            self.ledit_patient_date_of_birth.setCursorPosition(0)
            return True
        if hasattr(self, 'ledit_patient_passport') and source == self.ledit_patient_passport.line_edit and event.type() == QEvent.MouseButtonPress:
            self.ledit_patient_passport.line_edit.setFocus(Qt.MouseFocusReason)
            self.ledit_patient_passport.setCursorPosition(0)
            return True
        if hasattr(self, 'ledit_patient_snils') and source == self.ledit_patient_snils.line_edit and event.type() == QEvent.MouseButtonPress:
            self.ledit_patient_snils.line_edit.setFocus(Qt.MouseFocusReason)
            self.ledit_patient_snils.setCursorPosition(0)
            return True
        if hasattr(self, 'ledit_date_of_diagnos') and source == self.ledit_date_of_diagnos.line_edit and event.type() == QEvent.MouseButtonPress:
            self.ledit_date_of_diagnos.line_edit.setFocus(Qt.MouseFocusReason)
            self.ledit_date_of_diagnos.setCursorPosition(0)
            return True
        if hasattr(self, 'ledit_phone') and source == self.ledit_phone.line_edit and event.type() == QEvent.MouseButtonPress:
            self.ledit_phone.line_edit.setFocus(Qt.MouseFocusReason)
            self.ledit_phone.setCursorPosition(0)
            return True
        return super().eventFilter(source, event)


# SETTINGS WHEN TO START
# Set the initial class and also additional parameters of the "QApplication" class
# ///////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # APPLICATION
    # ///////////////////////////////////////////////////////////////
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon_neurology.ico"))
    #window = StartLoginWindow()
    window = MainWindow()

    # EXEC APP
    # ///////////////////////////////////////////////////////////////
    sys.exit(app.exec())