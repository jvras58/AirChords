# 🎸 CV Rhythm Hero

Um jogo de ritmo inovador controlado por gestos das mãos usando a webcam! Demonstre suas habilidades musicais através de movimentos precisos dos dedos.

## 🛠️ Requisitos do Sistema

- Python 3.12 ou superior
- Webcam funcional
- Boa iluminação para detecção de mãos
- Sistema operacional: Windows, macOS ou Linux

## 📦 Instalação

Este projeto utiliza [uv](https://github.com/astral-sh/uv) para gerenciamento de dependências e ambientes virtuais.

1. Instale o uv (se ainda não tiver):
   ```bash
   # No Windows (PowerShell)
   iwr -useb https://astral.sh/uv/install.ps1 | iex
   ```

2. Clone ou baixe o repositório e navegue até a pasta do projeto.

3. Instale as dependências:
   ```bash
   make install
   # ou diretamente: uv sync
   ```

## 🚀 Execução

Para executar o jogo, use o comando:
```bash
make run
# ou diretamente: uv run cv_rhythm_game.py
```

## 🎮 Como Jogar

1. Execute o jogo conforme descrito acima.
2. Permita o acesso à sua webcam quando solicitado.
3. Posicione sua mão na frente da câmera com boa iluminação.
4. **Objetivo**: Notas coloridas cairão em 4 raias verticais.
5. **Gestos**: Quando uma nota atingir a linha branca na parte inferior da tela, faça um gesto de pinça juntando as pontas dos dedos:

   - 🟢 **Verde (Raia 1)**: Polegar + Indicador 👌
   - 🔴 **Vermelho (Raia 2)**: Polegar + Dedo Médio
   - 🟡 **Amarelo (Raia 3)**: Polegar + Anelar
   - 🔵 **Azul (Raia 4)**: Polegar + Mindinho 🤟

6. **Pontuação**: Acerte as notas no ritmo para aumentar sua pontuação e combo!
7. **Dicas**: Mantenha a mão relaxada e bem iluminada para melhor detecção.

## 🎵 Música Personalizada

O jogo inclui um sintetizador simples integrado, mas para uma experiência imersiva completa:

1. Obtenha qualquer arquivo de música no formato .mp3.
2. Renomeie o arquivo para `musica.mp3`. - Alceu Valença - Anunciação - Karaokê (Nosso exemplo no musica.mp3)
3. Coloque-o na raiz do projeto (mesma pasta do `cv_rhythm_game.py`).
4. Reinicie o jogo.

**Mecânica de Música**: O jogo utiliza "Volume Ducking". A música tocará em volume baixo se você errar ou não interagir. Quando você acerta as notas no ritmo correto, o volume aumenta, criando a sensação de que você está tocando a música ao vivo!

## 🛠️ Desenvolvimento

- **Estrutura do Projeto**:
  - `cv_rhythm_game.py`: Arquivo principal do jogo
  - `pyproject.toml`: Configuração do projeto e dependências
  - `Makefile`: Comandos de automação
  - `README.md`: Este arquivo

- **Dependências Principais**:
  - `pygame`: Para interface gráfica e áudio
  - `opencv-python`: Para processamento de vídeo da webcam
  - `mediapipe`: Para detecção de mãos e gestos
  - `numpy`: Para cálculos numéricos

Para contribuir ou modificar o código, certifique-se de que as mudanças sejam testadas em diferentes condições de iluminação e posições de mão.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Divirta-se tocando com as mãos!** 🎶