# -*- coding: utf-8 -*-

# STYLE
# ///////////////////////////////////////////////////////////////
style = '''
QPlainTextEdit {{
	background-color: {_bg_color};
	border-radius: {_border_radius}px;
	border: {_border_size}px solid {_border_color};
	padding-left: 10px;
    padding-right: 5px;
    padding-top: 5px;
    padding-bottom: 5px;
	selection-color: {_text_color};
	selection-background-color: {_border_color};
    color: {_place_holder_text_color};
    font-family: {_font_family};
    font-style: {_font_style};
    font-weight: {_font_weight};
    font-size: {_font_size};
}}
QPlainTextEdit:focus {{
	border: {_border_size}px solid {_context_color};
    background-color: {_bg_color_active};
    color: {_text_color};
}}

QScrollBar:vertical {{
	border: none;
    background: {_scroll_bar_bg_color};
    width: 4px;
    margin: 0 0 0 0;
	border-radius: 2px;
}}
QScrollBar::handle:vertical {{	
	background: {_scroll_bar_btn_color};
    min-height: 10px;
	border-radius: 2px
}}
QScrollBar::add-line:vertical {{
        border: none;
        background: none;
        height: 20px;
	    border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }}
QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
        height: 20px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
     background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
     background: none;
}}



    




'''