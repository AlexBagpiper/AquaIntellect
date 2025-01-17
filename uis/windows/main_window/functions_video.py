# -*- coding: utf-8 -*-

import time

import numpy as np

from import_core import *
from core.functions import Functions
from core.functions_database import *
from config.file_path import *
from uis.windows.main_window.functions_main_window import *


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

        self.model = YOLO("yolov8n_fish_trained.pt")

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
                #results = self.model(self.frame)
                #annotated_img = results[0].plot()
                #self.rawFrame.emit(annotated_img)
                self.rawFrame.emit(self.frame)
                '''yolo_outputs = self.model.predict(self.frame)
                output = yolo_outputs[0]
                box = output.boxes
                names = output.names
                print('**********************')
                for j in range(len(box)):
                    labels = names[box.cls[j].item()]
                    coordinates = box.xyxy[j].tolist()
                    confidence = np.round(box.conf[j].item(), 2)
                    print(f'In this image {len(box)} fish has been detected.')
                    print(f'Fish {j + 1} is: {labels}')
                    print(f'Coordinates are: {coordinates}')
                    print(f'Confidence is: {confidence}')
                    print('-------')'''
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
        

class FrameProcessThread(QThread):
    statParam = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame = None
        self.arr_data = np.array([], dtype=int)
        self.param_dict = {'max_pdf': 0, 'arr_data_size': 0, 'data_min': 0, 'data_max': 0}
        self.model = YOLO(f"{MODELS_PATH}\\{parent.settings['segmentation_model_default']}")

    def run(self):
        gray_image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        blurredImage = cv2.GaussianBlur(gray_image, (5, 5), 0)
        ret,thresh = cv2.threshold(blurredImage, 80, 255, cv2.THRESH_BINARY)
        #ret,thresh1 = cv2.threshold(blurredImage, 40, 255, cv2.THRESH_BINARY)
        height, width = thresh.shape[0], thresh.shape[1]
        mask = np.zeros(thresh.shape[:2], dtype="uint8")
        cv2.circle(mask, (int(height/2), int(width/2)), 240, 255, -1)
        mask = cv2.bitwise_not(mask)
        mask = cv2.bitwise_and(mask, cv2.circle(mask, (int(height/2), int(width/2)), 25, 255, -1))
        masked = cv2.bitwise_or(thresh, mask)

        # Find all pixels
        result = np.count_nonzero(masked==0)
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(masked, f'current: {result}',(10,50), font, 1,(100,100,100),2,cv2.LINE_AA)
        #cv2.putText(masked, f'averange: {avr}',(10,int(height) - 30), font, 0.5,(100,100,100),1,cv2.LINE_AA)
        #thresh1 = cv2.adaptiveThreshold(gray_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        self.arr_data = np.append(self.arr_data, result)
        mn = np.min(self.arr_data)
        mx = np.max(self.arr_data)
        self.param_dict.update({'arr_data_size': self.arr_data.size, 'data_min': mn, 'data_max': mx})        
        if self.arr_data.size > 1:
            if len(self.arr_data) < 1000:
                kde_xs = np.linspace(mn, mx, self.arr_data.size)
            else:
                kde_xs = np.linspace(mn, mx, 1000)
            kde = ScipyStats.gaussian_kde(self.arr_data)
            max_pdf = kde_xs[kde.pdf(kde_xs).argmax()]
            self.param_dict.update({'max_pdf': round(max_pdf)})
            #cv2.putText(masked, f'PDF: {round(max_pdf)}',(10,int(height) - 10), font, 0.5,(100,100,100),1,cv2.LINE_AA)
        self.statParam.emit(self.param_dict)    

    def clear(self):
        self.arr_data = np.array([], dtype=int)


class VideoWriteThread(QThread):
    status = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = None
        self.path = None
        self.frame = None
        self.frame_list = None
        self.frame_rate = None
        self.frame_counter = None
        self.codec = cv2.VideoWriter_fourcc('D','I','V','X')

        self.writer_complete = None
        self.writer_close = None

    def run(self):
        if self.mode == 'post_time':
            self.post_time_writer()
        elif self.mode == 'real_time':
            self.real_time_writer()


    def post_time_writer(self):
        H, W, CH = self.frame_list[0].shape
        self.post_time_writer_codec = cv2.VideoWriter(self.path, self.codec, self.frame_rate, (W, H))
        for idx, frame in enumerate(self.frame_list):
            self.post_time_writer_codec.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.writer_complete = round(100*idx/len(self.frame_list))
            self.status.emit(self.writer_complete)
        self.post_time_writer_codec.release()


    def real_time_writer(self):
        H, W, CH = self.frame.shape
        self.real_time_writer_codec = cv2.VideoWriter(self.path, self.codec, self.frame_rate, (W, H))
        while not self.writer_close:
            self.real_time_write_frame(self.frame)
        self.real_time_writer_codec.release()


    def real_time_write_frame(self, frame):
        start = time.perf_counter()
        self.real_time_writer_codec.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pause = self.frame_rate / 1000 - (time.perf_counter() - start)
        if pause > 0:
            time.sleep(pause)
        else:
            self.real_time_write_frame(frame)


class OneEuroFilter:
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.x_prev = float(x0)
        self.dx_prev = float(dx0)
        self.t_prev = float(t0)

    def __call__(self, t, x):
        t_e = t - self.t_prev
        a_d = self.smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = self.exponential_smoothing(a_d, dx, self.dx_prev)
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self.smoothing_factor(t_e, cutoff)
        x_hat = self.exponential_smoothing(a, x, self.x_prev)
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev


# FUNCTIONS
class VideoFunctions():
    def __init__(self):
        super().__init__()

    def __del__(self):
        pass

    def setup_video_input(self):
        def camera_connect_connect_flag(flag):
            if flag == 'start_connect':
                self.btn_camera_preview.hide()
                self.wait_progress_camera.show()
                self.scaled_size = (600, 600)
            elif flag == 'end_connect':
                self.wait_progress_camera.hide()
            elif flag == 'error_connect':
                self.btn_camera_preview.show()
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
            VideoFunctions.update_camera_thread(self, frame)

        self.camera_connect_thread = CameraConnectThread()
        self.camera_connect_thread.connect_flag.connect(camera_connect_connect_flag)
        self.camera_connect_thread.camera.connect(camera_connect_camera)
        self.camera_connect_thread.start()
        self.camera_thread = VideoGetThread(self)
        self.camera_thread.rawFrame.connect(camera_thread_rawFrame)
        self.camera_thread.start()


    def setup_frame_processing(self):
        def timer_grab_tic():
            if hasattr(self, 'frame_progress_thread') and not self.frame_progress_thread.isRunning() and hasattr(self, 'raw_frame'):
                self.frame_progress_thread.frame = self.raw_frame
                self.frame_progress_thread.start()
        def frame_progress_thread_statParam(data):
            print(data)
        self.frame_progress_thread = FrameProcessThread(self)
        self.frame_progress_thread.statParam.connect(frame_progress_thread_statParam)
        self.timer_get_frame = TimerThread(self, timer_tic=self.settings['timer_image_grab'])
        self.timer_get_frame.timerTic.connect(timer_grab_tic)
        self.timer_get_frame.start()

    def set_camera(self):
        try:
            if self.current_pool_page_1['id']:
                data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                           table='cameras',
                                                           where='pool_id',
                                                           value=self.current_pool_page_1['id'])

                if data[0] and data[1]:
                    self.current_camera = data[1][0]
                    self.camera = None
                    #self.camera = cv2.VideoCapture(self.current_camera['camera_address'])
                    #self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings[f'camera_{num_camera}_setting']['resolution'][0])
                    #self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings[f'camera_{num_camera}_setting']['resolution'][1])
                    #self.camera.set(cv2.CAP_PROP_FPS, self.settings[f'camera_{num_camera}_setting']['frame_rate'])
                    #self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)'''
                    return True
            return False
        except Exception as e:
            print(f'error set_camera: {e}')
            return False

    def stop_video_processing_threads(self):
        self.camera_thread.stop()
        self.camera_connect_thread.stop()

    def stop_frame_processing_treads(self):
        if hasattr(self, 'timer_get_frame'):
            self.timer_get_frame.stopped = True
            self.timer_get_frame.wait()
            self.timer_get_frame.terminate()
        if hasattr(self, 'frame_progress_thread'):
            self.frame_progress_thread.clear()
            self.frame_progress_thread.wait()
            self.timer_get_frame.terminate()
            #self.frame_progress_thread.terminate()


    def change_camera(self):
        while(self.camera_thread.isStreamming):
            self.camera_thread.stop_stream()
        self.camera_connect_thread.cam_disconnect()
        #VideoFunctions.stop_frame_processing_treads(self)
        if not VideoFunctions.set_camera(self): self.current_camera = None
        self.camera_connect_thread.current_camera = self.current_camera


    def update_preview(self, frame):
        '''if self.start_rect_pos and self.scene_mouse_pos and self.pbtn_zoom.objectName() == 'zoom':
            self.scale_rectangle.setRect(QRectF(self.start_rect_pos, QSize(abs(self.scene_mouse_pos.x() - self.start_rect_pos.x()),
                                                                           abs(self.scene_mouse_pos.y() - self.start_rect_pos.y()))))'''
        scene_ratio = self.scene.sceneRect().width() / self.scene.sceneRect().height()
        h, w, _ = frame.shape
        frame_ratio = w / h
        #self.l_preview.setPixmap(VideoFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio, Qt.KeepAspectRatio))
        if abs(scene_ratio - frame_ratio) / scene_ratio > 0.1:
            self.l_preview.setPixmap(VideoFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio, Qt.KeepAspectRatio))
        else:
            self.l_preview.setPixmap(VideoFunctions.convert_cv_to_pixmap(frame).scaled(self.scene.sceneRect().width(), self.scene.sceneRect().width() / frame_ratio))
        '''if hasattr(self, "start_recognize_timer"):
            filtered_recognize_fps = self.filter_recognize_fps(time.perf_counter(), (1 / (time.perf_counter() - self.start_recognize_timer)))
            if self.grabbed == 'done':
                self.l_recognize_fps.setText(f'FPS (распознавание): {int(filtered_recognize_fps)}')
            elif self.grabbed == 'undone':
                self.l_recognize_fps.setText('FPS (распознавание):  - -')
        self.start_recognize_timer = time.perf_counter()'''


    def convert_cv_to_pixmap(frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame, w, h,bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        return pixmap


    def change_scale(self):
        if self.pbtn_zoom.is_active() and self.pbtn_zoom.objectName() == 'zoom':
            x_factor = self.settings['camera_0_setting']['resolution'][0] / self.scene.sceneRect().width()
            y_factor = self.settings['camera_0_setting']['resolution'][1] / self.scene.sceneRect().height()
            self.camera_thread.scaled_size = (int(self.start_rect_pos.x() * x_factor), int(self.start_rect_pos.y() * y_factor),
                                              int(self.end_rect_pos.x() * x_factor), int(self.end_rect_pos.y() * y_factor))
            self.scale_rectangle.setRect(QRectF(0,0,0,0))
            self.start_rect_pos = None
            self.scene_mouse_pos = None
            self.end_rect_pos = None
            self.pbtn_zoom.set_active(False)
            self.pbtn_zoom.setObjectName('home')
            self.pbtn_zoom.set_icon(Functions.set_svg_icon("icon_home.svg"))
            self.pbtn_change_camera.setEnabled(False)
        if self.pbtn_zoom.is_active() and self.pbtn_zoom.objectName() == 'home':
            self.camera_thread.scaled_size = None
            self.pbtn_change_camera.setEnabled(True)


    def sample_preview(self, frame):
        if hasattr(self, 'anim_is_running') and not self.anim_is_running:
            self.l_sample_video.setPixmap(TaskWindowFunctions.convert_cv_to_pixmap(frame).scaled(self.l_sample_video.width(), self.l_sample_video.height()))
        elif hasattr(self, 'anim_is_running') and self.anim_is_running:
            self.l_sample_video.setPixmap(TaskWindowFunctions.convert_cv_to_pixmap(frame).scaled(self.sample_video_max_size.width(), self.sample_video_max_size.height()))
        elif not hasattr(self, 'anim_is_running'):
            self.anim_is_running = False


    def zoom_button(self):
        if self.pbtn_zoom.is_active() and self.pbtn_zoom.objectName() == 'zoom':
            self.pbtn_zoom.toggle()
            self.start_rect_pos = None
        elif not self.pbtn_zoom.is_active() and self.pbtn_zoom.objectName() == 'zoom':
            self.pbtn_zoom.toggle()

        if not self.pbtn_zoom.is_active() and self.pbtn_zoom.objectName() == 'home':
            self.pbtn_zoom.toggle()
            TaskWindowFunctions.change_scale(self)
            self.pbtn_zoom.setObjectName('zoom')
            self.pbtn_zoom.toggle()

        if self.pbtn_zoom.objectName() == 'zoom':
            self.pbtn_zoom.set_icon(Functions.set_svg_icon("icon_zoom.svg"))
        elif self.pbtn_zoom.objectName() == 'home':
            self.pbtn_zoom.set_icon(Functions.set_svg_icon("icon_home.svg"))


    def record(self, recording):
        if recording:
            self.start_recording = True
            self.stop_recording = False
        else:
            self.start_recording = False
            self.stop_recording = True


    def get_video_writer_mode(self):
        if self.settings['video_recording_setting']['forced_writer_mode']:
            return self.settings['video_recording_setting']['forced_writer_mode']
        h, w, ch = self.raw_frame.shape
        fps = self.settings[f'camera_{self.cur_camera_num}_setting']['frame_rate']
        time = self.settings['video_recording_setting']['time_recording']
        self.frame_ratio = w / h
        if psutil.virtual_memory().available < (h * w * ch * fps * time):
            mode = 'real_time'
        else:
            mode = 'post_time'
        return  mode


    def update_camera_thread(self, frame):
        self.raw_frame = frame.copy()
        VideoFunctions.update_preview(self, self.raw_frame)



    def video_recording(self, frame):
        if self.start_recording and not self.stop_recording:
            if self.video_writer_mode == 'post_time':
                self.frame_list.append(frame)
            elif self.video_writer_mode == 'real_time':
                self.video_write_thread.frame = frame
                if not self.video_write_thread.isRunning():
                    self.video_write_thread.writer_close = False
                    self.video_write_thread.mode = 'real_time'
                    name_video_file = next(x['name_video'] for x in self.results_list if x["task_id"] == self.cur_task_id)
                    name_video = os.path.join(VIDEO_DATA_PATH, name_video_file)
                    if os.path.isfile(name_video): os.remove(name_video)
                    self.video_write_thread.path = name_video
                    self.video_write_thread.frame_rate = self.settings[f'camera_{self.cur_camera_num}_setting']['frame_rate']
                    self.video_write_thread.start()
        if self.stop_recording and not self.start_recording:
            self.stop_recording = False
            if self.video_writer_mode == 'post_time':
                if not self.video_write_thread.isRunning() and self.frame_list:
                    self.video_write_thread.mode = 'post_time'
                    name_video_file = next(x['name_video'] for x in self.results_list if x["task_id"] == self.cur_task_id)
                    name_video = os.path.join(VIDEO_DATA_PATH, name_video_file)
                    if os.path.isfile(name_video): os.remove(name_video)
                    self.video_write_thread.path = name_video
                    self.video_write_thread.frame_list = self.frame_list
                    self.video_write_thread.frame_rate = self.settings[f'camera_{self.cur_camera_num}_setting']['frame_rate']
                    self.video_write_thread.start()
            elif self.video_writer_mode == 'real_time':
                self.video_write_thread.writer_close = True
                #self.video_write_thread.start()


    def video_write_thread_started(self):
        if self.video_writer_mode == 'post_time':
            # blocking camera increase speed video writing
            self.camera_thread.stopped = True
            self.camera_thread.wait()
            self.grab_flag = False
            self.time_procceses = time.perf_counter()


    def video_write_thread_status(self, status):
        self.wait_progress.show()
        self.wait_progress.set_message(f'Подождите...\nОбработка видео...{status}%')


    def video_write_thread_finished(self):
        if self.video_writer_mode == 'post_time' or self.video_write_thread.writer_close:
            self.frame_list.clear()
            if not self.reset_flag:
                self.name_video_file = next(z['name_video'] for z in self.results_list if z["task_id"] == self.cur_task_id)
                self.name_csv_file = next(z['name_raw_data'] for z in self.results_list if z["task_id"] == self.cur_task_id)
                self.name_compute_csv_file = next(z['name_compute_data'] for z in self.results_list if z["task_id"] == self.cur_task_id)
                self.landmarks_list = TaskWindowFunctions.prepare_data(self, self.data_list, os.path.join(VIDEO_DATA_PATH, self.name_video_file))
                self.raw_data_list = PrepareDataFunctions.create_raw_data_list(self.cur_task_id, self.landmarks_list)
                PrepareDataFunctions.create_csv_file(os.path.join(TABLE_DATA_PATH, self.name_csv_file), self.raw_data_list)
                chart_data = PrepareDataFunctions.create_chart_data(self.cur_task_id, self.raw_data_list, TaskWindowFunctions.get_patient_sizes(self), self.frame_ratio)
                self.compute_data_list = PrepareDataFunctions.create_compute_data_list(chart_data)
                PrepareDataFunctions.create_csv_file(os.path.join(TABLE_DATA_PATH, self.name_compute_csv_file), self.compute_data_list)
                self.chart = TaskWindowFunctions.create_chart(self, chart_data)
                self.chart_view.setChart(self.chart)
            else:
                self.reset_flag = False
            # blocking camera increase speed video writing
            self.camera_thread.stopped = False
            self.camera_thread.start()
            self.grab_flag = True
            self.wait_progress.hide()
            #self.chart_view.update()
            #QApplication.processEvents()



    def create_chart(self, chart_data):
        chart = QChart()
        chart.layout().setContentsMargins(0,0,0,0)
        chart.setMargins(QMargins(5,5,5,5))
        chart.legend().hide()
        data_series = []
        quality_series = []
        empty_series = []
        select_series = []
        for data in chart_data['chart_list']['data_charts']:
            lower_data_series = QLineSeries(chart)
            upper_data_series = QLineSeries(chart)
            lower_quality_series = QLineSeries(chart)
            upper_quality_series = QLineSeries(chart)
            for x_point in data:
                lower_data_series.append(QPointF(chart_data['x_data_list'][x_point], 0))
                upper_data_series.append(QPointF(chart_data['x_data_list'][x_point], chart_data['y_data_list'][x_point]))
                lower_quality_series.append(QPointF(chart_data['x_data_list'][x_point], 0))
                upper_quality_series.append(QPointF(chart_data['x_data_list'][x_point], chart_data['y_quality_list'][x_point]))
            data_area = QAreaSeries(upper_data_series, lower_data_series)
            data_area.setBrush(QColor(86, 104, 232, 100))
            data_area.setPen(Qt.NoPen)
            quality_area = QAreaSeries(lower_quality_series, upper_quality_series)
            quality_area.setBrush(QColor(218, 165, 32, 50))
            quality_area.setPen(Qt.NoPen)
            pen = QPen(QColor("#5668E8"))
            pen.setWidth(1)
            upper_data_series.setPen(pen)
            lower_data_series.setPen(pen)
            lower_quality_series.setPen(Qt.NoPen)
            data_series.append(data_area)
            data_series.append(upper_data_series)
            quality_series.append(quality_area)

            start_line = QLineSeries(chart)
            start_line.setName('start_line')
            pen = QPen(QColor("#0bda51"))
            pen.setWidth(1)
            start_line.setPen(pen)
            start_line.hide()
            end_line = QLineSeries(chart)
            end_line.setName('end_line')
            pen = QPen(QColor("#0bda51"))
            pen.setWidth(1)
            end_line.setPen(pen)
            end_line.hide()
            upper_select_line = QLineSeries(chart)
            upper_select_line.setName('upper_select_line')
            lower_select_line = QLineSeries(chart)
            lower_select_line.setName('lower_select_line')
            select_area = QAreaSeries(upper_select_line, lower_select_line)
            select_area.setName('select_area')
            select_area.setBrush(QColor(11, 218, 81, 50))
            select_area.setPen(Qt.NoPen)
            select_area.hide()
            select_series.append(select_area)
            select_series.append(upper_select_line)
            select_series.append(lower_select_line)
            select_series.append(start_line)
            select_series.append(end_line)

        for data in chart_data['chart_list']['empty_charts']:
            lower_empty_series = QLineSeries(chart)
            upper_empty_series = QLineSeries(chart)
            for x_point in data:
                lower_empty_series.append(QPointF(chart_data['x_data_list'][x_point], 0))
                upper_empty_series.append(QPointF(chart_data['x_data_list'][x_point], 1))
            empty_area = QAreaSeries(upper_empty_series, lower_empty_series)
            empty_area.setBrush(QColor(255, 85, 85, 50))
            empty_area.setPen(Qt.NoPen)
            empty_series.append(empty_area)

        axisX = QValueAxis()
        if chart_data['x_data_list'][-1] < 10:
            if int(chart_data['x_data_list'][-1]) < chart_data['x_data_list'][-1]:
                axisX.setTickCount(int(chart_data['x_data_list'][-1]) + 1)
            else:
                axisX.setTickCount(int(chart_data['x_data_list'][-1]))
        else:
            axisX.setTickCount(10)
        axisX.setRange(0, chart_data['x_data_list'][-1])
        #axisX.setLabelFormat("%d")
        axisX.setTitleText("Время [сек]")
        axisX.setTitleFont(QFont(self.settings['font']['family'], 8, QFont.Normal))
        axisX.setLabelsFont(QFont(self.settings['font']['family'], 8, QFont.Normal))
        chart.addAxis(axisX, Qt.AlignBottom)

        axisY1 = QValueAxis()
        axisY1.setRange(min([x for x in chart_data['y_data_list'] if x]), max([x for x in chart_data['y_data_list'] if x]))
        axisY1.setLabelFormat("%.1f")
        axisY1.setTitleText(chart_data['Y1_title'])
        axisY1.setTitleFont(QFont(self.settings['font']['family'], 8, QFont.Normal))
        axisY1.setLabelsFont(QFont(self.settings['font']['family'], 8, QFont.Normal))
        axisY1.setLabelsBrush(QBrush(QColor("#5668E8")))
        chart.addAxis(axisY1, Qt.AlignLeft)

        axisY2 = QValueAxis()
        axisY2.setRange(0, 1)
        axisY2.setLabelFormat("%.2f")
        axisY2.setTitleText(chart_data['Y2_title'])
        axisY2.setTitleFont(QFont(self.settings['font']['family'], 8, QFont.Normal))
        axisY2.setTitleText("Качество захвата [ед]")
        axisY2.setLabelsFont(QFont(self.settings['font']['family'], 8, QFont.Normal))
        axisY2.setLabelsBrush(QBrush(QColor("#daa520")))
        axisY2.setGridLineVisible(False)
        chart.addAxis(axisY2, Qt.AlignRight)

        for serie in data_series:
            chart.addSeries(serie)
            serie.attachAxis(axisX)
            serie.attachAxis(axisY1)
            serie.setPointsVisible(False)
            serie.setPointLabelsVisible(False)

        for serie in quality_series:
            chart.addSeries(serie)
            serie.attachAxis(axisX)
            serie.attachAxis(axisY2)
            serie.setPointsVisible(False)
            serie.setPointLabelsVisible(False)

        for serie in empty_series:
            chart.addSeries(serie)
            serie.attachAxis(axisX)
            serie.attachAxis(axisY2)
            serie.setPointsVisible(False)
            serie.setPointLabelsVisible(False)

        for serie in select_series:
            chart.addSeries(serie)
            serie.attachAxis(axisX)
            serie.attachAxis(axisY2)
            serie.setPointsVisible(False)
            serie.setPointLabelsVisible(False)

        chart.setAnimationOptions(QChart.AllAnimations)
        try:
            marker_list = chart.legend().markers()
            marker_list[0].setVisible(False)
        except Exception as e:
            print(e)

        return chart
































