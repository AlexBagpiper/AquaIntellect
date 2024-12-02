# -*- coding: utf-8 -*-

class Styles(object):
    style = """
    QFrame {{
	    background: {_bg_color};
	    border-radius: 8px;
	    border: 1px solid #4f5b6e;
    }}
    QLabel {{
        text-color: {_text_color};
        font-family: {_font_family};
        font-style: {_font_style};
        font-weight: {_font_weight};
        font-size: {_font_size};
    }} 
    QPushButton {{
        border: 1px solid #4f5b6e;
        padding-left: 10px;
        padding-right: 10px;
        color: '#FFFFFF';
        border-radius: 5px;	
        background-color: none;
        text-align: center;
        font-family: Segoe UI;
        font-style: normal;
        font-weight: 400;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: #272c36;
        border: 1px solid #4f5b6e;
        color: '#dce1ec';
    }}
    QPushButton:pressed {{	
        background-color: #6c99f4;
        border: 1px solid #4f5b6e;
        color: '#FFFFFF';
    }}
    """

    STYLE_LINK = '''
            color: #FFFFFF;
            font-family: Segoe UI;
            font-style: normal;
            font-weight: 500;
            font-size: 14px;
            '''


