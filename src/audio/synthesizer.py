import pygame
import numpy as np
from src.utils.config import NOTAS_BASE, INTERVALOS


class Sintetizador:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.mixer.init()
        pygame.init()
        self.cache_acordes = {}

    def criar_onda(self, freq, duracao=1.0, volume=0.5):
        sample_rate = 44100
        n_samples = int(sample_rate * duracao)
        t = np.linspace(0, duracao, n_samples, False)

        # Síntese Aditiva para um som mais "piano elétrico" e menos "apito"
        # Fundamental + Harmônicos
        onda = 0.6 * np.sin(2 * np.pi * freq * t)
        onda += 0.3 * np.sin(2 * np.pi * freq * 2 * t)  # Oitava acima
        onda += 0.1 * np.sin(2 * np.pi * freq * 3 * t)  # Quinta da oitava

        # Envelope ADSR simples (Ataque rápido, Decay suave)
        envelope = np.exp(-3 * t)
        onda = onda * envelope * volume

        # Converter para 16-bit PCM
        onda = (onda * 32767).astype(np.int16)
        return np.column_stack((onda, onda))

    def gerar_acorde(self, nome_acorde_full):
        # Ex: "G:maj" ou "A:min"
        if nome_acorde_full in self.cache_acordes:
            return self.cache_acordes[nome_acorde_full]

        try:
            if ":" in nome_acorde_full:
                tonica, tipo = nome_acorde_full.split(":")
            else:
                tonica = nome_acorde_full
                tipo = "maj"

            freq_base = NOTAS_BASE.get(tonica, 261.63)
            intervalos = INTERVALOS.get(tipo, INTERVALOS["maj"])

            # Misturar as notas do acorde
            audio_final = None

            for semi_tons in intervalos:
                # Calcular frequência da nota do intervalo (f = f0 * 2^(n/12))
                freq_nota = freq_base * (2 ** (semi_tons / 12.0))
                onda_nota = self.criar_onda(freq_nota)

                if audio_final is None:
                    audio_final = onda_nota
                else:
                    audio_final = audio_final + onda_nota  # Soma as ondas

            # Normalizar para evitar distorção (clipping)
            max_val = np.max(np.abs(audio_final))
            if max_val > 0:
                audio_final = (audio_final / max_val * 32767).astype(np.int16)

            som = pygame.sndarray.make_sound(audio_final)
            self.cache_acordes[nome_acorde_full] = som
            return som
        except Exception as e:
            print(f"Erro ao gerar acorde {nome_acorde_full}: {e}")
            return None
