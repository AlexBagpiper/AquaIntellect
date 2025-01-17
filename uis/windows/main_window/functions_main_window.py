# -*- coding: utf-8 -*-

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.functions_database import *
from . ui_main import *

# FUNCTIONS
class MainFunctions():
    def __init__(self):
        super().__init__()
        # SETUP MAIN WINDOw
        # Load widgets from "gui\uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

    # SET MAIN WINDOW PAGES
    # ///////////////////////////////////////////////////////////////
    def set_page(self, page):
        self.ui.load_pages.pages.setCurrentWidget(page)

    # SET LEFT COLUMN PAGES
    # ///////////////////////////////////////////////////////////////
    def set_left_column_menu(
        self,
        menu,
        title,
        icon_path
    ):
        self.ui.left_column.menus.menus.setCurrentWidget(menu)
        self.ui.left_column.title_label.setText(title)
        self.ui.left_column.icon.set_icon(icon_path)

    # RETURN IF LEFT COLUMN IS VISIBLE
    # ///////////////////////////////////////////////////////////////
    def left_column_is_visible(self):
        width = self.ui.left_column_frame.width()
        if width == 0:
            return False
        else:
            return True

    # RETURN IF RIGHT COLUMN IS VISIBLE
    # ///////////////////////////////////////////////////////////////
    def right_column_is_visible(self):
        width = self.ui.right_column_frame.width()
        if width == 0:
            return False
        else:
            return True

    # SET RIGHT COLUMN PAGES
    # ///////////////////////////////////////////////////////////////
    def set_right_column_menu(self, menu):
        self.ui.right_column.menus.setCurrentWidget(menu)

    # GET TITLE BUTTON BY OBJECT NAME
    # ///////////////////////////////////////////////////////////////
    def get_title_bar_btn(self, object_name):
        return self.ui.title_bar_frame.findChild(QPushButton, object_name)

    # GET TITLE BUTTON BY OBJECT NAME
    # ///////////////////////////////////////////////////////////////
    def get_left_menu_btn(self, object_name):
        return self.ui.left_menu.findChild(QPushButton, object_name)
    
    # LEDT AND RIGHT COLUMNS / SHOW / HIDE
    # ///////////////////////////////////////////////////////////////
    def toggle_left_column(self):
        # GET ACTUAL CLUMNS SIZE
        width = self.ui.left_column_frame.width()
        right_column_width = self.ui.right_column_frame.width()

        MainFunctions.start_box_animation(self, width, right_column_width, "left")

    def toggle_right_column(self):
        # GET ACTUAL CLUMNS SIZE
        left_column_width = self.ui.left_column_frame.width()
        width = self.ui.right_column_frame.width()

        MainFunctions.start_box_animation(self, left_column_width, width, "right")

    def start_box_animation(self, left_box_width, right_box_width, direction):
        right_width = 0
        left_width = 0
        time_animation = self.ui.settings["time_animation"]
        minimum_left = self.ui.settings["left_column_size"]["minimum"]
        maximum_left = self.ui.settings["left_column_size"]["maximum"]
        minimum_right = self.ui.settings["right_column_size"]["minimum"]
        maximum_right = self.ui.settings["right_column_size"]["maximum"]

        # Check Left Values        
        if left_box_width == minimum_left and direction == "left":
            left_width = maximum_left
        else:
            left_width = minimum_left

        # Check Right values        
        if right_box_width == minimum_right and direction == "right":
            right_width = maximum_right
        else:
            right_width = minimum_right       

        # ANIMATION LEFT BOX        
        self.left_box = QPropertyAnimation(self.ui.left_column_frame, b"minimumWidth")
        self.left_box.setDuration(time_animation)
        self.left_box.setStartValue(left_box_width)
        self.left_box.setEndValue(left_width)
        self.left_box.setEasingCurve(QEasingCurve.InOutQuart)

        # ANIMATION RIGHT BOX        
        self.right_box = QPropertyAnimation(self.ui.right_column_frame, b"minimumWidth")
        self.right_box.setDuration(time_animation)
        self.right_box.setStartValue(right_box_width)
        self.right_box.setEndValue(right_width)
        self.right_box.setEasingCurve(QEasingCurve.InOutQuart)

        # GROUP ANIMATION
        self.group = QParallelAnimationGroup()
        self.group.stop()
        self.group.addAnimation(self.left_box)
        self.group.addAnimation(self.right_box)
        self.group.start()

    def update_pools_list(self, page=1):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                   table='pools')
        if data[0] and data[1]:
            return [{"btn_id" : f"page_{page}__{item['pool_id']}",
                     "is_active": False,
                     "is_status_checked": False,
                     "text": item['pool_name']} for item in data[1]]
        else: return []

    def get_add_menu_parameters(self, pool_id, page=1):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='pools',
                                             where='pool_id',
                                             value=pool_id)
        if data[0] and data[1]:
            return [{"btn_id" : f"page_{page}__{ data[1][0]['pool_id']}",
                     "is_active": False,
                     "is_status_checked": False,
                     "text": data[1][0]['pool_name']}]
        else: return []

    def get_first_pool(self):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                   table='pools')
        if data[0] and data[1]:
            return {"id" : data[1][0]['pool_id'],
                    "text": data[1][0]['pool_name']}
        else: return {"id" : None,
                      "text": None}

    def set_current_pool(self, btn_id: str, page=1):
        if btn_id:
            data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                       table='pools',
                                                       where='pool_id',
                                                       value=btn_id.split('__')[-1])

            if data[0] and data[1]:
                if page == 1:
                    self.current_pool_page_1.update({"id" : data[1][0]['pool_id'],
                                              "text": data[1][0]['pool_name']})
                    self.left_menu_page_1.select_only_one(btn_id)
                elif page == 2:
                    pass
                elif page == 3:
                    self.current_pool_page_3.update({"id" : data[1][0]['pool_id'],
                                                     "text": data[1][0]['pool_name']})
                    self.left_menu_page_3.select_only_one(btn_id)
                return True
        else: return False

    def get_current_pool(self, page=1):
        if page == 1: return self.current_pool_page_1
        elif page == 2: pass
        elif page == 3: return self.current_pool_page_3

    def delete_pool(self, id: str):
        try:
            if id:
                data = DatabaseFunctions.delete_data(database=COMMON_DATABASE_PATH,
                                                     table='pools',
                                                     where='pool_id',
                                                     value=id)
                data1 = DatabaseFunctions.delete_data(database=COMMON_DATABASE_PATH,
                                                     table='cameras',
                                                     where='pool_id',
                                                     value=id)
                if data[0]:
                    self.left_menu_page_1.delete_menu(f'page_1__{id}')
                    if id == self.current_pool_page_1['id']:
                        self.current_pool_page_1.update(MainFunctions.get_first_pool(self))
                        MainFunctions.set_current_pool(self, self.current_pool_page_1['id'])
                    self.left_menu_page_3.delete_menu(f'page_3__{id}')
                    if id == self.current_pool_page_3['id']:
                        self.current_pool_page_3.update(MainFunctions.get_first_pool(self))
                        MainFunctions.set_current_pool(self, self.current_pool_page_3['id'], page=3)
                    return True
            else: return False
        except Exception as e:
            print(e)
            return False


