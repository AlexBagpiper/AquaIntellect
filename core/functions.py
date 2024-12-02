# -*- coding: utf-8 -*-

from import_core import *

from config.file_path import *

# APP FUNCTIONS
# ///////////////////////////////////////////////////////////////
class Functions:

    # SET SVG ICON
    # ///////////////////////////////////////////////////////////////
    def set_svg_icon(icon_name):
        path = os.path.join(IMAGES_PATH, 'svg_icons')
        icon = os.path.normpath(os.path.join(path, icon_name))
        return icon

    # SET SVG IMAGE
    # ///////////////////////////////////////////////////////////////
    def set_svg_image(icon_name):
        path = os.path.join(IMAGES_PATH, 'svg_images')
        icon = os.path.normpath(os.path.join(path, icon_name))
        return icon

    # SET PNG ICON
    # ///////////////////////////////////////////////////////////////
    def set_png_icon(icon_name):
        path = os.path.join(IMAGES_PATH, 'png_icons')
        icon = os.path.normpath(os.path.join(path, icon_name))
        return icon

    # SET GIF ICON
    # ///////////////////////////////////////////////////////////////
    def set_gif_icon(icon_name):
        path = os.path.join(IMAGES_PATH, 'gif_icons')
        icon = os.path.normpath(os.path.join(path, icon_name))
        return icon

    # SET IMAGE
    # ///////////////////////////////////////////////////////////////
    def set_image(image_name):
        path = os.path.join(IMAGES_PATH, 'images')
        image = os.path.normpath(os.path.join(path, image_name))
        return image

    # DELETE FILE
    # ///////////////////////////////////////////////////////////////
    def del_file(folder, file):
        try:
            if os.path.isfile(Path(APP_PATH, folder, file)): os.remove(Path(APP_PATH, folder, file))
            return True
        except Exception as e:
            return False

    # SET SOUND
    # ///////////////////////////////////////////////////////////////
    def set_sound(sound_name):
        sound = os.path.normpath(os.path.join(SOUNDS_PATH, sound_name))
        return sound

    # GET HWID
    # ///////////////////////////////////////////////////////////////
    def get_hwid() -> str:
        hwid = 'NeuroVision'
        try:
            os_type = sys.platform.lower()
            if "win" in os_type:
                command = "wmic bios get serialnumber"
            elif "linux" in os_type:
                command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
            elif "darwin" in os_type:
                command = "ioreg -l | grep IOPlatformSerialNumber"
            hwid = os.popen(command).read().replace("\n","").replace("	","").replace(" ","")
        except:
            hwid = str(uuid.uuid1(uuid.getnode(), 0))[24:]
        finally:
            hwid_hash = hashlib.sha256(hwid.encode('utf-8'))
        return hwid_hash.hexdigest()

    # GET FILE MD5
    # ///////////////////////////////////////////////////////////////
    def get_file_md5(file):
        try:
            with open(file, 'rb') as f:
                data = f.read()
                md5_returned = hashlib.md5(data).hexdigest()
            return md5_returned
        except Exception as e:
            return False

    # CHECK SERVER AVAILABLE
    # ///////////////////////////////////////////////////////////////
    def server_available(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except:
            return False
        finally:
            s.close()







