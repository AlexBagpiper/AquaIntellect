# -*- coding: utf-8 -*-

# IMPORT CORE

# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from PySide6.QtSvg import *
from PySide6.QtCharts import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *
from PySide6.QtPrintSupport import *


import os
# OPTIMIZE OPENCV OPEN CAMERA SPEED.(import before cv2) IMPORTANT!!!
# ///////////////////////////////////////////////////////////////
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
# ADJUST QT FONT DPI FOR HIGHT SCALE AN 4K MONITOR
# ///////////////////////////////////////////////////////////////
os.environ["QT_FONT_DPI"] = "96"



import sys
import threading
import subprocess

import time
import datetime
import calendar

import uuid
import hashlib
#import sqleet

import cv2
#from PIL import Image
#import img2pdf
#from docxtpl import DocxTemplate, InlineImage

import numpy as np
import itertools
from operator import itemgetter, attrgetter, methodcaller
from collections.abc import Iterable
import math
#from scipy.signal import savgol_filter, find_peaks, butter, filtfilt, sosfilt
import scipy.stats as ScipyStats

#import psutil
import shutil
import logging
import locale

import sqlite3
import csv
#import pandas as pd

import socket
#import requests
import json
import asyncio
import qasync
#import httpx
import http.client
import mimetypes
from codecs import encode

from pathlib import Path
from configparser import ConfigParser

import matplotlib.pyplot as plt

from ultralytics import YOLO
import scipy.stats as st

#from PySide6 import QtGui, QtCore
#print(dir(QtCore))
