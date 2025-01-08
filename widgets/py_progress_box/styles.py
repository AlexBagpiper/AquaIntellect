# -*- coding: utf-8 -*-

class Styles(object):
    style = """
    QFrame {{
	    background: {_bg_color};
	    border-radius: 10px;
    }}
    QLabel {{
        text-color: {_text_color};
        font-family: {_font_family};
        font-style: {_font_style};
        font-weight: {_font_weight};
        font-size: {_font_size};
    }} 
    QPushButton {{
        border: 1px solid #E1E5FF;
        padding-left: 10px;
        padding-right: 10px;
        color: '#FFFFFF';
        border-radius: 5px;	
        background-color: none;
        text-align: center;
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 500;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: none;
        border: 2px solid #E1E5FF;
        color: '#FFFFFF';
    }}
    QPushButton:pressed {{	
        background-color: #BABCCC;
        border: 2px solid #E1E5FF;
        color: '#FFFFFF';
    }}
    """

    STYLE_LINK = '''
            color: #FFFFFF;
            font-family: Roboto;
            font-style: normal;
            font-weight: 500;
            font-size: 14px;
            '''


