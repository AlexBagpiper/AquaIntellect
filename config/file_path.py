# -*- coding: utf-8 -*-

from import_core import *

# Debug status change in production
DEBUG = True

path = ConfigParser()
path.read(Path(Path.cwd(), 'config', 'file_path.cfg'))

if DEBUG:
    APP_PATH = Path.cwd()
    IMAGES_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Images'))
    MODELS_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Models'))
    SOUNDS_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Sounds'))
    THEMES_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Themes'))
    TEMPLATES_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Templates'))
    PDFVIEWER_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'PdfViewer'))
    TEMP_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Temp'))
    LOG_PATH = Path(Path.cwd(), path.get('MAIN_DIR', 'Log'))

    COMMON_DATABASE_TEMPLATE_PATH = Path('database', 'templates', path.get('DATABASE', 'common_default'))
    COMMON_DATABASE_PATH = Path('database', path.get('DATABASE', 'common'))
    DATABASE_ENCRYPTION = False

    SETTINGS = Path(Path.cwd(), path.get('JSON', 'Settings'))
else:
    APP_PATH = Path.cwd()
    IMAGES_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Images'))
    MODELS_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Models'))
    SOUNDS_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Sounds'))
    THEMES_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Themes'))

    TEMPLATES_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Templates'))
    PDFVIEWER_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'PdfViewer'))
    TEMP_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Temp'))
    LOG_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Log'))

    DATABASE_TEMPLATE_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Database'), 'templates', path.get('DATABASE', 'common_default'))
    DATABASE_PATH = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('MAIN_DIR', 'Database'), path.get('DATABASE', 'common'))
    DATABASE_ENCRYPTION = True

    SETTINGS = Path(os.environ['ALLUSERSPROFILE'], path.get('MAIN_DIR', 'MainDir'), path.get('JSON', 'Settings'))

