"""A module for tracking useful in-game information."""

import ctypes
import threading
import time
from ctypes import wintypes

import cv2
import mss
import mss.windows
import numpy as np

from src.common import config, utils

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


# The` distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9

# Offset in pixels to adjust for windowed mode
WINDOWED_OFFSET_TOP = 36
WINDOWED_OFFSET_LEFT = 10

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = cv2.imread("assets/minimap_tl_template.png", 0)
MM_BR_TEMPLATE = cv2.imread("assets/minimap_br_template.png", 0)

MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread("assets/player_template.png", 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape


class CommandRecorder:
    def __init__(self):
        config.recorder = self
        self.frame = None
        self.minimap = {}
        self.minimap_ratio = 1
        self.minimap_smaple = None
        self.sct = None
        self.window = {"left": 0, "top": 0, "width": 1366, "height": 768}

        self.ready = False
        self.calibrated = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        print("\n[~] Started Keyboard Recorder")
        self.thread.start()

    def _main(self):
        return
