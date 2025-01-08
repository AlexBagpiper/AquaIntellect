# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from core.functions import Functions

from . style import *

# PY PUSH BUTTON
# ///////////////////////////////////////////////////////////////
class PyPlainTextEdit(QPlainTextEdit):
    def __init__(
        self,
        parent = None,
        obj_name = None,
        text = "",
        place_holder_text = "",
        border_radius = 8,
        border_size = 2,
        border_color = "#343b48",
        margin = 5,
        spacing = 5,
        bg_color = "#2c313c",
        bg_color_active = "#2c313c",
        selection_color = "#2c313c",
        context_color = "#2c313c",
        text_color = "#8a95aa",
        place_holder_text_color = "#8a95aa",
        font_family = 'Segoe UI',
        font_style = 'normal',
        font_weight = '400',
        font_size = '12px',
        scroll_bar_bg_color = "#8a95aa",
        scroll_bar_btn_color = "#2c313c",
        max_height = 60,
        blur_radius = 5,
        align = Qt.AlignVCenter | Qt.AlignLeft,
        popup_window = False,
        popup_window_pos = 'right',
        vertical_margin = 40,
        horisontal_margin = 10
    ):
        super().__init__()

        self.parent = parent

        if parent != None:
            self.setParent(parent)

        # PARAMETERS
        if obj_name:
            self.setObjectName(obj_name)
        else:
            self.setObjectName('py_plain_text_edit')

        if text:
            self.setPlainText(QCoreApplication.translate("QPlainTextEdit", text, None))

        if place_holder_text:
            self.setPlaceholderText(QCoreApplication.translate("QPlainTextEdit", place_holder_text, None))

        self.popup_window = popup_window
        self.popup_window_pos = popup_window_pos

        self.max_height = max_height

        self.bg_color = bg_color
        self.font_family = font_family
        self._vertical_margin = vertical_margin
        self._horisontal_margin = horisontal_margin

        self.setPopupWindow(self.popup_window)

        # SET STYLESHEET
        self.set_stylesheet(
            border_radius,
            border_size,
            border_color,
            text_color,
            place_holder_text_color,
            font_family,
            font_style,
            font_weight,
            font_size,
            selection_color,
            bg_color,
            bg_color_active,
            context_color,
            scroll_bar_bg_color,
            scroll_bar_btn_color
        )


    def __del__(self):
        pass

    # SET STYLESHEET
    def set_stylesheet(
        self,
        border_radius,
        border_size,
        border_color,
        text_color,
        place_holder_text_color,
        font_family,
        font_style,
        font_weight,
        font_size,
        selection_color,
        bg_color,
        bg_color_active,
        context_color,
        scroll_bar_bg_color,
        scroll_bar_btn_color
    ):
        # APPLY STYLESHEET
        style_format = style.format(
            _border_radius = border_radius,
            _border_size = border_size,
            _border_color = border_color,
            _text_color = text_color,
            _place_holder_text_color = place_holder_text_color,
            _font_family = font_family,
            _font_style = font_style,
            _font_weight = font_weight,
            _font_size = font_size,
            _selection_color = selection_color,
            _bg_color = bg_color,
            _bg_color_active = bg_color_active,
            _context_color = context_color,
            _scroll_bar_bg_color = scroll_bar_bg_color,
            _scroll_bar_btn_color = scroll_bar_btn_color
        )
        self.setStyleSheet(style_format)


    def paintEvent(self, event):
        min_height = self.document().lineCount() * QFontMetrics(self.font()).lineSpacing() + 2 * self.document().documentMargin() + 13
        if min_height > self.max_height: min_height = self.max_height
        self.setMinimumHeight(min_height)
        super().paintEvent(event)


    def resizeEvent(self, event):
        self.updateGeometry()
        super().resizeEvent(event)


    def enterEvent(self, event):
        pass
        """if self.popup_window and self.isEnabled():
            self.move_popup()"""


    def leaveEvent(self, event):
        pass


    def move_popup(self):
        gp = self.mapToGlobal(QPoint(0, 0))
        pos = self.parent.mapFromGlobal(gp)

        if self.popup_window_pos == 'bottom':
            pos_x = (pos.x() - (self.popup_window.width() // 2)) + (self.width() // 2)
            pos_y = pos.y() + self._vertical_margin
        elif self.popup_window_pos == 'left':
            pos_y = (pos.y() - (self.popup_window.height() // 2)) + (self.height() // 2)
            pos_x = pos.x() - self.popup_window.width() - self._horisontal_margin
        elif self.popup_window_pos == 'right':
            pos_y = (pos.y() - (self.popup_window.height() // 2)) + (self.height() // 2)
            pos_x = pos.x() + self.width() + self._horisontal_margin
        else:
            pos_x = (pos.x() - (self.popup_window.width() // 2)) + (self.width() // 2)
            pos_y = pos.y() - self._vertical_margin

        self.popup_window.move(pos_x, pos_y)


    def setPopupWindow(self, enabled, pos='right'):
        if enabled:
            self.popup_window = PopupWindow(parent=self.parent,
                                            wid_parent=self,
                                            font_family=self.font_family,
                                            bg_color=self.bg_color)
            self.popup_window_width = self.popup_window.width()
            self.popup_window_pos = pos
            self.popup_window.hide()


    def setPopupTitleText(self, text):
        if self.popup_window:
            self.popup_window.setTitleText(text)


    def setPopupDescriptionText(self, text):
        if self.popup_window:
            self.popup_window.setDescriptionText(text)


    def setPopupButton(self, enabled, text):
        if self.popup_window:
            self.popup_window.setButton(enabled, text)


    def setPopupButtonText(self, text):
        if self.popup_window:
            self.popup_window.setButtonText(text)




class PopupWindow(QFrame):
    style_popup_image = """ 
    QLabel#l_title {{		
        background-color: {_bg_color};	
        border: none;
        color: {_text_color};
        font-family: {_font_family};
        font-weight: {_font_weight_1};
        font-size: {_font_size_1}px;
    }}
    QLabel#l_description {{		
        background-color: {_bg_color};	
        border: none;
        color: {_text_color};
        font-family: {_font_family};
        font-weight: {_font_weight_2};
        font-size: {_font_size_2}px;
    }}
    QFrame#content_frame {{
        background: {_bg_color};		
        border-radius: 5px;
        border: none;
    }}
    QPushButton {{
        padding-left: 10px;
        padding-right: 10px;
        border: 1px solid #5668E8;
        color: #5668E8;
        border-radius: 5px;	
        background-color: #FFFFFF;
        font-family: {_font_family};
        font-weight: 400;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: #FFFFFF;
        color: #95A1F1;
        border: 1px solid #95A1F1;
    }}
    QPushButton:pressed {{	
        background-color: #F4F4F4;
        color: #5668E8;
        border: 1px solid #5668E8;
    }}
    """

    def __init__(
        self,
        parent,
        wid_parent,
        bg_color,
        text_color='#464857',
        font_family='Roboto',
        font_weight_1='500',
        font_weight_2='400',
        font_size_1='14px',
        font_size_2='14px',
        title_text = '',
        description_text = '',
        popup_btn = False,
        popup_btn_text = ''
    ):
        QFrame.__init__(self)

        self.parent = parent

        self.wid_parent = wid_parent
        self.popup_btn_text = popup_btn_text

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.corner = QLabel()
        self.corner.setPixmap(QPixmap(Functions.set_image('corner.png')))

        self.content_frame = QFrame(self)
        self.content_frame.setObjectName('content_frame')
        self.content_frame.setMaximumWidth(500)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(10,10,10,10)
        self.content_layout.setSpacing(10)

        self.l_title = QLabel()
        self.l_title.setObjectName('l_title')
        self.l_title.setText(title_text)
        self.l_title.setAlignment(Qt.AlignLeft)
        #self.l_title.setWordWrap(True)
        self.l_title.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        #self.l_title.setMinimumWidth(250)
        self.content_layout.addWidget(self.l_title)

        self.l_description = QLabel()
        self.l_description.setObjectName('l_description')
        self.l_description.setText(description_text)
        self.l_description.setAlignment(Qt.AlignLeft)
        self.l_description.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.l_description.setWordWrap(True)
        self.content_layout.addWidget(self.l_description)

        self.setButton(popup_btn, popup_btn_text)

        self.popup_flag = False

        # LABEL SETUP
        style = self.style_popup_image.format(_bg_color = bg_color,
                                              _text_color = text_color,
                                              _font_family = font_family,
                                              _font_weight_1 = font_weight_1,
                                              _font_weight_2 = font_weight_2,
                                              _font_size_1 = font_size_1,
                                              _font_size_2 = font_size_2)
        self.setObjectName(u"popup_window")
        self.setStyleSheet(style)
        self.setMinimumHeight(34)
        self.setParent(parent)

        self.layout.addWidget(self.corner)
        self.layout.addWidget(self.content_frame)

        self.adjustSize()

        # SET DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)


    def setTitleText(self,text):
        self.l_title.setText(text)
        self.adjustSize()

    def titleText(self):
        return self.l_title.text()


    def setDescriptionText(self,text):
        self.l_description.setText(text)
        self.adjustSize()

    def descriptionText(self):
        return self.l_description.text()


    def setButton(self, enabled, text):
        if enabled:
            self.popup_btn = QPushButton(self)
            self.popup_btn.setObjectName('popup_btn')
            self.popup_btn.setMinimumHeight(25)
            self.popup_btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
            self.popup_btn.setText(text)
            self.content_layout.addWidget(self.popup_btn)
            self.popup_btn.clicked.connect(self.btn_clicked)
            self.wid_parent = self.wid_parent
            self.adjustSize()

    def setButtonText(self,text):
        if self.popup_btn:
            self.popup_btn.setText(text)
            self.adjustSize()

    def buttonText(self):
        if self.popup_btn: return self.popup_btn.text()


    def enterEvent(self, event):
        self.popup_flag = True

    def leaveEvent(self, event):
        self.popup_flag = False


    def paintEvent(self, event):
        self.adjustSize()
        super().paintEvent(event)


    def btn_clicked(self):
        if self.sender().objectName() == 'popup_btn':
            self.wid_parent.setText(self.descriptionText())
            self.hide()




