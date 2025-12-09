"""Carregador de dados de acordes.

Responsável por carregar dados de acordes a partir de arquivos JSON
ou utilizar dados padrão quando o arquivo não está disponível.
"""

import json
import os

from src.utils.config import DADOS_CHORDS_PADRAO
from src.utils.paths import get_assets_path


def load_chords(json_path=None):
    """Carrega dados de acordes de um arquivo JSON.

    Args:
        json_path: Caminho opcional para o arquivo JSON de acordes.
            Se None, usa o caminho padrão em assets.

    Returns:
        list: Lista de dicionários com informações dos acordes.
    """
    if json_path is None:
        json_path = os.path.join(get_assets_path(), "chords.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return DADOS_CHORDS_PADRAO
