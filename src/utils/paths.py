"""Utilitários para resolução de caminhos de assets.

Suporta execução em modo desenvolvimento e empacotado com PyInstaller.
"""

import os
import sys


def get_assets_path():
    """Retorna o caminho para a pasta de assets.

    Returns:
        str: Caminho absoluto para a pasta assets, compatível com PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "assets")
    else:
        return "src/assets"
