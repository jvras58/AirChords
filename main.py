"""Ponto de entrada principal do Chord Hero AI.

Inicia o jogo de gestos musicais.
"""

from src.game.engine import MusicGame

if __name__ == "__main__":
    game = MusicGame()
    game.run()
