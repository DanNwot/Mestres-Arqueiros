"""
Mestres Arqueiros — Teste de Integridade e Validação
Verifica se todas as cenas, áudios, gráficos, física e IA funcionam sem erros.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1280, 720))

from scripts.settings import *
from scripts.audio import AudioManager
from scripts.scenes import SceneManager, MenuScene, OptionsScene, GameScene, VictoryScene, PhaseIntroScene, PhaseCompleteScene
from scripts.player import Player
from scripts.arrow import Arrow

print("[1/5] Inicializando Sistemas Globais...")
settings = GameSettings()
audio = AudioManager(settings)
sm = SceneManager(audio, settings)

print("[2/5] Registrando Cenas...")
sm.add_scene("menu", MenuScene(sm))
sm.add_scene("options", OptionsScene(sm))
sm.add_scene("game", GameScene(sm))
sm.add_scene("victory", VictoryScene(sm))
sm.add_scene("phase_intro", PhaseIntroScene(sm))
sm.add_scene("phase_complete", PhaseCompleteScene(sm))

print("[3/5] Testando Jogador e Flechas...")
p1 = Player(200, 1, P1_PRIMARY, P1_SECONDARY)
p2 = Player(1000, 2, P2_PRIMARY, P2_SECONDARY)
p1.adjust_angle(1, 0.1)
p1.adjust_power(1, 0.1)
pos, vec = p1.shoot()
arrow = Arrow(pos[0], pos[1], vec[0], vec[1], ARROW_EXPLOSIVE, 1)
arrow.update(0.016, 20)

print("[4/5] Testando Renderização em cada uma das 5 fases...")
game_scene = sm.scenes["game"]
for phase in range(1, 6):
    game_scene.set_args(mode="campaign", phase=phase)
    game_scene.update(0.016)
    game_scene.draw(screen)

print("[5/5] Testando Menu de Pausa e Troca de Cenas...")
game_scene.pause_menu.toggle()
assert game_scene.pause_menu.is_active == True
game_scene.update(0.016)
game_scene.draw(screen)
game_scene.pause_menu.toggle()
assert game_scene.pause_menu.is_active == False

print(">>> TODOS OS TESTES PASSARAM COM SUCESSO! 100% OK! <<<")
