# -*- coding: utf-8 -*-

# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

# IMPORT FUNCTIONS
# ///////////////////////////////////////////////////////////////
from core.functions import *

# CUSTOM LEFT MENU
# ///////////////////////////////////////////////////////////////
class PyLeftMenuButton(QPushButton):
    def __init__(
        self,
        app_parent,
        btn_id = None,
        margin = 4,
        text = 'test',
        place = 'top',
        dark_one = "#1b1e23",
        dark_three = "#21252d",
        dark_four = "#272c36",
        bg_one = "#2c313c",
        icon_color = "#c3ccdf",
        icon_color_hover = "#dce1ec",
        icon_color_pressed = "#edf0f5",
        icon_color_active = "#f5f6f9",
        context_color = "#568af2",
        icon_path = "icon_unchecked.svg",
        icon_status_unchecked = "icon_unchecked.svg",
        icon_status_checked = "icon_checked.svg",
        is_active = False,
        is_active_tab = False,
        is_toggle_active = False,
        is_status_checked = False,
    ):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setMaximumHeight(20)
        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setObjectName(btn_id)

        # APP PATH
        self._icon_path = Functions.set_svg_icon(icon_path)
        self._icon_active_menu = Functions.set_svg_icon(icon_path)

        self._icon_status_checked = Functions.set_svg_icon(icon_status_checked)
        self._icon_status_unchecked = Functions.set_svg_icon(icon_status_unchecked)

        # PROPERTIES
        self._text = text
        self._place = place
        self._margin = margin
        self._dark_one = dark_one
        self._dark_three = dark_three
        self._dark_four = dark_four
        self._bg_one = bg_one
        self._context_color = context_color
        self._icon_color = icon_color
        self._icon_color_hover = icon_color_hover
        self._icon_color_pressed = icon_color_pressed
        self._icon_color_active = icon_color_active
        self._set_icon_color = self._icon_color # Set icon color
        self._set_bg_color = self._dark_one # Set BG color
        self._parent = app_parent
        self._is_active = is_active
        self._is_active_tab = is_active_tab
        self._is_toggle_active = is_toggle_active
        self._is_status_checked = is_status_checked


    def __del__(self):
        pass

    def _deleteLater(self):
        self.deleteLater()

    def place(self):
        return self._place

    def btn_id(self):
        return self.objectName()

    # PAINT EVENT
    # ///////////////////////////////////////////////////////////////
    def paintEvent(self, event):
        # PAINTER
        p = QPainter()
        p.begin(self)
        p.setPen(Qt.NoPen)
        p.setRenderHint(QPainter.Antialiasing)

        # RECTANGLES
        #rect = QRect(4, 5, self.width(), self.height() - 5)
        #rect_inside = QRect(4, 5, self.width() - 8, self.height() - 5)
        #rect_icon = QRect(0, 0, 50, self.height())
        #rect_icon_status = QRect(50, 0, 120, self.height())


        if self._is_status_checked:
            self.icon_status = self._icon_status_checked
        else:
            self.icon_status = self._icon_status_unchecked

        if self._is_active:
            # BG INSIDE

            p.setBrush(QColor(self._bg_one))
            p.drawRoundedRect(event.rect(), 8, 8)

            # DRAW ACTIVE
            icon_path = self._icon_active_menu
            app_path = os.path.abspath(os.getcwd())
            self._set_icon_color = self._icon_color_active
            #self.icon_active(p, icon_path, self.width())

            # DRAW ICONS
            #self.icon_paint(p, self._icon_path, rect_icon, self._set_icon_color)
            #self.icon_paint(p, self.icon_status, rect_icon_status, self._set_icon_color)
            p.setPen(QColor(self._icon_color_pressed))
            self.drawText(event, p)
        # NORMAL BG
        else:
            # BG INSIDE
            p.setBrush(QColor(self._set_bg_color))
            p.drawRoundedRect(event.rect(), 8, 8)

            # DRAW ICONS
            #self.icon_paint(p, self._icon_path, rect_icon, self._set_icon_color)
            #self.icon_paint(p, self.icon_status, rect_icon_status, self._set_icon_color)
            p.setPen(QColor(self._icon_color))
            self.drawText(event, p)
        p.end()

    def drawText(self, event, p):
        p.setFont(QFont('Segoe UI', 9))
        p.drawText(event.rect(), Qt.AlignCenter, self._text)

    # SET ACTIVE MENU
    # ///////////////////////////////////////////////////////////////
    def set_active(self, is_active):
        self._is_active = is_active
        if not is_active:
            self._set_icon_color = self._icon_color
            self._set_bg_color = self._dark_one
        self.repaint()

    # SET BTN STATUS
    # ///////////////////////////////////////////////////////////////
    def set_status_checked(self, is_checked):
        self._is_status_checked = is_checked
        self.repaint()

    # RETURN IF IS ACTIVE MENU
    # ///////////////////////////////////////////////////////////////
    def is_active(self):
        return self._is_active

    # RETURN IF IS STATUS CHECKED
    # ///////////////////////////////////////////////////////////////
    def is_status_checked(self):
        return self._is_status_checked

    # SET ICON
    # ///////////////////////////////////////////////////////////////
    def set_icon(self, icon_path):
        self._icon_path = icon_path
        self.repaint()

    # DRAW ICON WITH COLORS
    # ///////////////////////////////////////////////////////////////
    def icon_paint(self, qp, image, rect, color):
        icon = QPixmap(image)
        painter = QPainter(icon)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(icon.rect(), color)
        qp.drawPixmap(
            (rect.width() - icon.width()) / 2,
            (rect.height() - icon.height()) / 2,
            icon
        )
        painter.end()

    # DRAW ACTIVE ICON / RIGHT SIDE
    # ///////////////////////////////////////////////////////////////
    def icon_active(self, qp, image, width):
        icon = QPixmap(image)
        painter = QPainter(icon)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(icon.rect(), self._bg_one)
        qp.drawPixmap(width - 5, 0, icon)
        painter.end()

    # CHANGE STYLES
    # Functions with custom styles
    # ///////////////////////////////////////////////////////////////
    def change_style(self, event):
        if event == QEvent.Enter:
            if not self._is_active:
                self._set_icon_color = self._icon_color_hover
                self._set_bg_color = self._dark_three
            self.repaint()
        elif event == QEvent.Leave:
            if not self._is_active:
                self._set_icon_color = self._icon_color
                self._set_bg_color = self._dark_one
            self.repaint()
        elif event == QEvent.MouseButtonPress:
            if not self._is_active:
                self._set_icon_color = self._context_color
                self._set_bg_color = self._dark_four
            self.repaint()
        elif event == QEvent.MouseButtonRelease:
            if not self._is_active:
                self._set_icon_color = self._icon_color_hover
                self._set_bg_color = self._dark_three
            self.repaint()

    # MOUSE OVER
    # Event triggered when the mouse is over the BTN
    # ///////////////////////////////////////////////////////////////
    def enterEvent(self, event):
        self.change_style(QEvent.Enter)

    # MOUSE LEAVE
    # Event fired when the mouse leaves the BTN
    # ///////////////////////////////////////////////////////////////
    def leaveEvent(self, event):
        self.change_style(QEvent.Leave)

    # MOUSE PRESS
    # Event triggered when the left button is pressed
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.change_style(QEvent.MouseButtonPress)
            return self.clicked.emit()

    # MOUSE RELEASED
    # Event triggered after the mouse button is released
    # ///////////////////////////////////////////////////////////////
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.change_style(QEvent.MouseButtonRelease)
            return self.released.emit()





    
