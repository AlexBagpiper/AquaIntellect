# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
import numpy as np

from import_core import *

from core.functions import Functions

from core.functions_database import *
from core.functions_data_process import *


class TimerThread(QThread):
    timerTic = Signal()

    def __init__(self, parent=None, mode='continuous', timer_tic=None):
        super().__init__(parent)
        self.mode = mode
        self.timer_tic = timer_tic
        self.stopped = False

    def run(self):
        if self.mode == 'continuous':
            while not self.stopped:
                time.sleep(self.timer_tic)
                self.timerTic.emit()
        elif self.mode == 'single':
            if not self.stopped:
                time.sleep(self.timer_tic)
                self.timerTic.emit()

    def stop(self):
        self.stopped = True


class CameraConnectThread(QThread):
    camera = Signal(object)
    connect_flag = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_camera = None
        self.stopped = False
        self.cmd = ''

    def run(self):
        self.stopped = False
        while(not self.stopped):
            if self.cmd == 'connect':
                self.camera_connect()
            elif self.cmd == 'disconnect':
                self.camera_disconnect()
            elif self.cmd == 'stop':
                self.camera_disconnect()
                self.stopped = True
            time.sleep(0.1)

    def camera_connect(self):
        self.cmd = ''
        try:
            if self.current_camera['camera_address']:
                self.connect_flag.emit('start_connect')
                if hasattr(self, 'cap_camera') and self.cap_camera.isOpened():
                    self.cap_camera.release()
                self.cap_camera = cv2.VideoCapture(self.current_camera['camera_address'], cv2.CAP_FFMPEG)
                if self.cap_camera.isOpened():
                    self.camera.emit(self.cap_camera)
                    self.connect_flag.emit('end_connect')
                else: self.connect_flag.emit('error_connect')
            else: self.connect_flag.emit('error_connect')
        except Exception as e:
            self.connect_flag.emit('error_connect')

    def camera_disconnect(self):
        self.cmd = ''
        try:
            self.connect_flag.emit('start_disconnect')
            if hasattr(self, 'cap_camera') and self.cap_camera.isOpened():
                self.cap_camera.release()
                self.connect_flag.emit('end_disconnect')
            else: self.connect_flag.emit('error_disconnect')
        except Exception as e:
            self.connect_flag.emit('error_disconnect')

    def cam_connect(self):
        self.cmd = 'connect'

    def cam_disconnect(self):
        self.cmd = 'disconnect'

    def stop(self):
        self.cmd = 'stop'


class VideoGetThread(QThread):
    rawFrame = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.cmd = ''
        self.isStreamming = False
        self.stream = None
        self.current_camera = None
        self.streamming_stopped = False
        self.stopped = False

    def run(self):
        self.stopped = False
        while(not self.stopped):
            if self.cmd == 'start_stream':
                self.start_streamming()
            elif self.cmd == 'stop_thread':
                self.stop_stream()
                self.stopped = True
            time.sleep(0.1)

    def start_streamming(self):
        self.cmd = ''
        self.isStreamming = True
        self.streamming_stopped = False
        self.scaled_size = None
        camera_roi = None
        if self.current_camera: camera_roi = self.current_camera['camera_roi']
        if camera_roi:
            camera_roi = json.loads(camera_roi)
            self.scaled_size = [camera_roi['x'], camera_roi['y'], camera_roi['x'] + camera_roi['w'], camera_roi['y'] + camera_roi['h']]
        while self.stream.isOpened() and not self.streamming_stopped:
            try:
                (self.grabbed, frame) = self.stream.read()
                h, w, ch = frame.shape
                if self.scaled_size and (h != self.scaled_size[1] or w != self.scaled_size[0]):
                    frame = frame[self.scaled_size[1]:self.scaled_size[3], self.scaled_size[0]:self.scaled_size[2]]
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.rawFrame.emit(self.frame)
            except Exception as e:
                print(e)
        self.stream.release()
        self.isStreamming = False

    def start_stream(self):
        self.cmd = 'start_stream'

    def stop_stream(self):
        self.cmd = ''
        self.streamming_stopped = True

    def stop(self):
        self.cmd = 'stop_thread'

# FUNCTIONS
class CompileVolBiomassFunctions():
    def __init__(self):
        super().__init__()

    def __del__(self):
        pass

    def start_compile(self):
        self.pbtn_start.setEnabled(False)
        self.area_arr = np.array([])
        self.conf_arr = np.array([])
        self.cur_area_arr = np.array([])
        self.cur_conf_arr = np.array([])
        self.is_compiling = True
        self.progress_val = 0
        self.cur_area_num = 0
        self.area_num_arr = np.array([], dtype=int)
        self.l_val_relative_volume.setText('')
        self.l_val_fish_qty.setText('')
        self.time_total = self.settings['num_data_to_compile_S'] * self.settings['timer_image_grab']
        self.l_time_remain.setText(QCoreApplication.translate("Label", u"Осталось 00:00", None))


    def stop_compile(self):
        self.pbtn_start.setEnabled(True)
        self.is_compiling = False
        self.l_val_relative_volume.setText(str(round(DataProcessFunctions.compile_pdf_max(self.area_arr) / float(self.current_pool['koef_v']))))
        self.l_val_fish_qty.setText(str(DataProcessFunctions.compile_qty(self.area_arr, self.area_num_arr)))
        #print(f'max_pdf: {self.l_val_relative_volume.text()} max_arr_size: {self.l_val_fish_qty.text()}')
        #CompileVolBiomassFunctions.start_compile(self)

    def setup_video_input(self):
        def camera_connect_connect_flag(flag):
            if flag == 'start_connect':
                self.pbtn_start.setEnabled(False)
                self.wait_progress_camera.show()
                self.scaled_size = (300, 300)
            elif flag == 'end_connect':
                pass
            elif flag == 'error_connect':
                self.pbtn_start.setEnabled(True)
                self.wait_progress_camera.hide()
                msg = PyMessageBox(self,
                                   mode='warning',
                                   text_message='Невозможно подключиться к камере!',
                                   button_yes_text='Ok',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
                msg.l_message.setWordWrap(False)
                msg.yes.connect(self.close)
                msg.show()
            elif flag == 'end_predict':
                self.pbtn_start.setEnabled(True)
                self.wait_progress_camera.hide()
            elif flag == 'error_predict':
                pass

        def camera_connect_camera(camera):
            self.camera = camera
            if self.camera_thread.isStreamming:
                self.camera_thread.stop_stream()
            self.camera_thread.current_camera = self.current_camera
            self.camera_thread.stream = self.camera
            self.camera_thread.start_stream()
            self.timer_predict.start()

        def camera_thread_rawFrame(frame):
            #CompileVolBiomassFunctions.update_camera_thread(self, frame)
            if not self.predict_thread.isRunning():
                self.predict_thread.frame = frame
                self.predict_thread.start()

        def predict_thread_predictedData(data):
            if data:
                CompileVolBiomassFunctions.update_camera_thread(self, data['frame'])
                self.cur_area_arr = data['area_arr']
                self.cur_conf_arr = data['conf_arr']

        def timer_predict_timerTic():
            CompileVolBiomassFunctions.increment_val(self)

        self.camera_connect_thread = CameraConnectThread()
        self.camera_connect_thread.connect_flag.connect(camera_connect_connect_flag)
        self.camera_connect_thread.camera.connect(camera_connect_camera)
        self.camera_connect_thread.current_camera = self.current_camera
        self.camera_connect_thread.start()
        self.camera_thread = VideoGetThread(self)
        self.camera_thread.rawFrame.connect(camera_thread_rawFrame)
        self.camera_thread.start()
        self.predict_thread = PredictProcessThread(self)
        self.predict_thread.predictedData.connect(predict_thread_predictedData)
        self.predict_thread.predict_flag.connect(camera_connect_connect_flag)
        self.timer_predict = TimerThread(self, timer_tic=self.settings['timer_image_grab'])
        self.timer_predict.timerTic.connect(timer_predict_timerTic)

    def stop_video_processing_threads(self):
        self.camera_thread.stop()
        self.camera_connect_thread.stop()
        self.camera_thread.terminate()
        self.camera_connect_thread.terminate()
        self.predict_thread.terminate()
        self.timer_predict.stop()
        self.timer_predict.terminate()

    def change_camera(self):
        self.camera_connect_thread.current_camera = self.current_camera

    def update_preview(self, frame):
        scene_ratio = self.scene.sceneRect().width() / self.scene.sceneRect().height()
        h, w, _ = frame.shape
        frame_ratio = w / h
        if abs(scene_ratio - frame_ratio) / scene_ratio > 0.1:
            self.l_preview.setPixmap(CompileVolBiomassFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio, Qt.KeepAspectRatio))
        else:
            self.l_preview.setPixmap(CompileVolBiomassFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio))

    def convert_cv_to_pixmap(frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame, w, h,bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        return pixmap

    def update_camera_thread(self, frame):
        self.raw_frame = frame.copy()
        CompileVolBiomassFunctions.update_preview(self, self.raw_frame)

    def increment_val(self):
        if hasattr(self, 'is_compiling') and self.is_compiling:
            self.progress_val += 1
            seconds = int(self.time_total - self.time_total * self.progress_val / self.settings['num_data_to_compile_S'])
            minutes, seconds = divmod(seconds, 60)
            self.l_time_remain.setText(QCoreApplication.translate("Label", f"Осталось {minutes:02d}:{seconds:02d}", None))
            if self.cur_area_arr.size:
                self.area_arr = np.append(self.area_arr, self.cur_area_arr)
                self.cur_area_num = self.cur_area_arr.size
                self.area_num_arr =np.append(self.area_num_arr, self.cur_area_num)
            if self.cur_conf_arr.size:
                self.conf_arr = np.append(self.conf_arr, self.cur_conf_arr)
            if self.progress_val <= self.settings['num_data_to_compile_S']:
                self.circular_progress.set_value(round(100*self.progress_val/self.settings['num_data_to_compile_S']))
            else:
                CompileVolBiomassFunctions.stop_compile(self)














































