# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.functions import Functions

from core.functions_database import *

STYLE_FIELD_GREEN = '''
    QLabel {
        font-family: 'Segoe UI';
        font-style: normal;
        font-weight: 500;
        font-size: 12px;
        line-height: 16px;
        color: green;
    }
    '''

STYLE_FIELD_RED = '''
    QLabel {
        font-family: 'Segoe UI';
        font-style: normal;
        font-weight: 500;
        font-size: 12px;
        line-height: 16px;
        color: red;
    }
    '''

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
        calib_params = json.dumps(self.calib_params) if self.calib_params else ''
        column_list = ['camera_id',
                       'camera_name',
                       'camera_address',
                       'camera_roi',
                       'calib_params',
                       'calib_enable',
                       'pool_id']
        value_list = [camera_id,
                      self.ledit_name_video_source.text(),
                      self.ledit_video_source.text(),
                      json.dumps({"x": int(self.ledit_roi_x.text()), "y": int(self.ledit_roi_y.text()), "w": int(self.ledit_roi_w.text()), "h": int(self.ledit_roi_h.text())}),
                      calib_params,
                      str(self.tbtn_calib_en.isChecked()),
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

    # EDIT CHANGES
    def edit_pool(self):
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
        else: pool_id = 'pool_1'
        column_list = ['pool_name',
                       'pool_comments',
                       'koef_v']
        value_list = [self.ledit_name.text(),
                      self.ledit_comments.toPlainText(),
                      str(koef_v) if self.ledit_koef_v.text() else '1.0']
        data = DatabaseFunctions.update_data(database=COMMON_DATABASE_PATH,
                                             table='pools',
                                             column_list=column_list,
                                             value_list=value_list,
                                             where_column='pool_id',
                                             where_value=self.parent.current_pool_page_3['id'])
        if not data: return False
        calib_params = json.dumps(self.calib_params) if self.calib_params else ''
        column_list = ['camera_name',
                       'camera_address',
                       'camera_roi',
                       'calib_params',
                       'calib_enable']
        value_list = [self.ledit_name_video_source.text(),
                      self.ledit_video_source.text(),
                      json.dumps({"x": int(self.ledit_roi_x.text()), "y": int(self.ledit_roi_y.text()), "w": int(self.ledit_roi_w.text()), "h": int(self.ledit_roi_h.text())}),
                      calib_params,
                      str(self.tbtn_calib_en.isChecked())]
        data = DatabaseFunctions.update_data(database=COMMON_DATABASE_PATH,
                                             table='cameras',
                                             column_list=column_list,
                                             value_list=value_list,
                                             where_column='camera_id',
                                             where_value=self.current_camera['camera_id'])
        return True

    def fill_edit_data(self):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='pools',
                                             where='pool_id',
                                             value=self.parent.current_pool_page_3['id'])
        self.ledit_name.setText(data[1][0]['pool_name'])
        self.ledit_comments.setPlainText(data[1][0]['pool_comments'])
        self.ledit_koef_v.setText(data[1][0]['koef_v'])

        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='cameras',
                                             where='camera_id',
                                             value=self.current_camera['camera_id'])

        self.ledit_name_video_source.setText(data[1][0]['camera_name'])
        self.ledit_video_source.setText(data[1][0]['camera_address'])
        roi = json.loads(data[1][0]['camera_roi'])
        if roi:
            self.ledit_roi_x.setText(str(roi['x']))
            self.ledit_roi_y.setText(str(roi['y']))
            self.ledit_roi_w.setText(str(roi['w']))
            self.ledit_roi_h.setText(str(roi['h']))

    def update_calib_status(self):
        if self.mode == 'edit':
            data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                 table='cameras',
                                                 where='camera_id',
                                                 value=self.current_camera['camera_id'])
            if data[0] and data[1]:
                if data[1][0]['calib_params']:
                    self.calib_params = json.loads(data[1][0]['calib_params'])
                    self.l_calib_status.setText(QCoreApplication.translate("Label", u"откалибровано", None))
                    self.l_calib_status.setStyleSheet(STYLE_FIELD_GREEN)
                    self.tbtn_calib_en.setEnabled(True)
                else:
                    self.l_calib_status.setText(QCoreApplication.translate("Label", u"не откалибровано", None))
                    self.l_calib_status.setStyleSheet(STYLE_FIELD_RED)
                    self.tbtn_calib_en.setEnabled(False)
                    self.tbtn_calib_en.setChecked(False)
                if data[1][0]['calib_enable'] == 'True':
                    self.tbtn_calib_en.setChecked(True)
                elif data[1][0]['calib_enable'] == 'False':
                    self.tbtn_calib_en.setChecked(False)
        elif self.mode == 'add':
            self.l_calib_status.setText(QCoreApplication.translate("Label", u"не откалибровано", None))
            self.l_calib_status.setStyleSheet(STYLE_FIELD_RED)
            self.tbtn_calib_en.setEnabled(False)
            self.tbtn_calib_en.setChecked(False)

    def update_calib_params(self, params):
        self.calib_params = params
        self.l_calib_status.setText(QCoreApplication.translate("Label", u"откалибровано", None))
        self.l_calib_status.setStyleSheet(STYLE_FIELD_GREEN)
        self.tbtn_calib_en.setEnabled(True)






