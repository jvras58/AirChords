import os
import sys


def get_assets_path():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "assets")
    else:
        return "src/assets"
