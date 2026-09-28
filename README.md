# Mestres Arqueiros

Um jogo indie PvP de artilharia e combate balístico em turnos, desenvolvido em Python utilizando Pygame.
Totalmente construído proceduralmente sem dependência de sprites externos.

## Funcionalidades

- **PvP Local e PvE (Jogador vs IA)**
- **Física Balística Completa** com gravidade e influência de vento (opcional).
- **Três Tipos de Flechas**: Normal, Pesada e Explosiva (cada uma com propriedades e efeitos únicos).
- **Três Cenários Diferentes**: Floresta Antiga, Vale dos Arqueiros e Fortaleza Real.
- **Dano Localizado**: Acertos na cabeça causam dano crítico.
- **Efeitos Visuais**: Sistema de partículas, sangue estilizado, poeira, explosões, tremor de tela e dano flutuante.
- **Interface Completa**: Menu principal, tela de opções mutáveis, HUD dinâmico e tela de vitória com suporte a rodadas (Melhor de 1/3/5).
- **Áudio Resiliente**: O sistema de som funciona 100% mesmo se os arquivos de áudio não existirem.

## Requisitos

- Python 3.11+
- Pygame 2.0+

## Como Jogar

1. Certifique-se de que o Pygame está instalado:
   ```bash
   pip install pygame
   ```

2. Execute o jogo a partir do diretório raiz:
   ```bash
   python main.py
   ```

## Controles (Durante a partida)

* `←` e `→` : Ajustar Ângulo
* `↑` e `↓` : Ajustar Potência
* `ESPAÇO` : Disparar Flecha
* `Q` e `E` : Trocar tipo de flecha (Normal, Pesada, Explosiva)

## Opções

No menu de opções, você pode alterar:
- Volumes (Efeitos e Música)
- Partículas, Sangue e Tremor de Tela
- Vento (Ativa uma força aleatória que afeta o eixo X das flechas)
- Formato da partida (Melhor de 1, 3 ou 5)

## Arquitetura e Código

O código foi arquitetado utilizando orientação a objetos e divisão clara de responsabilidades:
- `settings.py`: Constantes globais e estrutura de opções.
- `main.py` e `scenes.py`: Máquina de estados controlando a transição fluida entre telas.
- `player.py`: Desenho procedural do avatar baseando-se em trigonometria e temporizadores para criar a ilusão de respiração e puxada do arco.
- `arrow.py`: Motor de física, cálculo balístico e detecção de colisão via hitboxes independentes para cabeça e corpo.
- `ai.py`: Módulo que simula heurística humana ao tentar calcular parábolas com inclusão intencional de "erro humano".
- `effects.py`: Engine leve de partículas e retroalimentação visual de combate (game feel).
