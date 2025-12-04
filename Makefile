# Makefile para o projeto pymusicy

.PHONY: install run clean

# Instalar dependências usando uv
install:
	uv sync

# Executar o jogo
run:
	uv run main.py

# Limpar arquivos temporários (se houver)
clean:
	@echo "Limpando arquivos temporários..."
	# Adicione comandos de limpeza se necessário