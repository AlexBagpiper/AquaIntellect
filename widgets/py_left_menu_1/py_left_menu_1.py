# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

# IMPORT BUTTON AND DIV
# ///////////////////////////////////////////////////////////////
from . py_left_menu_button import PyLeftMenuButton
from . py_div import PyDiv

# IMPORT FUNCTIONS
# ///////////////////////////////////////////////////////////////
from core.functions import *

# PY LEFT MENU
# ///////////////////////////////////////////////////////////////
class PyLeftMenu1(QWidget):
    # SIGNALS
    clicked = Signal(object)
    released = Signal(object)

    def __init__(
        self,
        parent = None,
        app_parent = None,
        dark_one = "#1b1e23",
        dark_three = "#21252d",
        dark_four = "#272c36",
        bg_one = "#2c313c",
        icon_color = "#c3ccdf",
        icon_color_hover = "#dce1ec",
        icon_color_pressed = "#edf0f5",
        icon_color_active = "#f5f6f9",
        context_color = "#568af2",
        duration_time = 500,
        radius = 8,
        minimum_width = 200,
        maximum_width = 240
    ):
        super().__init__()

        # PROPERTIES
        # ///////////////////////////////////////////////////////////////
        self._dark_one = dark_one
        self._dark_three = dark_three
        self._dark_four = dark_four
        self._bg_one = bg_one
        self._icon_color = icon_color
        self._icon_color_hover = icon_color_hover
        self._icon_color_pressed = icon_color_pressed
        self._icon_color_active = icon_color_active
        self._context_color = context_color
        self._duration_time = duration_time
        self._radius = radius
        self._minimum_width = minimum_width
        self._maximum_width = maximum_width

        # SET PARENT
        self._parent = parent
        self._app_parent = app_parent

        # SETUP WIDGETS
        self.setup_ui()

        # SET BG COLOR
        self.bg.setStyleSheet(f"background: {dark_one}; border-radius: {radius};")


        # ADD TO BOTTOM LAYOUT
        # ///////////////////////////////////////////////////////////////
        self.div_bottom = PyDiv(dark_four)
        self.div_bottom.hide()
        self.bottom_layout.addWidget(self.div_bottom)

    def __del__(self):
        pass

    # ADD BUTTONS TO LEFT MENU
    # Add btns and emit signals
    # ///////////////////////////////////////////////////////////////
    def add_menus(self, parameters):
        idx = 0
        if parameters != None:
            for parameter in parameters:
                _btn_id = parameter['btn_id']
                _is_active = parameter['is_active']
                _is_status_checked = parameter['is_status_checked']
                _text = parameter['text']

                if 'place' in parameter:
                    _place = parameter['place']
                else:
                    _place = 'top'

                self.menu = PyLeftMenuButton(
                    self._app_parent,
                    text = _text,
                    place = _place,
                    btn_id = _btn_id,
                    dark_one = self._dark_one,
                    dark_three = self._dark_three,
                    dark_four = self._dark_four,
                    bg_one = self._bg_one,
                    icon_color = self._icon_color,
                    icon_color_hover = self._icon_color_hover,
                    icon_color_pressed = self._icon_color_pressed,
                    icon_color_active = self._icon_color_active,
                    context_color = self._context_color,
                    is_active = _is_active,
                    is_status_checked = _is_status_checked,
                )
                self.menu.clicked.connect(self.btn_clicked)

                # ADD TO LAYOUT
                if _place == 'top':
                    self.top_layout.addWidget(self.menu)
                elif _place == 'bottom':
                    self.bottom_layout.addWidget(self.menu)

    def clear_top_menus(self):
        children = self.findChildren(PyLeftMenuButton)
        if children:
            for child in children:
                if child.place() == 'top':
                    child.setParent(None)
                    child._deleteLater()

    def delete_menu(self, btn_id):
        children = self.findChildren(PyLeftMenuButton)
        if children:
            for child in children:
                if child.btn_id() == btn_id:
                    child.setParent(None)
                    child._deleteLater()

    def top_menus_count(self):
        count = 0
        children = self.findChildren(PyLeftMenuButton)
        if children:
            for child in children:
                if child.place() == 'top':
                    count += 1
        return count

    # LEFT MENU EMIT SIGNALS
    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self):
        self.clicked.emit(self.menu)
        self.select_only_one(self.sender().objectName())

    # SELECT ONLY ONE BTN
    # ///////////////////////////////////////////////////////////////
    def select_only_one(self, widget: str):
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == widget:
                btn.set_active(True)
            else:
                btn.set_active(False)

    # SELECT ONLY ONE TAB BTN
    # ///////////////////////////////////////////////////////////////
    def select_only_one_tab(self, widget: str):
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == widget:
                btn.set_active_tab(True)
            else:
                btn.set_active_tab(False)

    # DESELECT ALL BTNs
    # ///////////////////////////////////////////////////////////////
    def deselect_all(self):
        for btn in self.findChildren(QPushButton):
            btn.set_active(False)


    # SETUP APP
    # ///////////////////////////////////////////////////////////////
    def setup_ui(self):
        # ADD MENU LAYOUT
        self.left_menu_layout = QVBoxLayout(self)
        self.left_menu_layout.setContentsMargins(0,0,0,0)

        # ADD BG
        self.bg = QFrame()

        # TOP FRAME
        #self.top_frame = QFrame()

        # BOTTOM FRAME
        #self.bottom_frame = QFrame()

        # ADD LAYOUTS
        self._layout = QVBoxLayout(self.bg)
        self._layout.setContentsMargins(0,0,0,0)

        # TOP LAYOUT
        self.top_layout = QVBoxLayout(self.bg)
        self.top_layout.setContentsMargins(5,5,5,5)
        self.top_layout.setSpacing(5)

        self.center_layout = QVBoxLayout(self.bg)
        self.center_layout.setContentsMargins(0,0,0,0)
        self.center_layout.setSpacing(0)
        self.center_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))

        # BOTTOM LAYOUT
        self.bottom_layout = QVBoxLayout(self.bg)
        self.bottom_layout.setContentsMargins(5,5,5,5)
        self.bottom_layout.setSpacing(5)

        # ADD TOP AND BOTTOM FRAME
        #self._layout.addWidget(self.top_frame, 0, Qt.AlignTop)
        #self._layout.addWidget(self.bottom_frame, 0, Qt.AlignBottom)

        self._layout.addLayout(self.top_layout, Qt.AlignTop)
        self._layout.addLayout(self.center_layout)
        self._layout.addLayout(self.bottom_layout, Qt.AlignBottom)

        # ADD BG TO LAYOUT
        self.left_menu_layout.addWidget(self.bg)



        

