# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.functions import Functions

# IMPORT STYLES
# ///////////////////////////////////////////////////////////////
from . styles import Styles

# PY PUSH BUTTON
# ///////////////////////////////////////////////////////////////
class PyMessageBox(QWidget):
    yes = Signal()
    no = Signal()
    clicked = Signal(object)
    linkClicked = Signal(object)

    def __init__(
        self,
        parent = None,
        obj_name = None,
        mode = None,
        title = "",
        text_message = "",
        link_button_text = None,
        button_yes_text = None,
        button_no_text = None,
        win_flags = Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint,
        bg_color = "#1b1e23",
        font_family = 'Segoe UI',
        font_style = 'normal',
        font_weight = '500',
        font_size = '10px',
        text_color = "#FFFFFF",
        modal = True,
        delete_on_close = False,
        pos_mode = 'center',
        pos_x = 0,
        pos_y = 0,
        animation = b'geometry',
        sound = None
    ):
        QWidget.__init__(self)

        self.setParent(parent)

        self.parent = parent

        if obj_name:
            self.setObjectName(obj_name)

        if modal:
            self.setWindowModality(Qt.WindowModal)

        if delete_on_close:
            self.setAttribute(Qt.WA_DeleteOnClose)

        self.win_flags = win_flags
        self.pos_mode = pos_mode
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.animation = animation
        self.text_message = text_message
        self.mode = mode
        self.sound = sound

        self.link_button_text = link_button_text
        self.button_yes_text = button_yes_text
        self.button_no_text = button_no_text

        self.setup_gui()

        # SET STYLESHEET
        self.set_stylesheet(
            bg_color,
            font_family,
            font_style,
            font_weight,
            font_size,
            text_color
        )

        self.widget_position(pos_mode, pos_x, pos_y)

    def setup_gui(self):
        self.setWindowFlags(self.win_flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)
        self.main_frame = QFrame()
        self.layout.addWidget(self.main_frame)

        self.main_frame_layout = QVBoxLayout(self.main_frame)
        self.main_frame_layout.setContentsMargins(20,20,20,20)
        self.main_frame_layout.setSpacing(20)

        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0,0,0,0)
        self.top_layout.setSpacing(20)

        self.middle_layout = QHBoxLayout()
        self.middle_layout.setContentsMargins(0,0,0,0)
        self.middle_layout.setSpacing(20)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setContentsMargins(0,0,0,0)
        self.bottom_layout.setSpacing(10)

        self.main_frame_layout.addLayout(self.top_layout)
        self.main_frame_layout.addLayout(self.middle_layout)
        self.main_frame_layout.addLayout(self.bottom_layout)

        self.icon_svg = QSvgWidget()
        self.icon_svg.setFixedSize(30,30)
        self.top_layout.addWidget(self.icon_svg)

        self.l_message = QLabel()
        self.l_message.setStyleSheet(u"QLabel{"
                                     u"color: #FFFFFF;"
                                     u"font-family: 'Segoe UI';"
                                     u"font-size: 12px;"
                                     u"font-style: normal;"
                                     u"font-weight: 400;"
                                     u"border: none}")
        self.l_message.setText(QCoreApplication.translate("PyMessageBox", self.text_message))
        #self.l_message.setWordWrap(True)
        self.l_message.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.l_message.setMaximumWidth(400)
        self.top_layout.addWidget(self.l_message)

        if self.link_button_text:
            self.link_btn = QLabel()
            self.link_btn.setObjectName(f"{self.objectName()}__link_btn")
            self.link_btn.setStyleSheet(u"QLabel{"
                                     u"color: #FFFFFF;"
                                     u"font-family: 'Roboto';"
                                     u"font-size: 14px;"
                                     u"font-style: normal;"
                                     u"font-weight: 500;}")
            self.link_btn.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.link_btn.setText(f"<a href='link_btn'style='text-decoration:none;{Styles.STYLE_LINK}'>{self.link_button_text}</a>")
            self.link_btn.linkActivated.connect(self.btn_clicked)
            self.bottom_layout.addWidget(self.link_btn)

        #BUTTONS
        self.bottom_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.pbtn_yes = QPushButton()
        self.pbtn_yes.setObjectName('pbtn_yes')
        self.pbtn_yes.setText(QCoreApplication.translate("QPushButton", self.button_yes_text, None))
        self.pbtn_yes.clicked.connect(self.btn_clicked)
        self.pbtn_yes.setMinimumHeight(25)
        self.pbtn_yes.setMinimumWidth(80)
        self.pbtn_yes.setCursor(Qt.PointingHandCursor)
        self.bottom_layout.addWidget(self.pbtn_yes)

        self.pbtn_no = QPushButton()
        self.pbtn_no.setObjectName('pbtn_no')
        self.pbtn_no.setText(QCoreApplication.translate("QPushButton", self.button_no_text, None))
        self.pbtn_no.clicked.connect(self.btn_clicked)
        self.pbtn_no.setMinimumHeight(25)
        self.pbtn_no.setMinimumWidth(80)
        self.pbtn_no.setCursor(Qt.PointingHandCursor)
        self.bottom_layout.addWidget(self.pbtn_no)

        self.bottom_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.icon_svg.load(self.change_mode(self.mode))

        '''self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(self.shadow)'''

        self.resize_widget()


    def resize_widget(self):
        font = self.l_message.font()
        fontMetrics = QFontMetrics(font)
        textSize = fontMetrics.size(0, self.l_message.text())

        if textSize.width() > 400:
            width = self.icon_svg.width() + 460
        else:
            width = textSize.width() + self.icon_svg.width() + 60

        if textSize.height() > self.icon_svg.height():
            height = textSize.height() + 60
        else:
            height = self.icon_svg.height() + 60

        self.resize(width,height)


    def widget_position(self, pos_mode='center', pos_x=0, pos_y=0):
        frame_geometry = self.frameGeometry()
        parent_center = self.parent.frameGeometry().center()
        if pos_mode == 'center':
            point_position = parent_center
        elif pos_mode == 'right_top':
            point_position = QPoint(parent_center.x() + self.parent.frameGeometry().width()/2 - frame_geometry.width()/2 - pos_x,
                                    parent_center.y() - self.parent.frameGeometry().height()/2 + frame_geometry.height()/2 + pos_y)
        elif pos_mode == 'right_bottom':
            point_position = QPoint(parent_center.x() + self.parent.frameGeometry().width()/2 - frame_geometry.width()/2 - pos_x,
                                    parent_center.y() + self.parent.frameGeometry().height()/2 - frame_geometry.height()/2 - pos_y)
        frame_geometry.moveCenter(point_position)
        if self.animation == b'geometry':
            self.anim = QPropertyAnimation(self, self.animation)
            self.anim.setDuration(500)
            self.anim.setEasingCurve(QEasingCurve.OutBack)
            #self.animation.setEasingCurve(QEasingCurve.OutCubic)
            #self.animation.setEasingCurve(QEasingCurve.OutQuad)
            self.anim.setStartValue(QRect(parent_center.x() + self.parent.frameGeometry().width()/2,  frame_geometry.y(), frame_geometry.width(), frame_geometry.height()))
            self.anim.setEndValue(frame_geometry)
            self.anim.start(QAbstractAnimation.DeleteWhenStopped)
        else:
            self.move(frame_geometry.topLeft())


    def change_mode(self, mode=None):
        if mode == 'information':
            icon_path = Functions.set_svg_icon('info.svg')
            if not self.button_no_text:
                self.pbtn_no.setVisible(False)
        elif mode == 'question':
            icon_path = Functions.set_svg_icon('circle-help.svg')
        elif mode == 'warning':
            icon_path = Functions.set_svg_icon('alert-triangle.svg')
            if not self.button_no_text:
                self.pbtn_no.setVisible(False)
        else:
            icon_path = None
            self.icon_svg.setVisible(False)
        return icon_path


    def play_sound(self, sound_name):
        effect = QSoundEffect(QCoreApplication.instance())
        effect.setSource(QUrl.fromLocalFile(Functions.set_sound(sound_name)))
        effect.play()


    def showEvent(self, event):
        event.accept()
        if self.sound:
            self.play_sound(self.sound)


    def closeEvent(self, event):
        event.accept()

    def center(self):
        frame_geometry = self.frameGeometry()
        center_point = QPoint(self.parent.frameGeometry().width()/2, self.parent.frameGeometry().height()/2)
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


    def paintEvent(self, event):
        if QPoint(self.parent.frameGeometry().center()) != self.frameGeometry().center() \
                and not self.parent.isActiveWindow() \
                and not self.underMouse():
            self.widget_position(self.pos_mode, self.pos_x, self.pos_y)


    def __del__(self):
        pass

    # SET STYLESHEET
    def set_stylesheet(
        self,
        bg_color,
        font_family,
        font_style,
        font_weight,
        font_size,
        text_color
    ):
        # APPLY STYLESHEET
        style_format = Styles.style.format(
            _bg_color = bg_color,
            _text_color = text_color,
            _font_family = font_family,
            _font_style = font_style,
            _font_weight = font_weight,
            _font_size = font_size
        )
        self.setStyleSheet(style_format)


    def btn_clicked(self):
        if self.sender().objectName() == 'pbtn_yes':
            self.close()
            self.clicked.emit(self.sender())
            self.yes.emit()
        if self.sender().objectName() == 'pbtn_no':
            self.close()
            self.clicked.emit(self.sender())
            self.no.emit()
        if hasattr(self, 'link_btn') and self.sender().objectName() == self.link_btn.objectName():
            self.close()
            self.linkClicked.emit(self.sender())