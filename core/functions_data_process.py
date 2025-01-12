# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from config.file_path import *
from core.functions import *


# LOAD UI MAIN
# ///////////////////////////////////////////////////////////////
from uis.windows.main_window.ui_main import *

class PredictProcessThread(QThread):
    predictedData = Signal(dict)
    predict_flag = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model_source = f"{MODELS_PATH}\\{self.parent.settings['segmentation_model']['default']['source']}"
        self.predict_param = {'conf': self.parent.settings['segmentation_model']['default']['conf'],
                              'verbose': self.parent.settings['segmentation_model']['default']['verbose'],
                              'augment': self.parent.settings['segmentation_model']['default']['augment'],
                              'device': self.parent.settings['segmentation_model']['default']['device']}
        self.model = YOLO(self.model_source)
        self.frame = None
        self.first_predicted = False

    def run(self):
        if self.frame.size:
            img = self.frame.copy()
            shapes = np.zeros_like(self.frame, np.uint8)
            mask = shapes.astype(bool)
            alpha = 0.7
            results = self.model.predict(source=self.frame,
                                    conf=self.predict_param['conf'],
                                    verbose=self.predict_param['verbose'],
                                    augment=self.predict_param['augment'],
                                    device=self.predict_param['device'])
            masks = results[0].masks
            if masks:
                conf_arr = np.array(results[0].boxes.conf.tolist())
                arr = np.array([])
                for idx, contur in enumerate(masks.xy):
                    arr = np.append(arr, round(cv2.contourArea(contur)))
                cv2.fillPoly(shapes, [x.astype(int) for x in masks.xy], (255,150,200))
                img = cv2.addWeighted(self.frame, alpha, shapes, 1 - alpha, 0)
                self.predictedData.emit({'frame': img,'conf_arr': conf_arr, 'area_arr': arr})
            else: self.predictedData.emit({'frame': img,'conf_arr': None, 'area_arr': None})
            if not self.first_predicted:
                self.predict_flag.emit('end_predict')
                self.first_predicted = True
        else:
            self.predict_flag.emit('error_predict')
            self.predictedData.emit(None)

    def change_model(self, source=None):
        if source:
            self.model = YOLO(f"{MODELS_PATH}\\{source}")

    def change_predict_param(self, predict_param=None):
        if predict_param:
            if 'conf' in predict_param:
                self.predict_param['conf'] = predict_param['conf']
            if 'verbose' in predict_param:
                self.predict_param['verbose'] = predict_param['verbose']
            if 'augment' in predict_param:
                self.predict_param['augment'] = predict_param['augment']

    def reset(self):
        self.first_predicted = False

class DataProcessFunctions():
    def __init__(self):
        super().__init__()

    def split_arr1_by_arr2(arr_1, arr_2):
        lst = []
        for x in arr_2:
            lst.append(arr_1[:x])
            arr_1 = arr_1[x:]
        return lst

    def filtered_list_by_min_max(lst, min, max):
        return [[y for y in x if y >= min and y <= max] for x in lst]

    def filtered_index_list_by_min_max(lst, min, max):
        return [[idx for idx, y in enumerate(x) if y >= min and y <= max] for x in lst]

    def filtered_compare(lst1, lst2):
        return [x for idx, x in enumerate(lst1) if len(lst1[idx]) == len(lst2[idx])]

    def list_to_1D_array(lst):
        return np.array([y for x in lst for y in x])

    def compile_pdf_max(arr, unique=False):
        mn = np.min(arr)
        mx = np.max(arr)
        if unique:
            unique_arr = np.unique(arr)
            if unique_arr.size < 1000:
                kde_xs = np.linspace(mn, mx, unique_arr.size)
            else:
                kde_xs = np.linspace(mn, mx, 1000)
        else:
            if arr.size < 1000:
                kde_xs = np.linspace(mn, mx, arr.size)
            else:
                kde_xs = np.linspace(mn, mx, 1000)
        kde = st.gaussian_kde(arr)
        return round(kde_xs[kde.pdf(kde_xs).argmax()])

    def compile_qty(area_arr, area_num_arr):
        pdf_max_area_arr = DataProcessFunctions.compile_pdf_max(area_arr)
        spl = DataProcessFunctions.split_arr1_by_arr2(area_arr, area_num_arr)
        #fil_index = DataProcessFunctions.filtered_index_list_by_min_max(spl, pdf_max_area_arr * 0.7, pdf_max_area_arr * 1.3)
        fil_min_max = DataProcessFunctions.filtered_list_by_min_max(spl, pdf_max_area_arr * 0.8, pdf_max_area_arr * 1.2)
        #arr_size = np.array([len(x) for x in fil_index])
        arr_size_compare = np.array([len(x) for x in DataProcessFunctions.filtered_compare(spl, fil_min_max)])
        '''print(f"max_pdf_simple: {DataProcessFunctions.compile_pdf_max(area_num_arr, unique=True)} "
              f"max_pdf_filt_min_max: {DataProcessFunctions.compile_pdf_max(arr_size, unique=True)} "
              f"max_size_filt_min_max:{np.max(arr_size)} "
              f"max_pdf_filt_compare: {DataProcessFunctions.compile_pdf_max(arr_size_compare, unique=True)} "
              f"max_filt_compare: {np.max(arr_size_compare)} "
              f"min_filt_compare: {np.min(arr_size_compare)} "
              f"mean_filt_compare: {np.mean(arr_size_compare)}")'''
        return np.max(arr_size_compare)




