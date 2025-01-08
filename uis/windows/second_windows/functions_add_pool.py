# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.functions import Functions

from core.functions_database import *

# FUNCTIONS
class AddPoolFunctions():
    def __init__(self):
        super().__init__()

    def __del__(self):
        pass

    # SAVE CHANGES ABOUT STAFF TO DATABASE
    def add_pool(self):
        if not self.ledit_name.text():
            self.ledit_name.setFocus()
            return False
        if self.ledit_koef_v.text():
            try:
                koef_v = float(self.ledit_koef_v.text())
            except:
                self.ledit_koef_v.clear()
                self.ledit_koef_v.setFocus()
                return False
        if not self.ledit_video_source.text():
            self.ledit_video_source.setFocus()
            return False

        if not self.ledit_roi_x.text():
            self.ledit_roi_x.setFocus()
            return False
        if not self.ledit_roi_y.text():
            self.ledit_roi_y.setFocus()
            return False
        if not self.ledit_roi_w.text():
            self.ledit_roi_w.setFocus()
            return False
        if not self.ledit_roi_h.text():
            self.ledit_roi_h.setFocus()
            return False

        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='pools')
        if data[0] and data[1]:
            max_id = max([int(item['pool_id'].split('_')[-1]) for item in data[1]])
            pool_id = f'pool_{max_id + 1}'
        else: pool_id = 'pool_1'
        column_list = ['pool_id',
                       'pool_name',
                       'pool_comments',
                       'koef_v']
        value_list = [pool_id,
                      self.ledit_name.text(),
                      self.ledit_comments.toPlainText(),
                      str(koef_v) if self.ledit_koef_v.text() else '1.0']
        data = DatabaseFunctions.insert_data(database=COMMON_DATABASE_PATH,
                                             table='pools',
                                             column_list=column_list,
                                             value_list=value_list)
        if not data: return False

        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='cameras')
        if data[0] and data[1]:
            max_id = max([int(item['camera_id'].split('_')[-1]) for item in data[1]])
            camera_id = f'camera_{max_id + 1}'
        else: camera_id = 'camera_1'
        column_list = ['camera_id',
                       'camera_name',
                       'camera_address',
                       'camera_roi',
                       'calib_matrix',
                       'pool_id']
        value_list = [camera_id,
                      self.ledit_name_video_source.text(),
                      self.ledit_video_source.text(),
                      json.dumps({"x": int(self.ledit_roi_x.text()), "y": int(self.ledit_roi_y.text()), "w": int(self.ledit_roi_w.text()), "h": int(self.ledit_roi_h.text())}),
                      '',
                      pool_id]
        data = DatabaseFunctions.insert_data(database=COMMON_DATABASE_PATH,
                                             table='cameras',
                                             column_list=column_list,
                                             value_list=value_list)
        if not data:
            data = DatabaseFunctions.delete_data(database=COMMON_DATABASE_PATH,
                                                table='pools',
                                                where='pool_id',
                                                value=pool_id)
            return False
        return True



