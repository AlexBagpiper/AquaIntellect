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
                #self.cap_camera = cv2.VideoCapture(0)
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
class CameraCalibrateFunctions():
    def __init__(self):
        super().__init__()

    def set_chessboard_size(self, size):
        self.CHECKERBOARD = (size[0], size[1])
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0] * self.CHECKERBOARD[1], 3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0], 0:self.CHECKERBOARD[1]].T.reshape(-1, 2)

    def set_calib_val(self):
        self.threedpoints = []
        self.twodpoints = []
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0] * self.CHECKERBOARD[1], 3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0], 0:self.CHECKERBOARD[1]].T.reshape(-1, 2)

    def find_corners(self, frame):
        if frame.size:
            img = frame.copy()
            grayColor = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(grayColor,
                                                     self.CHECKERBOARD,
                                                     cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
            if ret:
                self.corners = cv2.cornerSubPix(grayColor, corners, (11, 11), (-1, -1), self.criteria)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_corners = cv2.cvtColor(grayColor, cv2.COLOR_GRAY2RGB)
                cv2.drawChessboardCorners(img_corners,
                                          self.CHECKERBOARD,
                                          self.corners,
                                          ret)
                return {'orig_image': img, 'cornered_image': img_corners}
            return False

    def add_last_points(self):
        self.threedpoints.append(self.objectp3d)
        self.twodpoints.append(self.corners)

    def get_calib_param(frame, threedpoints, twodpoints, img_size):
        ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(threedpoints, twodpoints, img_size, None, None)
        return {'ret': ret, 'matrix': matrix, 'distortion': distortion, 'r_vecs': r_vecs, 't_vecs': t_vecs}

    def get_calib_image(frame, matrix, distortion):
        h, w = frame.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w, h), 1, (w, h))
        dst = cv2.undistort(frame, matrix, distortion, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        return dst

    def grab_frame(self):
        if self.ledit_side_0.text() and self.ledit_side_1.text():
            size = [3 if int(self.ledit_side_0.text()) < 3 else int(self.ledit_side_0.text()),
                    3 if int(self.ledit_side_1.text()) < 3 else int(self.ledit_side_1.text())]
            CameraCalibrateFunctions.set_chessboard_size(self, size)
        self.corners_dict = CameraCalibrateFunctions.find_corners(self, self.raw_frame)
        if self.corners_dict:
            self.camera_thread.stop_stream()
            CameraCalibrateFunctions.update_camera_thread(self, self.corners_dict['cornered_image'])
            self.pbtn_accept.show()
            self.pbtn_reject.show()
        else:
            self.l_ungrabbed.show()
            self.current_timer = QTimer()
            self.current_timer.timeout.connect(lambda: self.l_ungrabbed.hide())
            self.current_timer.setSingleShot(True)
            self.current_timer.start(500)

    def accept_grab(self):
        CameraCalibrateFunctions.add_last_points(self)
        self.camera_thread.start_stream()
        self.pbtn_accept.hide()
        self.pbtn_reject.hide()
        self.l_grab_frames.setText(str(len(self.twodpoints)))
        self.pbtn_compile.show()
        self.pbtn_reset.show()

    def reject_grab(self):
        self.camera_thread.start_stream()
        self.pbtn_accept.hide()
        self.pbtn_reject.hide()

    def compile_param(self):
        try:
            h, w = self.raw_frame.shape[:2]
            ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(self.threedpoints, self.twodpoints, (w, h), None, None)
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w, h), 1, (w, h))
            self.calib_params = {'old_matrix': matrix.tolist(), 'old_distortion': distortion.tolist(), 'new_matrix': newcameramtx.tolist(), 'roi': roi}
            self.pbtn_save.show()
            self.pbtn_preview.show()
            self.pbtn_compile.hide()
            return True
        except Exception as e:
            print(e)
            return False

    def preview(self):
        self.preview_calibrated_ui = UI_PreviewCalibrate(self, self.raw_frame, self.calib_params)
        self.preview_calibrated_ui.show()

    def reset(self):
        self.l_grab_frames.setText('')
        self.pbtn_save.hide()
        self.pbtn_compile.hide()
        self.pbtn_preview.hide()
        self.pbtn_reset.hide()
        self.pbtn_accept.hide()
        self.pbtn_reject.hide()
        CameraCalibrateFunctions.set_calib_val(self)
        if not self.camera_thread.isStreamming: self.camera_thread.start_stream()

    def save(self):
        self.save.emit(self.calib_params)
        '''self.current_camera.update({'calib_params': json.dumps(self.calib_params)})
        column_list = [x for x in self.current_camera.keys()]
        value_list = [x for x in self.current_camera.values()]
        data = DatabaseFunctions.update_data(database=COMMON_DATABASE_PATH,
                                             table='cameras',
                                             column_list=column_list,
                                             value_list=value_list,
                                             where_column='camera_id',
                                             where_value=self.current_camera['camera_id'])'''
        CameraCalibrateFunctions.reset(self)

    def setup_video_input(self):
        def camera_connect_connect_flag(flag):
            if flag == 'start_connect':
                self.pbtn_grab.setEnabled(False)
                self.wait_progress_camera.show()
                self.scaled_size = (600, 600)
            elif flag == 'end_connect':
                self.wait_progress_camera.hide()
                self.pbtn_grab.setEnabled(True)
            elif flag == 'error_connect':
                #self.btn_camera_preview.show()
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
                CameraCalibrateFunctions.update_camera_thread(self, frame)

        self.camera_connect_thread = CameraConnectThread()
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

    def change_camera(self):
        self.camera_connect_thread.current_camera = self.current_camera

    def update_preview(self, frame):
        scene_ratio = self.scene.sceneRect().width() / self.scene.sceneRect().height()
        h, w, _ = frame.shape
        frame_ratio = w / h
        if abs(scene_ratio - frame_ratio) / scene_ratio > 0.1:
            self.l_preview.setPixmap(CameraCalibrateFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio, Qt.KeepAspectRatio))
        else:
            self.l_preview.setPixmap(CameraCalibrateFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio))

    def convert_cv_to_pixmap(frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame, w, h,bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        return pixmap

    def update_camera_thread(self, frame, grab=False):
        if grab: print(grab)
        self.raw_frame = frame.copy()
        CameraCalibrateFunctions.update_preview(self, self.raw_frame)




































