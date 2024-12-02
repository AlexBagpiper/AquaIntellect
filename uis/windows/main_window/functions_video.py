# -*- coding: utf-8 -*-

import time
from import_core import *
from core.functions import Functions
from core.functions_database import *
from config.file_path import *
from uis.windows.main_window.functions_main_window import *


class TimerThread(QObject):
    timerTic = Signal()

    def __init__(self, timer_tic=None):
        super().__init__()
        self.timer_tic = timer_tic
        self.stopped = False

    @Slot()
    def run(self):
        self.stopped = False
        while not self.stopped:
            time.sleep(self.timer_tic)
            self.timerTic.emit()

    def stop(self):
        self.stopped = True


class VideoGetThread(QThread):
    rawFrame = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stream = parent.camera
        self.scaled_size = None
        camera_roi = parent.current_camera['camera_roi']
        if camera_roi:
            camera_roi = json.loads(camera_roi)
            self.scaled_size = [camera_roi['x'], camera_roi['y'], camera_roi['x'] + camera_roi['w'], camera_roi['y'] + camera_roi['h']]
        self.stopped = False

    def run(self):
        while self.stream.isOpened() and not self.stopped:
            try:
                #s = time.perf_counter()
                (self.grabbed, frame) = self.stream.read()
                #print(time.perf_counter() - s)
                h, w, ch = frame.shape
                if self.scaled_size and (h != self.scaled_size[1] or w != self.scaled_size[0]):
                    frame = frame[self.scaled_size[1]:self.scaled_size[3], self.scaled_size[0]:self.scaled_size[2]]
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.rawFrame.emit(self.frame)
            except Exception as e:
                print(e)
                #self.stream.release()

    def stop(self):
        self.stopped = True
        self.stream.release()


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


class RecognizeThread(QThread):
    recognizedFrame = Signal(object)
    unrecognizedFrame = Signal(object)

    def __init__(self, parent=None, solution=None, smoothing_hand=True, smoothing_pose=True):
        super().__init__(parent)
        self.settings = parent.settings
        self.solution = solution
        self.stream = parent.camera
        self.stopped = False
        self.smoothing_hand = smoothing_hand
        self.smoothing_pose = smoothing_pose

        self.raw_frame = None
        self.recognized_frame = None
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.frame_num = None
        self.time_frame = None

        self.hand_landmarks = {'frame': None, 'time': None, 'status': None, 'left': None, 'right': None, 'score': None}
        self.pose_landmarks = {'frame': None, 'time': None, 'status': None, 'pose': None}

        self.current_hand = None

        if self.smoothing_hand:
            min_cutoff = 0.004
            beta = 30.0
            self.filter_hand_x_list = [OneEuroFilter(0.0, 0.0, min_cutoff=min_cutoff, beta=beta) for x in range(21)]
            self.filter_hand_y_list = [OneEuroFilter(0.0, 0.0, min_cutoff=min_cutoff, beta=beta) for x in range(21)]
            self.filter_hand_z_list = [OneEuroFilter(0.0, 0.0, min_cutoff=min_cutoff, beta=beta) for x in range(21)]

        if self.smoothing_pose:
            min_cutoff = 0.004
            beta = 30.0
            self.filter_pose_x_list = [OneEuroFilter(0.0, 0.0, min_cutoff=min_cutoff, beta=beta) for x in range(33)]
            self.filter_pose_y_list = [OneEuroFilter(0.0, 0.0, min_cutoff=min_cutoff, beta=beta) for x in range(33)]
            self.filter_pose_z_list = [OneEuroFilter(0.0, 0.0, min_cutoff=min_cutoff, beta=beta) for x in range(33)]

    def run(self):
        if self.solution == 'hand':
            self.hands()
        elif self.solution == 'pose':
            self.pose()

    def smoothing_hand_filter(self, hand_landmarks):
        timestamp = time.perf_counter()
        for idx, landmark in enumerate(hand_landmarks.landmark):
            filtered_x = self.filter_hand_x_list[idx](timestamp, landmark.x)
            filtered_y = self.filter_hand_y_list[idx](timestamp, landmark.y)
            filtered_z = self.filter_hand_z_list[idx](timestamp, landmark.z)
            hand_landmarks.landmark[idx].x = filtered_x
            hand_landmarks.landmark[idx].y = filtered_y
            hand_landmarks.landmark[idx].z = filtered_z
        return hand_landmarks


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

    def setup_video_processing(self):
        def camera_thread_rawFrame(frame):
            VideoFunctions.update_camera_thread(self, frame)

        def video_write_thread_status(writer_complete):
            VideoFunctions.video_write_thread_status(self, writer_complete)

        def recognize_thread_recognizedFrame(frame):
            VideoFunctions.recognize_thread_complete(self, frame, 'done')

        def recognize_thread_unrecognizedFrame(frame):
            VideoFunctions.recognize_thread_complete(self, frame, 'undone')

        VideoFunctions.set_camera(self)
        #self.scaled_size = (self.preview_size[0], self.preview_size[1])
        self.scaled_size = (600, 600)
        self.camera_thread = VideoGetThread(self)
        self.camera_thread.rawFrame.connect(camera_thread_rawFrame)
        '''self.filter_camera_fps = OneEuroFilter(0.0, 0.0, min_cutoff=0.01, beta=0.01)
        self.filter_recognize_fps = OneEuroFilter(0.0, 0.0, min_cutoff=0.01, beta=0.01)
        self.video_write_thread = VideoWriteThread(self)
        self.video_write_thread.status.connect(video_write_thread_status)
        self.video_write_thread.started.connect(lambda: TaskWindowFunctions.video_write_thread_started(self))
        self.video_write_thread.finished.connect(lambda: TaskWindowFunctions.video_write_thread_finished(self))
        #set 'cur_solution' depending of task
        self.recognize_thread = RecognizeThread(self, solution=self.cur_solution)
        self.recognize_thread.recognizedFrame.connect(recognize_thread_recognizedFrame)
        self.recognize_thread.unrecognizedFrame.connect(recognize_thread_unrecognizedFrame)'''
        #self.camera_thread.rawFrame.connect(lambda: TaskWindowFunctions.update_camera_thread(self, self.camera_thread.frame))
        self.camera_thread.start()
        self.cam_frame_counter = 0
        self.recog_frame_counter = 0


    def set_camera(self):
        try:
            if self.current_pool['id']:
                data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                           table='cameras',
                                                           where='pool_id',
                                                           value=self.current_pool['id'])

                if data[0] and data[1]:
                    self.current_camera = data[1][0]
                    self.camera = cv2.VideoCapture(self.current_camera['camera_address'])
                    #self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings[f'camera_{num_camera}_setting']['resolution'][0])
                    #self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings[f'camera_{num_camera}_setting']['resolution'][1])
                    #self.camera.set(cv2.CAP_PROP_FPS, self.settings[f'camera_{num_camera}_setting']['frame_rate'])
                    #self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)'''
                    return True
            return False
        except Exception as e:
            print(f'error set_camera: {e}')
            return False

    def stop_video_processing_thread(self):
        self.camera_thread.stopped = True
        self.camera_thread.wait()
        self.camera.release()
        #self.recognize_thread.wait()
        #self.cam_frame_counter = 0
        #self.recog_frame_counter = 0


    def change_camera(self):
        VideoFunctions.stop_video_processing_thread(self)
        VideoFunctions.set_camera(self)
        self.camera_thread.stream = self.camera
        self.recognize_thread.stream = self.camera
        self.camera_thread.stopped = False
        self.camera_thread.start()
        #self.cam_frame_counter = 0
        #self.recog_frame_counter = 0


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
        #VideoFunctions.grab_data(self)
        #VideoFunctions.video_recording(self, frame)
        # save video with mask
        #self.raw_frame = frame
        # save video without mask
        self.raw_frame = frame.copy()
        VideoFunctions.update_preview(self, self.raw_frame)
        '''if self.grab_flag and not self.recognize_thread.isRunning():
            self.recognize_thread.raw_frame = frame
            self.recognize_thread.stopped = False
            self.recognize_thread.start()
        elif not self.grab_flag and not self.recognize_thread.isRunning():
            VideoFunctions.update_preview(self, self.raw_frame)
        elif not self.grab_flag and self.recognize_thread.isRunning():
            self.recognize_thread.stopped = True
            VideoFunctions.update_preview(self, self.raw_frame)'''
        '''if hasattr(self, "start_camera_timer"):
            filtered_camera_fps = self.filter_camera_fps(time.perf_counter(), (1 / (time.perf_counter() - self.start_camera_timer)))
            self.l_camera_fps.setText(f'FPS (камера): {int(filtered_camera_fps)}')
        self.start_camera_timer = time.perf_counter()'''

        #print(f'camera_counter: {self.cam_frame_counter}')


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


    def recognize_thread_complete(self, frame, state=None):
        self.recog_frame_counter += 1
        self.recognize_thread.raw_frame = self.raw_frame
        TaskWindowFunctions.update_preview(self, frame)
        if state == 'done':
            self.ibtn_grab._set_icon_color = 'green'
            if self.cur_solution == 'hand':
                if self.recognize_thread.current_hand == 'left':
                    self.ibtn_grab._set_icon_path = Functions.set_svg_icon("left_hand_in_frame.svg")
                elif self.recognize_thread.current_hand == 'right':
                    self.ibtn_grab._set_icon_path = Functions.set_svg_icon("right_hand_in_frame.svg")
            elif self.cur_solution == 'pose':
                self.ibtn_grab._set_icon_path = Functions.set_svg_icon("human_in_frame.svg")
            self.is_recognized = True
        elif state == 'undone':
            self.ibtn_grab._set_icon_color = '#AF0000'
            self.ibtn_grab._set_icon_path = Functions.set_svg_icon("empty_frame.svg")
            self.is_recognized = False
        self.grabbed = state
        if self.start_flag:
            if self.cur_solution == 'hand':
                TaskWindowFunctions.collect_data(self, self.recognize_thread.hand_landmarks)
            elif self.cur_solution == 'pose':
                TaskWindowFunctions.collect_data(self, self.recognize_thread.pose_landmarks)


    def start_task(self):
        self.start_flag = True
        self.cam_frame_counter = 0
        self.data_list.clear()
        self.video_writer_mode = TaskWindowFunctions.get_video_writer_mode(self)
        TaskWindowFunctions.update_action_button(self, 'reset')
        TaskWindowFunctions.preview_content_change(self, 'start')
        TaskWindowFunctions.start_task_timer(self)
        TaskWindowFunctions.record(self, True)


    def stop_task(self):
        self.wait_progress.show()
        self.wait_progress.set_message('Подождите...')
        self.start_flag = False
        TaskWindowFunctions.preview_content_change(self, 'stop')
        TaskWindowFunctions.record(self, False)
        TaskWindowFunctions.update_action_button(self, 'save')


    def reset_task(self):
        if self.start_flag:
            self.start_flag = False
            self.progress_timer.stop()
            self.progress_timer_thread.quit()
            TaskWindowFunctions.stop_task(self)
            TaskWindowFunctions.preview_content_change(self, 'stop')
            TaskWindowFunctions.record(self, False)
        TaskWindowFunctions.update_action_button(self, 'start')
        self.reset_flag = True
        TaskWindowFunctions.clear_chart(self, self.chart)


    def exit_tasks(self):
        TaskWindowFunctions.stop_video_processing_thread(self)
        for result in self.results_list:
            if not result['date_result']:
                name_video = os.path.join(VIDEO_DATA_PATH, result['name_video'])
                name_raw_data = os.path.join(TABLE_DATA_PATH, result['name_raw_data'])
                name_compute_data = os.path.join(TABLE_DATA_PATH, result['name_compute_data'])
                if os.path.isfile(name_video): os.remove(name_video)
                if os.path.isfile(name_raw_data): os.remove(name_raw_data)
                if os.path.isfile(name_compute_data): os.remove(name_compute_data)


    def save_task(self):
        if not TaskWindowFunctions.save_check(self):
            return
        TaskWindowFunctions.update_action_button(self, 'start')
        next(btn for btn in self.task_left_menu.findChildren(QPushButton) if btn.objectName() == self.cur_task_id).set_status_checked(True)
        data_list = next(x for x in self.results_list if x['task_id'] == self.cur_task_id)
        data_list.update({'date_result': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                          'human_score': next(x.objectName().split('_')[-1] for x in self.findChildren(PyToggle) if x.isChecked()),
                          'comp_score': False if not self.cur_score['status'] else self.cur_score['info'].split('_')[-1],
                          'comments': self.tedit_comment.toPlainText()})
        check_data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                   table='results_tasks',
                                                   where='result_task_id',
                                                   value=data_list['result_task_id'])
        if check_data[1]:
            data = DatabaseFunctions.update_data(database=COMMON_DATABASE_PATH,
                                                 table='results_tasks',
                                                 column_list=list(data_list.keys()),
                                                 value_list=list(data_list.values()),
                                                 where_column='result_task_id',
                                                 where_value=data_list['result_task_id'])
        else:
            data = DatabaseFunctions.insert_data(database=COMMON_DATABASE_PATH,
                                                 table='results_tasks',
                                                 column_list=data_list.keys(),
                                                 value_list=data_list.values())

        for item in self.results_list:
            if item['result_task_id'] == data_list['result_task_id']:
                item.update({'date_result': data_list['date_result'],
                             'human_score': data_list['human_score'],
                             'comp_score': data_list['comp_score'],
                             'comments': data_list['comments']})
        TaskWindowFunctions.clear_chart(self, self.chart)
        TaskWindowFunctions.fill_data(self, self.cur_task_id)


    def save_check(self):
        msg_text = None
        score = next((x.objectName().split('_')[-1] for x in self.findChildren(PyToggle) if x.isChecked()), False)
        if not score:
            msg_text = 'Выставите оценку выполненному упражнению!'
        if  msg_text:
            msg = PyMessageBox(self.parent,
                                   mode = 'information',
                                   text_message=msg_text,
                                   button_yes_text='Ок',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
            msg.l_message.setWordWrap(False)
            msg.show()
            return False

        csv_file = os.path.join(TABLE_DATA_PATH, self.name_csv_file)
        df = pd.read_csv(csv_file)
        flags_list = df['FLAGS'].tolist()
        flag = False
        for value in flags_list:
            if value == 'valid':
                flag = True
                break
        # Remove when will make compute core for this tasks
        ################################
        if self.cur_task_id in ['UPDRS_task_15', 'UPDRS_task_16']:
            flag = True
        ################################
        if not flag:
            msg_text = 'Выберите на графике область допустимых\nзначений для более точного расчета оценки.'
        if  msg_text:
            msg = PyMessageBox(self.parent,
                                   mode = 'information',
                                   text_message=msg_text,
                                   button_yes_text='Ок',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
            msg.l_message.setWordWrap(False)
            msg.show()
            return False
        return True


    def clear_chart(self, chart):
        chart.removeAllSeries()
        for ax in chart.axes():
            chart.removeAxis(ax)


    def start_check(self):
        msg_text = None
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='task_updrs',
                                             where='task_id',
                                             value=self.cur_task_id)
        if not self.is_recognized:
            if self.cur_solution == 'pose':
                msg_text = 'Отсутствует захват тела в кадре!\nВыполните захват тела.'
            elif self.cur_solution == 'hand' and data[1][0]['side'] == 'left':
                msg_text = 'Отсутствует захват левой руки в кадре!\nВыполните захват левой руки.'
            elif self.cur_solution == 'hand' and data[1][0]['side'] == 'right':
                msg_text = 'Отсутствует захват правой руки в кадре!\nВыполните захват правой руки.'
        elif self.is_recognized and self.cur_solution == 'hand' and data[1][0]['side'] != self.recognize_thread.current_hand:
                msg_text = 'Выполнен захват неверной руки!\nСмените руку.'
        elif next(btn for btn in self.task_left_menu.findChildren(QPushButton) if btn.objectName() == self.cur_task_id).is_status_checked():
            msg = PyMessageBox(self.parent,
                               mode='question',
                               text_message='Задание уже выполнено.\nВыполнить упражнение снова?',
                               button_yes_text='Да',
                               button_no_text='Нет',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
            msg.yes.connect(lambda: TaskWindowFunctions.start_task(self))
            msg.l_message.setWordWrap(False)
            msg.show()
            return False
        if msg_text:
            msg = PyMessageBox(self.parent,
                                   mode = 'information',
                                   text_message=msg_text,
                                   button_yes_text='Ок',
                                   pos_mode='center',
                                   animation=None,
                                   sound='notify_messaging.wav')
            msg.l_message.setWordWrap(False)
            msg.show()
            return False
        return True


    def preview_content_change(self, preset=None):
        if preset == 'start':
            self.circular_progress.setVisible(True)
            self.icon_record.setVisible(True)
            self.pbtn_zoom.setVisible(False)
            self.pbtn_change_camera.setVisible(False)
        elif preset == 'stop':
            self.circular_progress.setVisible(False)
            self.icon_record.setVisible(False)
            self.pbtn_zoom.setVisible(True)
            self.pbtn_change_camera.setVisible(True)


    def start_task_timer(self):
        self.timer_tic = 0.025
        self.start_timer = time.perf_counter()

        self.progress_timer_thread = QThread()

        self.progress_timer = TimerThread(self.timer_tic)
        self.progress_timer.moveToThread(self.progress_timer_thread)
        self.progress_timer.timerTic.connect(lambda: TaskWindowFunctions.update_progress(self))
        self.progress_timer_thread.started.connect(self.progress_timer.run)
        self.progress_timer_thread.start()


    def update_progress(self):
        time_elapsed = time.perf_counter() - self.start_timer
        if self.circular_progress.max_value - time_elapsed <= 0:
            self.circular_progress.set_value(0)
            self.progress_timer.stop()
            self.progress_timer_thread.quit()
            TaskWindowFunctions.stop_task(self)
        self.circular_progress.set_value(self.circular_progress.max_value - time_elapsed)


    def update_action_button(self, btn_id, enabled=True):
        if btn_id == 'start':
            self.pbtn_action.setObjectName('start')
            self.pbtn_action.setText(QCoreApplication.translate("QPushButton", 'Начать', None))
        elif btn_id == 'save':
            self.pbtn_action.setObjectName('save')
            self.pbtn_action.setText(QCoreApplication.translate("QPushButton", 'Сохранить', None))
            self.pbtn_skip_exit.setObjectName('tasks_pbtn_exit')
            self.pbtn_skip_exit.setText(QCoreApplication.translate("QPushButton", 'Выйти', None))
        elif btn_id == 'reset':
            self.pbtn_action.setObjectName('reset')
            self.pbtn_action.setText(QCoreApplication.translate("QPushButton", 'Сброс', None))
        self.pbtn_action.setEnabled(enabled)


    def grab_data(self):
        if self.start_flag:
            self.recognize_thread.frame_num = self.cam_frame_counter
            self.recognize_thread.time_frame = time.perf_counter()
            self.cam_frame_counter += 1


    def collect_data(self, data):
        self.data_list.append(data)


    def prepare_data(self, data, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step_time = 1 / cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        data_list = [None for x in range(frames)]
        for idx, row in enumerate(data):
            if row['frame'] and row['frame'] < len(data_list): data_list[row['frame']] = row
        while data_list.count(None) > 0:
            for idx, row in enumerate(data_list[:-1]):
                if not row and data_list[idx + 1]:
                    data_list[idx] = data_list[idx + 1].copy()
                    data_list[idx].update({'frame': idx, 'time': data_list[idx + 1]['time'] - step_time})
            for idx, row in enumerate(data_list[1:][::-1]):
                if not row and data_list[len(data_list) - idx - 2]:
                    data_list[len(data_list) - idx - 1] = data_list[len(data_list) - idx - 2].copy()
                    data_list[len(data_list) - idx - 1].update({'frame': len(data_list) - idx - 1, 'time': data_list[len(data_list) - idx - 2]['time'] + step_time})
        start_time = data_list[0]['time']
        for idx, data in enumerate(data_list):
            # simple increase time frame
            data.update({'time': idx * step_time})
            # compute time frame
            #data.update({'time': data['time'] - start_time})
        return data_list


    def get_left_menu_list(self):
        menu_list = []
        for idx, task in enumerate(self.tasks_list):
            if task['task_solution'] == 'hand_left':
                btn_icon = "left_hand.svg"
            elif task['task_solution'] == 'hand_right':
                btn_icon = "right_hand.svg"
            elif task['task_solution'] == 'pose':
                btn_icon = "human.svg"
            elif task['task_solution'] == 'pose_left':
                btn_icon = "human.svg"
            elif task['task_solution'] == 'pose_right':
                btn_icon = "human.svg"
            else:
                btn_icon = "no_icon.svg"
            menu_list.append({"btn_icon" : btn_icon,
                              "btn_id" : task['task_id'],
                              "is_active": task['is_current_task'],
                              "is_status_checked": True if task['result_task_id'] else False})
        return menu_list


    def get_recognize_solution(self, task_id):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='task_updrs',
                                             where='task_id',
                                             value=task_id)
        if data[0] and data[1]:
            return data[1][0]['recognize_solution']


    def get_sample_video_path(task_id):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                            table='task_updrs',
                                            where='task_id',
                                            value=task_id)
        if data[0] and data[1]:
            return os.path.join(SAMPLE_VIDEO_PATH, data[1][0]['sample_video'])
        return None


    def prepare_results_list(self):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                     table='sessions',
                                                     where='session_id',
                                                     value=self.cur_session_id)
        results_list = [{'result_task_id': x['result_task_id'], 'task_id': x['task_id'], 'date_result': False,
                         'human_score': False, 'comp_score': False, 'comments': False,
                         'name_video': False, 'name_raw_data': False, 'name_compute_data': False,
                         'session_id': self.cur_session_id, 'personal_card_id': data[1][0]['personal_card_id'],
                         'staff_id': data[1][0]['staff_id'], 'company_id': data[1][0]['company_id'], 'sync_number': '0'} for x in self.tasks_list]
        for result in results_list:
            if result['result_task_id']:
                data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                     table='results_tasks',
                                                     where='result_task_id',
                                                     value=result['result_task_id'])
                if data[0] and data[1]:
                    result.update({'date_result': data[1][0]['date_result'], 'human_score': data[1][0]['human_score'],
                                   'comp_score': data[1][0]['comp_score'], 'comments': data[1][0]['comments'],
                                   'name_video': data[1][0]['name_video'], 'name_raw_data': data[1][0]['name_raw_data'],
                                   'name_compute_data': data[1][0]['name_compute_data']})
            else:
                id = str(uuid.uuid1())
                result.update({'result_task_id': id, 'date_result': False, 'human_score': False,
                               'comp_score': False, 'comments': False, 'name_video': f'video__{id}.avi',
                               'name_raw_data': f'raw_data__{id}.csv', 'name_compute_data': f'compute_data__{id}.csv'})
        return results_list


    def set_current_task(self, task_id):
        self.wait_progress.show()
        self.wait_progress.set_message('Подождите...')
        TaskWindowFunctions.fill_data(self, task_id)
        self.cur_solution = TaskWindowFunctions.get_recognize_solution(self, task_id)
        self.cur_task_id = task_id
        if hasattr(self, 'video_sample_thread'):
            self.video_sample_thread.stopped = True
            self.video_sample_thread.wait()
            self.video_sample_thread.set_video(TaskWindowFunctions.get_sample_video_path(self.cur_task_id))
            if not self.video_sample_thread.isRunning():
                self.video_sample_thread.stopped = False
                self.video_sample_thread.start()
        if hasattr(self, 'recognize_thread'):
            self.recognize_thread.stopped = True
            self.recognize_thread.wait()
            self.recognize_thread.solution = self.cur_solution
            if not self.recognize_thread.isRunning():
                self.recognize_thread.stopped = False
                self.recognize_thread.start()
        self.wait_progress.hide()


    def fill_data(self, task_id):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='task_updrs',
                                             where='task_id',
                                             value=task_id)
        if data[0] and data[1]:
            self.l_title.setText(QCoreApplication.translate("Label", data[1][0]['title'], None))
            self.l_description.setText(QCoreApplication.translate("Label", data[1][0]['description'], None))
        for task in self.tasks_list:
            if task['result_task_id'] and task['task_id'] == task_id:
                data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                                     table='results_tasks',
                                                     where='result_task_id',
                                                     value=task['result_task_id'])
                if data[0] and data[1]:
                    self.tedit_comment.setText(data[1][0]['comments'])
                    self.findChild(PyToggle, f"rbtn_score_{data[1][0]['human_score']}").setChecked(True)
                break
            else:
                self.tedit_comment.setText('')
                self.score_group.setExclusive(False)
                for idx in range(5):
                    self.findChild(PyToggle, f"rbtn_score_{idx}").setChecked(False)
                self.score_group.setExclusive(True)


    def get_patient_sizes(self):
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='sessions',
                                             where='session_id',
                                             value=self.cur_session_id)
        if data[0] and data[1]:
            self.personal_card_id = data[1][0]['personal_card_id']
        else:
            return {'hand_width': None, 'hip_length': None}
        data = DatabaseFunctions.select_data(database=COMMON_DATABASE_PATH,
                                             table='personal_cards',
                                             where='personal_card_id',
                                             value=self.personal_card_id)
        if data[0] and data[1]:
            if data[1][0]['hand_width']: hand_width = int(data[1][0]['hand_width'])
            else: hand_width = None
            if data[1][0]['hip_length']: hip_length = int(data[1][0]['hip_length'])
            else: hip_length = None
            return {'hand_width': hand_width, 'hip_length': hip_length}
        else:
            return {'hand_width': None, 'hip_length': None}


    def create_chart_data(self, list_data):
        chart_data = PrepareDataFunctions.compute_chart_data(self.cur_task_id, list_data, TaskWindowFunctions.get_patient_sizes(self))
        return chart_data


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


    def insert_selected_chart_data(self, data_dict):
        #raw data file
        try:
            csv_file = os.path.join(TABLE_DATA_PATH, self.name_csv_file)
        except:
            return
        df = pd.read_csv(csv_file)
        df['FLAGS'] = df['FLAGS'].replace({'valid': ''})
        time_list = df['TIME'].tolist()
        start_flag = False
        end_flag = False
        for idx, value in enumerate(time_list):
            if value >= data_dict['start'] and value <= data_dict['end']:
                df.loc[idx, 'FLAGS'] = 'valid'
                start_flag = True
                end_flag = True
        if not start_flag or not end_flag:
            for idx, value in enumerate(time_list):
                df.loc[idx, 'FLAGS'] = 'valid'
        df.to_csv(csv_file, index=False)
        #compute data file
        csv_file = os.path.join(TABLE_DATA_PATH, self.name_compute_csv_file)
        df = pd.read_csv(csv_file)
        df['FLAGS'] = df['FLAGS'].replace({'valid': ''})
        time_list = df['TIME'].tolist()
        start_flag = False
        end_flag = False
        for idx, value in enumerate(time_list):
            if value >= data_dict['start'] and value <= data_dict['end']:
                df.loc[idx, 'FLAGS'] = 'valid'
                start_flag = True
                end_flag = True
        if not start_flag or not end_flag:
            for idx, value in enumerate(time_list):
                df.loc[idx, 'FLAGS'] = 'valid'
        df.to_csv(csv_file, index=False)
        self.cur_score = ComputeDataFunctions.compute_score_task(self.cur_task_id, df)
        TaskWindowFunctions.score_window(self, self.cur_score)


    def score_window(self, score_dict):
        msg_text = None
        if not score_dict['status']:
            if score_dict['info'] == 'bad_data':
                msg_text = QCoreApplication.translate("message_text", u"Невозможно выставить оценку!\n\nВыбранные данные низкого качества.\nВыберите другой диапазон данных,\nлибо перезапишите упражнение.", None)
            elif score_dict['info'] == 'short_data':
                msg_text = QCoreApplication.translate("message_text", u"Невозможно выставить оценку!\n\nНедостаточно данных для расчета.\nРасширьте диапазон данных,\nлибо перезапишите упражнение.", None)
            elif score_dict['info'] == 'error_task':
                msg_text = QCoreApplication.translate("message_text", u"Невозможно выставить оценку!\n\nОтсутстует модуль расчета для данного упражнения.", None)
        if msg_text:
            msg = PyMessageBox(self.parent,
                               mode = 'information',
                               text_message=msg_text,
                               button_yes_text='Ок',
                               pos_mode='center',
                               animation=None,
                               sound='notify_messaging.wav')
            msg.l_message.setWordWrap(False)
            msg.show()
            return False
        if hasattr(self, 'score_window'):
            self.score_window.setParent(None)
            del self.score_window
        self.score_window = UI_ScoreWindow(self)
        self.score_window.setWindowModality(Qt.ApplicationModal)
        self.score_window.clicked.connect(self.btn_clicked)
        self.score_window.show()

























