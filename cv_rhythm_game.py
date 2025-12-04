import cv2
import mediapipe as mp
import pygame
import numpy as np
import random
import math
import os

# --- CONFIGURAÇÕES DO JOGO ---
LARGURA_TELA = 800
ALTURA_TELA = 600
FPS = 30
TITULO = "CV Rhythm Hero - Use seus dedos!"

# Cores (R, G, B)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 100, 255)
AMARELO = (255, 255, 0)
ROXO = (128, 0, 128)
LARANJA = (255, 165, 0)

# Configurações das Raias (Lanes)
CORES_RAIAS = [VERDE, VERMELHO, AMARELO, AZUL]
NOME_DEDOS = ["Indicador", "Médio", "Anelar", "Mindinho"]
TECLAS_DEBUG = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]  # Fallback para teclado


# --- CLASSE DE ÁUDIO ---
class GerenciadorAudio:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.usando_mp3 = False

        # Tenta carregar música em formatos suportados
        formatos = ["musica.mp3", "musica.ogg", "musica.wav"]
        self.usando_mp3 = False
        for caminho_musica in formatos:
            if os.path.exists(caminho_musica):
                try:
                    pygame.mixer.music.load(caminho_musica)
                    pygame.mixer.music.set_volume(0.1)  # Começa baixo (silencio)
                    self.usando_mp3 = True
                    print(f"Música externa carregada de {caminho_musica}!")
                    break
                except Exception as e:
                    print(
                        f"Erro ao carregar {caminho_musica}: {e}. Tentando próximo formato..."
                    )
        if not self.usando_mp3:
            print(
                "Nenhuma música compatível encontrada. Usando sintetizador procedural."
            )

        # Sons sintetizados para fallback (Escala Pentatônica)
        self.sons_notas = []
        if not self.usando_mp3:
            frequencias = [261.63, 293.66, 329.63, 392.00]  # C4, D4, E4, G4
            for freq in frequencias:
                self.sons_notas.append(self.gerar_onda_senoidal(freq))

        # Sons de feedback
        self.som_erro = self.gerar_ruido_branco()

    def gerar_onda_senoidal(self, freq, duracao=0.3):
        sample_rate = 44100
        n_samples = int(sample_rate * duracao)
        t = np.linspace(0, duracao, n_samples, False)
        # Onda com decay suave para parecer um instrumento
        onda = np.sin(2 * np.pi * freq * t) * np.exp(-3 * t)
        onda = (onda * 32767).astype(np.int16)
        stereo = np.column_stack((onda, onda))
        return pygame.sndarray.make_sound(stereo)

    def gerar_ruido_branco(self, duracao=0.1):
        sample_rate = 44100
        n_samples = int(sample_rate * duracao)
        ruido = np.random.uniform(-1, 1, n_samples) * 0.3
        ruido = (ruido * 32767).astype(np.int16)
        stereo = np.column_stack((ruido, ruido))
        return pygame.sndarray.make_sound(stereo)

    def tocar_nota(self, indice_raia):
        if self.usando_mp3:
            # Se acertar, aumenta o volume da música (sensação de tocar)
            pygame.mixer.music.set_volume(1.0)
        else:
            # Se não tiver música, toca o tom sintetizado
            self.sons_notas[indice_raia].play()

    def tocar_erro(self):
        self.som_erro.play()
        if self.usando_mp3:
            pygame.mixer.music.set_volume(0.1)  # Abaixa volume no erro

    def iniciar_musica_fundo(self):
        if self.usando_mp3:
            pygame.mixer.music.play(-1)

    def atualizar(self):
        # Efeito de decaimento do volume se usar MP3
        if self.usando_mp3:
            vol_atual = pygame.mixer.music.get_volume()
            if vol_atual > 0.1:
                pygame.mixer.music.set_volume(max(0.1, vol_atual - 0.02))


# --- CLASSE DE DETECÇÃO DE MÃO ---
class DetectorMaos:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils
        # IDs das pontas dos dedos: 4=Polegar, 8=Indicador, 12=Médio, 16=Anelar, 20=Mindinho
        self.ids_pontas = [8, 12, 16, 20]
        self.estado_anterior = [
            False,
            False,
            False,
            False,
        ]  # Para evitar disparos contínuos

    def encontrar_maos(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        gestos_ativos = [
            False,
            False,
            False,
            False,
        ]  # [Indicador, Médio, Anelar, Mindinho]
        posicao_polegar = None

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

                # Obter coordenadas em pixels
                h, w, c = img.shape
                pontos = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    pontos.append((cx, cy))

                # Verificar distância entre Polegar (4) e os outros dedos
                if len(pontos) >= 21:
                    x4, y4 = pontos[4]
                    posicao_polegar = (x4, y4)

                    for i, id_dedo in enumerate(self.ids_pontas):
                        x_dedo, y_dedo = pontos[id_dedo]
                        # Distância Euclidiana
                        distancia = math.hypot(x4 - x_dedo, y4 - y_dedo)

                        # Limiar de toque (ajuste conforme necessário)
                        if distancia < 40:
                            cv2.circle(img, (x4, y4), 15, CORES_RAIAS[i], cv2.FILLED)
                            gestos_ativos[i] = True

        return img, gestos_ativos, posicao_polegar


# --- CLASSE DO JOGO ---
class JogoRitmo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("Arial", 30, bold=True)
        self.fonte_grande = pygame.font.SysFont("Arial", 60, bold=True)

        self.cap = cv2.VideoCapture(0)
        self.detector = DetectorMaos()
        self.audio = GerenciadorAudio()

        self.notas = []  # Lista de notas caindo
        self.velocidade_nota = 7
        self.raia_largura = LARGURA_TELA // 4

        self.pontuacao = 0
        self.combo = 0
        self.rodando = True
        self.game_over = False

        self.spawn_timer = 0
        self.audio.iniciar_musica_fundo()

    def desenhar_interface(self, frame_camera):
        # 1. Desenhar o fundo (Feed da Câmera escurecido)
        frame_camera = np.rot90(frame_camera)  # Rotaciona para Pygame
        frame_camera = cv2.cvtColor(frame_camera, cv2.COLOR_BGR2RGB)
        frame_camera = pygame.surfarray.make_surface(frame_camera)
        frame_camera = pygame.transform.scale(frame_camera, (LARGURA_TELA, ALTURA_TELA))

        # Escurecer o fundo para destacar as notas
        sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        sombra.set_alpha(150)
        sombra.fill((0, 0, 0))

        self.tela.blit(frame_camera, (0, 0))
        self.tela.blit(sombra, (0, 0))

        # 2. Desenhar as Raias e Linha de Acerto
        linha_acerto_y = ALTURA_TELA - 100
        pygame.draw.line(
            self.tela, BRANCO, (0, linha_acerto_y), (LARGURA_TELA, linha_acerto_y), 3
        )

        for i in range(4):
            x = i * self.raia_largura
            # Linhas divisórias
            pygame.draw.line(self.tela, (50, 50, 50), (x, 0), (x, ALTURA_TELA), 2)

            # Indicador de tecla/dedo na base
            cor = CORES_RAIAS[i]
            # Efeito visual se a "tecla" estiver pressionada
            if self.input_atual[i]:
                pygame.draw.rect(
                    self.tela, cor, (x, linha_acerto_y, self.raia_largura, 20)
                )
                pygame.draw.circle(
                    self.tela, cor, (x + self.raia_largura // 2, linha_acerto_y), 40, 4
                )
            else:
                pygame.draw.circle(
                    self.tela, cor, (x + self.raia_largura // 2, linha_acerto_y), 30, 2
                )

            # Nome do dedo
            texto_dedo = self.fonte.render(NOME_DEDOS[i][0:3], True, BRANCO)
            self.tela.blit(
                texto_dedo, (x + self.raia_largura // 2 - 15, ALTURA_TELA - 40)
            )

    def gerenciar_notas(self):
        # Spawning simples (pode ser melhorado com detecção de batida)
        self.spawn_timer += 1
        if self.spawn_timer > 30:  # A cada 30 frames (aprox 1 seg)
            if random.random() < 0.7:  # 70% de chance de spawnar
                raia = random.randint(0, 3)
                # Nota: [raia, y, ativa]
                self.notas.append([raia, -50, True])
            self.spawn_timer = 0

        # Atualizar posições
        linha_acerto_y = ALTURA_TELA - 100
        zona_acerto = 60  # Tolerância

        for nota in self.notas[:]:
            nota[1] += self.velocidade_nota  # Desce a nota

            raia = nota[0]
            y = nota[1]

            # Desenhar nota
            cor = CORES_RAIAS[raia]
            rect = (raia * self.raia_largura + 10, y, self.raia_largura - 20, 40)
            pygame.draw.rect(self.tela, cor, rect, border_radius=10)
            # Brilho interno
            pygame.draw.rect(
                self.tela,
                (255, 255, 255),
                (raia * self.raia_largura + 20, y + 10, self.raia_largura - 40, 20),
                2,
                border_radius=5,
            )

            # Lógica de Acerto (Verifica se está na zona E se o usuário apertou AGORA)
            distancia_centro = abs(y - linha_acerto_y)

            # Se passou da tela
            if y > ALTURA_TELA:
                self.notas.remove(nota)
                if nota[2]:  # Se ainda estava ativa (não foi acertada)
                    self.combo = 0
                    self.audio.tocar_erro()

            # Checar colisão
            # self.input_trigger[raia] é verdadeiro apenas no frame que o gesto começa
            elif distancia_centro < zona_acerto and nota[2]:
                if self.input_trigger[raia]:
                    self.pontuacao += 10 + self.combo
                    self.combo += 1
                    nota[2] = False  # Marca como acertada para não contar duas vezes
                    self.notas.remove(nota)  # Remove visualmente
                    self.audio.tocar_nota(raia)

                    # Efeito visual de acerto
                    x_hit = raia * self.raia_largura
                    pygame.draw.rect(
                        self.tela,
                        (255, 255, 255),
                        (x_hit, linha_acerto_y - 10, self.raia_largura, 20),
                    )

    def desenhar_hud(self):
        texto_score = self.fonte_grande.render(f"Score: {self.pontuacao}", True, BRANCO)
        texto_combo = self.fonte.render(
            f"Combo: x{self.combo}", True, AMARELO if self.combo > 5 else BRANCO
        )

        self.tela.blit(texto_score, (20, 20))
        self.tela.blit(texto_combo, (20, 80))

        # Instruções
        instrucao = self.fonte.render(
            "Junte o POLEGAR com outro dedo na hora certa!", True, (200, 200, 200)
        )
        instrucao_rect = instrucao.get_rect(
            center=(LARGURA_TELA // 2, ALTURA_TELA - 150)
        )
        self.tela.blit(instrucao, instrucao_rect)

    def executar(self):
        while self.rodando:
            self.clock.tick(FPS)

            # 1. Eventos Pygame (Quit e Teclado Debug)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.rodando = False

            # 2. Captura de Câmera e Visão Computacional
            sucesso, img = self.cap.read()
            if not sucesso:
                continue

            img = cv2.flip(img, 1)  # Espelhar para ficar intuitivo
            img, gestos, polegar_pos = self.detector.encontrar_maos(img)

            # 3. Processar Inputs (Gestos + Teclado para debug)
            keys = pygame.key.get_pressed()
            self.input_atual = [False] * 4
            self.input_trigger = [False] * 4  # Apenas no frame que iniciou o toque

            for i in range(4):
                # Ativa se o gesto for detectado OU a tecla for pressionada
                esta_pressionado = gestos[i] or keys[TECLAS_DEBUG[i]]

                self.input_atual[i] = esta_pressionado

                # Detectar borda de subida (apenas quando muda de False para True)
                if esta_pressionado and not self.detector.estado_anterior[i]:
                    self.input_trigger[i] = True

                # Atualizar estado anterior
                self.detector.estado_anterior[i] = esta_pressionado

            # 4. Desenhar e Atualizar Lógica do Jogo
            self.desenhar_interface(img)
            self.gerenciar_notas()
            self.desenhar_hud()
            self.audio.atualizar()

            pygame.display.flip()

        # Limpeza
        self.cap.release()
        pygame.quit()


if __name__ == "__main__":
    try:
        jogo = JogoRitmo()
        jogo.executar()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        pygame.quit()
