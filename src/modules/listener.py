"""A keyboard listener to track user inputs."""

import os
import threading
import time
import winsound
from datetime import datetime

import keyboard as kb

from src.common import config, utils
from src.common.interfaces import Configurable


class KeyBoardEvent:
    @staticmethod
    def toggle_enabled():
        """Resumes or pauses the current routine. Plays a sound to notify the user."""

        config.bot.rune_active = False

        if not config.enabled:
            KeyBoardEvent.recalibrate_minimap()  # Recalibrate only when being enabled.

        config.enabled = not config.enabled
        utils.print_state()

        if config.enabled:
            winsound.Beep(784, 333)  # G5
        else:
            winsound.Beep(523, 333)  # C5
        time.sleep(0.267)

    @staticmethod
    def reload_routine():
        KeyBoardEvent.recalibrate_minimap()

        config.routine.load(config.routine.path)

        winsound.Beep(523, 200)  # C5
        winsound.Beep(659, 200)  # E5
        winsound.Beep(784, 200)  # G5

    @staticmethod
    def recalibrate_minimap():
        config.capture.calibrated = False
        while not config.capture.calibrated:
            time.sleep(0.01)
        config.gui.edit.minimap.redraw()

    @staticmethod
    def record_position():
        pos = tuple("{:.3f}".format(round(i, 3)) for i in config.player_pos)
        now = datetime.now().strftime("%I:%M:%S %p")
        config.gui.edit.record.add_entry(now, pos)
        print(f"\n[~] Recorded position ({pos[0]}, {pos[1]}) at {now}")
        time.sleep(0.6)

    @staticmethod
    def record_keypress():
        fname = input("Name of new command: ")
        OUTPATH = os.path.join(config.CUSTOM_CMD_DIR, fname)

        print("Start recording now. ")
        print("STOP RECORDING by pressing [esc]")
        rec_kp = kb.record(until="esc")
        with open(OUTPATH, "w") as fout:
            for i in range(len(rec_kp)):
                fout.write(rec_kp[i].to_json() + "\n")
        time.sleep(0.01)


class Listener(Configurable):
    DEFAULT_CONFIG = {
        "Start/stop": "insert",
        "Reload routine": "f6",
        "Record position": "f7",
        "Record key press": "f8",
    }
    BLOCK_DELAY = 1  # Delay after blocking restricted button press

    def __init__(self):
        """Initializes this Listener object's main thread."""

        super().__init__("controls")
        config.listener = self

        self.enabled = False
        self.ready = False
        self.block_time = 0
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print("\n[~] Started keyboard listener")
        self.thread.start()

    def _main(self):
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """

        self.ready = True
        while True:
            if self.enabled:
                if kb.is_pressed(self.config["Start/stop"]):
                    KeyBoardEvent.toggle_enabled()
                elif kb.is_pressed(self.config["Reload routine"]):
                    KeyBoardEvent.reload_routine()
                elif kb.is_pressed(self.config["Record key press"]):
                    KeyBoardEvent.record_keypress()
                elif self.restricted_pressed("Record position"):
                    KeyBoardEvent.record_position()
            time.sleep(0.01)

    def restricted_pressed(self, action):
        """Returns whether the key bound to ACTION is pressed only if the bot is disabled."""

        if kb.is_pressed(self.config[action]):
            if not config.enabled:
                return True
            now = time.time()
            if now - self.block_time > Listener.BLOCK_DELAY:
                print(
                    f"\n[!] Cannot use '{action}' while Auto Maple is enabled"
                )
                self.block_time = now
        return False
