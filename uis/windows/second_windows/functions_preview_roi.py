# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
import numpy as np

from import_core import *

from core.functions import Functions

from core.functions_database import *
from core.functions_data_process import *
from .ui_preview_calibrate import *

class CameraConnectThread(QThread):
    camera = Signal(object)
    connect_flag = Signal(str)

    def __init__(self, parent=None, camera=None):
        super().__init__(parent)
        self.current_camera = camera
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
                #self.cap_camera = cv2.VideoCapture(0)
                if self.cap_camera.isOpened():
                    self.camera.emit(self.cap_camera)
                    self.connect_flag.emit('end_connect')
                else: self.connect_flag.emit('error_connect')
            else: self.connect_flag.emit('error_connect')
        except Exception as e:
            print(e)
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

        self.model = YOLO("yolov8n_fish_trained.pt")

    def run(self):
        self.stopped = False
        while(not self.stopped):
            if self.cmd == 'start_stream':
                self.start_streamming()
            elif self.cmd == 'stop_thread':
                self.stop_stream()
                self.stopped = True
                self.stream.release()
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
        self.isStreamming = False

    def start_stream(self):
        self.cmd = 'start_stream'

    def stop_stream(self):
        self.cmd = ''
        self.streamming_stopped = True

    def stop(self):
        self.cmd = 'stop_thread'

# FUNCTIONS
class PreviewRoiFunctions():
    def __init__(self):
        super().__init__()

    def setup_video_input(self):
        def camera_connect_connect_flag(flag):
            if flag == 'start_connect':
                self.wait_progress_camera.show()
                self.scaled_size = (600, 600)
            elif flag == 'end_connect':
                self.wait_progress_camera.hide()
            elif flag == 'error_connect':
                self.wait_progress_camera.hide()
                msg = PyMessageBox(self,
                                   mode='warning',
                                   text_message='Невозможно подключиться к камере!',
                                   button_yes_text='Ok',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
                msg.l_message.setWordWrap(False)
                msg.show()

        def camera_connect_camera(camera):
            self.camera = camera
            if self.camera_thread.isStreamming:
                self.camera_thread.stop_stream()
            self.camera_thread.current_camera = self.current_camera
            self.camera_thread.stream = self.camera
            self.camera_thread.start_stream()

        def camera_thread_rawFrame(frame):
            if not self.camera_thread.streamming_stopped:
                PreviewRoiFunctions.update_preview(self, frame)

        self.camera_connect_thread = CameraConnectThread(camera=self.current_camera)
        self.camera_connect_thread.connect_flag.connect(camera_connect_connect_flag)
        self.camera_connect_thread.camera.connect(camera_connect_camera)
        self.camera_connect_thread.start()
        self.camera_thread = VideoGetThread(self)
        self.camera_thread.rawFrame.connect(camera_thread_rawFrame)
        self.camera_thread.start()

    def stop_video_processing_threads(self):
        self.camera_thread.stop()
        self.camera_connect_thread.stop()
        self.camera_thread.terminate()
        self.camera_connect_thread.terminate()

    def update_preview(self, frame):
        if self.calib_en and self.current_camera['calib_params']:
            dst = cv2.undistort(frame,
                                np.array(self.current_camera['calib_params']['old_matrix']),
                                np.array(self.current_camera['calib_params']['old_distortion']),
                                None,
                                np.array(self.current_camera['calib_params']['new_matrix']))
            x, y, w, h = self.current_camera['calib_params']['roi']
            dst = dst[y:y+h, x:x+w].copy()
            h, w, _ = dst.shape
            frame_ratio = w / h
            self.l_preview.setPixmap(PreviewRoiFunctions.convert_cv_to_pixmap(dst).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio))
        else:
            h, w, _ = frame.shape
            frame_ratio = w / h
            self.l_preview.setPixmap(PreviewRoiFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio))

    def convert_cv_to_pixmap(frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame, w, h,bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        return pixmap





































