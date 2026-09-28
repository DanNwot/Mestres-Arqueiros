import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys

from scripts.settings import *
from scripts.audio import AudioManager
from scripts.scenes import SceneManager, MenuScene, OptionsScene, GameScene, VictoryScene, PhaseIntroScene, PhaseCompleteScene

def main():
    # Inicialização do Pygame
    pygame.init()
    pygame.display.set_caption(TITLE)
    
    # Configuração da janela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # Sistemas globais
    settings = GameSettings()
    audio = AudioManager(settings)
    
    # Gerenciador de Cenas
    scene_manager = SceneManager(audio, settings)
    
    # Registra as cenas
    scene_manager.add_scene("menu", MenuScene(scene_manager))
    scene_manager.add_scene("options", OptionsScene(scene_manager))
    scene_manager.add_scene("game", GameScene(scene_manager))
    scene_manager.add_scene("victory", VictoryScene(scene_manager))
    scene_manager.add_scene("phase_intro", PhaseIntroScene(scene_manager))
    scene_manager.add_scene("phase_complete", PhaseCompleteScene(scene_manager))
    
    # Define cena inicial sem transição (entra direto)
    scene_manager.current_scene = scene_manager.scenes["menu"]
    scene_manager.current_scene.enter()
    
    # Game Loop
    running = True
    while running:
        # Delta time em segundos (limitado a um máximo para evitar pulos grandes ao travar a janela)
        dt = min(clock.tick(FPS) / 1000.0, 0.1)
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            scene_manager.handle_event(event)
            
        # Atualização lógica
        scene_manager.update(dt)
        
        # Renderização
        scene_manager.draw(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
