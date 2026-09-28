"""
Mestres Arqueiros — Sistema de Cenas
Controla fluxo de menus, opções, loop principal de gameplay e tela de vitória.
"""

import pygame
import random
import math
from scripts.settings import *
from scripts.ui import Button, Toggle, Slider, FadeTransition, HUD, PauseMenu, draw_glass_panel, draw_gradient_rect
from scripts.player import Player
from scripts.arrow import Arrow
from scripts.effects import ParticleSystem, BloodEffect, DustEffect, ExplosionEffect, DamageNumber, ScreenShake
from scripts.ai import AIController

class Scene:
    def __init__(self, manager):
        self.manager = manager
        
    def enter(self):
        pass
        
    def exit(self):
        pass
        
    def handle_event(self, event):
        pass
        
    def update(self, dt):
        pass
        
    def draw(self, surface):
        pass


class SceneManager:
    def __init__(self, audio_manager, settings):
        self.audio = audio_manager
        self.settings = settings
        self.scenes = {}
        self.current_scene = None
        self.fade = FadeTransition()
        self.next_scene_name = None
        self.transition_args = {}

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def switch_scene(self, name, **kwargs):
        """Inicia transição de fade-out para trocar de cena."""
        if name not in self.scenes:
            return
            
        self.next_scene_name = name
        self.transition_args = kwargs
        self.fade.start("out", self._on_fade_out_complete)

    def _on_fade_out_complete(self):
        """Callback chamado quando a tela fica preta."""
        if self.current_scene:
            self.current_scene.exit()
            
        self.current_scene = self.scenes[self.next_scene_name]
        
        # Passa argumentos para a cena, se ela suportar
        if hasattr(self.current_scene, 'set_args'):
            self.current_scene.set_args(**self.transition_args)
            
        self.current_scene.enter()
        self.fade.start("in") # Começa fade in

    def handle_event(self, event):
        if self.current_scene and not self.fade.is_fading:
            self.current_scene.handle_event(event)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)
        self.fade.update(dt)

    def draw(self, surface):
        if self.current_scene:
            self.current_scene.draw(surface)
        self.fade.draw(surface)


class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.buttons = []
        
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        
        self.buttons.append(Button(cx - 150, cy - 60, 300, 60, "CAMPANHA", lambda: self.manager.switch_scene("phase_intro", phase=1)))
        self.buttons.append(Button(cx - 150, cy + 20, 300, 60, "JOGADOR VS IA", lambda: self.manager.switch_scene("game", mode="pve")))
        self.buttons.append(Button(cx - 150, cy + 100, 300, 60, "JOGADOR VS JOGADOR", lambda: self.manager.switch_scene("game", mode="pvp")))
        self.buttons.append(Button(cx - 150, cy + 180, 300, 60, "OPÇÕES", lambda: self.manager.switch_scene("options")))
        self.buttons.append(Button(cx - 150, cy + 260, 300, 60, "SAIR", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))))
        
        try:
            self.font_title = pygame.font.SysFont("impact", 80)
        except:
            self.font_title = pygame.font.Font(None, 100)

    def enter(self):
        self.manager.audio.play_music("assets/music/menu.ogg")

    def handle_event(self, event):
        # Botões tratam estado no update
        pass

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for btn in self.buttons:
            was_clicked = btn.clicked
            btn.update(mouse_pos, mouse_click)
            if btn.clicked and not was_clicked:
                self.manager.audio.play_sound("click")

    def draw(self, surface):
        surface.fill(UI_BG)
        
        # Fundo dinâmico (estrelas/partículas lentas)
        t = pygame.time.get_ticks() / 1000
        for i in range(50):
            x = (math.sin(t + i) * 100 + i * 30) % SCREEN_WIDTH
            y = (math.cos(t * 0.5 + i) * 50 + i * 20) % SCREEN_HEIGHT
            pygame.draw.circle(surface, (50, 50, 70), (int(x), int(y)), 2)

        # Título
        title_text = "MESTRES ARQUEIROS"
        title_surf = self.font_title.render(title_text, True, UI_ACCENT)
        shadow = self.font_title.render(title_text, True, (0, 0, 0))
        
        tx = SCREEN_WIDTH//2 - title_surf.get_width()//2
        ty = 80
        surface.blit(shadow, (tx + 4, ty + 4))
        surface.blit(title_surf, (tx, ty))

        # Botões
        for btn in self.buttons:
            btn.draw(surface)


class OptionsScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.elements = []
        
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        
        # Obter config atual
        s = self.manager.settings
        
        # Audio
        self.elements.append(Toggle(cx - 250, cy - 150, "Música", s.music_on, self._toggle_music))
        self.elements.append(Slider(cx - 250, cy - 90, 200, "Vol. Música", s.music_volume, self._set_music_vol))
        self.elements.append(Slider(cx - 250, cy - 30, 200, "Vol. Efeitos", s.sfx_volume, lambda v: setattr(s, 'sfx_volume', v)))
        
        # Gráficos
        self.elements.append(Toggle(cx + 100, cy - 150, "Sangue", s.blood_on, lambda v: setattr(s, 'blood_on', v)))
        self.elements.append(Toggle(cx + 100, cy - 90, "Tremor", s.screen_shake_on, lambda v: setattr(s, 'screen_shake_on', v)))
        self.elements.append(Toggle(cx + 100, cy - 30, "Partículas", s.particles_on, lambda v: setattr(s, 'particles_on', v)))
        
        # Gameplay
        self.elements.append(Toggle(cx - 250, cy + 50, "Vento", s.wind_on, lambda v: setattr(s, 'wind_on', v)))
        
        self.rounds_text = ["Melhor de 1", "Melhor de 3", "Melhor de 5"]
        self.round_idx = 0 if s.rounds == 1 else (1 if s.rounds == 3 else 2)
        
        self.btn_rounds = Button(cx + 100, cy + 50, 250, 40, self.rounds_text[self.round_idx], self._cycle_rounds)
        self.elements.append(self.btn_rounds)
        
        # Voltar
        self.btn_back = Button(cx - 100, cy + 180, 200, 50, "VOLTAR", lambda: self.manager.switch_scene("menu"))
        self.elements.append(self.btn_back)
        
        try:
            self.font_title = pygame.font.SysFont("impact", 60)
        except:
            self.font_title = pygame.font.Font(None, 80)

    def _toggle_music(self, state):
        self.manager.audio.toggle_music()
        if self.manager.settings.music_on:
            self.manager.audio.play_music("assets/music/menu.ogg")
            
    def _set_music_vol(self, val):
        self.manager.settings.music_volume = val
        self.manager.audio.update_volumes()

    def _cycle_rounds(self):
        self.round_idx = (self.round_idx + 1) % 3
        vals = [1, 3, 5]
        self.manager.settings.rounds = vals[self.round_idx]
        self.btn_rounds.text = self.rounds_text[self.round_idx]

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for el in self.elements:
            if hasattr(el, 'clicked'):
                was_clicked = el.clicked
                el.update(mouse_pos, mouse_click)
                if el.clicked and not was_clicked:
                    self.manager.audio.play_sound("click")
            else:
                # É slider
                el.update(mouse_pos, mouse_click)

    def draw(self, surface):
        surface.fill(UI_BG)
        
        # Título
        title_surf = self.font_title.render("OPÇÕES", True, WHITE)
        surface.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 50))
        
        for el in self.elements:
            el.draw(surface)


# =============================================================================
# CENA DE INTRODUÇÃO DE FASE (Campanha)
# =============================================================================
class PhaseIntroScene(Scene):
    """Tela de introdução exibida antes de cada fase da campanha."""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.phase = 1
        self.timer = 0
        self.ready_to_continue = False
        
        try:
            self.font_title = pygame.font.SysFont("impact", 72)
            self.font_sub = pygame.font.SysFont("impact", 32)
            self.font_desc = pygame.font.SysFont("segoeui", 26)
            self.font_hint = pygame.font.SysFont("segoeui", 20)
        except:
            self.font_title = pygame.font.Font(None, 90)
            self.font_sub = pygame.font.Font(None, 40)
            self.font_desc = pygame.font.Font(None, 30)
            self.font_hint = pygame.font.Font(None, 24)
    
    def set_args(self, phase=1, **kwargs):
        self.phase = phase
        self.timer = 0
        self.ready_to_continue = False
    
    def enter(self):
        self.timer = 0
        self.ready_to_continue = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.ready_to_continue:
            self.manager.switch_scene("game", mode="campaign", phase=self.phase)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.ready_to_continue:
            self.manager.switch_scene("game", mode="campaign", phase=self.phase)
    
    def update(self, dt):
        self.timer += dt
        if self.timer >= 1.0:
            self.ready_to_continue = True
    
    def draw(self, surface):
        config = PHASE_CONFIG.get(self.phase, PHASE_CONFIG[1])
        scenario = config["scenario"]
        
        # Fundo baseado no cenário da fase
        bg_colors = {
            SCENARIO_FOREST: (20, 50, 30),
            SCENARIO_VALLEY: (60, 40, 20),
            SCENARIO_FORTRESS: (25, 25, 40),
            SCENARIO_SWAMP: (15, 30, 25),
            SCENARIO_VOLCANO: (50, 15, 10),
        }
        surface.fill(bg_colors.get(scenario, UI_BG))
        
        # Partículas decorativas
        t = pygame.time.get_ticks() / 1000
        for i in range(30):
            x = (math.sin(t * 0.7 + i * 2) * 200 + i * 50) % SCREEN_WIDTH
            y = (math.cos(t * 0.3 + i * 1.5) * 100 + i * 30) % SCREEN_HEIGHT
            alpha = int(80 + 40 * math.sin(t + i))
            color = self._get_phase_particle_color(scenario, alpha)
            pygame.draw.circle(surface, color, (int(x), int(y)), random.choice([2, 3]))
        
        cx = SCREEN_WIDTH // 2
        
        # Indicador de progresso (bolinhas)
        indicator_y = 150
        for i in range(1, TOTAL_PHASES + 1):
            ix = cx + (i - 3) * 60
            if i < self.phase:
                color = (50, 200, 100)   # Completa
                radius = 12
            elif i == self.phase:
                color = UI_ACCENT        # Atual
                radius = 16
            else:
                color = (60, 60, 80)     # Futura
                radius = 10
            pygame.draw.circle(surface, color, (ix, indicator_y), radius)
            # Número dentro
            num_surf = self.font_hint.render(str(i), True, BLACK if i <= self.phase else GRAY)
            surface.blit(num_surf, (ix - num_surf.get_width()//2, indicator_y - num_surf.get_height()//2))
            
            # Linha conectora
            if i < TOTAL_PHASES:
                line_color = (50, 200, 100) if i < self.phase else (60, 60, 80)
                pygame.draw.line(surface, line_color, (ix + radius + 5, indicator_y), (ix + 60 - radius - 5, indicator_y), 3)
        
        # Título da fase com animação de entrada
        anim_progress = min(1.0, self.timer / 0.8)
        slide_offset = int((1.0 - anim_progress) * 100)
        
        title_text = config["title"]
        title_surf = self.font_title.render(title_text, True, UI_ACCENT)
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        
        tx = cx - title_surf.get_width()//2
        ty = 230 + slide_offset
        
        surface.blit(shadow_surf, (tx + 3, ty + 3))
        surface.blit(title_surf, (tx, ty))
        
        # Descrição
        if self.timer > 0.3:
            desc_alpha = min(255, int((self.timer - 0.3) * 500))
            desc_surf = self.font_desc.render(config["desc"], True, UI_TEXT)
            desc_surf.set_alpha(desc_alpha)
            surface.blit(desc_surf, (cx - desc_surf.get_width()//2, 330))
        
        # Info da fase
        if self.timer > 0.6:
            info_alpha = min(255, int((self.timer - 0.6) * 500))
            
            # Dados da fase
            wind_min, wind_max = config["wind_range"]
            if wind_max == 0:
                wind_str = "Sem vento"
            elif wind_max <= 60:
                wind_str = "Vento leve"
            elif wind_max <= 100:
                wind_str = "Vento moderado"
            elif wind_max <= 130:
                wind_str = "Vento forte"
            else:
                wind_str = "Vento extremo"
            
            health_str = f"Vida do inimigo: {int(config['enemy_health_mult'] * 100)}%"
            diff_str = f"Dificuldade da IA: {'★' * int(config['ai_difficulty'] * 5 + 0.5)}{'☆' * (5 - int(config['ai_difficulty'] * 5 + 0.5))}"
            
            infos = [wind_str, health_str, diff_str]
            for idx, info in enumerate(infos):
                info_surf = self.font_sub.render(info, True, WHITE)
                info_surf.set_alpha(info_alpha)
                surface.blit(info_surf, (cx - info_surf.get_width()//2, 390 + idx * 45))
        
        # Dica para continuar
        if self.ready_to_continue:
            blink = math.sin(t * 4) > 0
            if blink:
                hint_surf = self.font_hint.render("Pressione qualquer tecla para começar...", True, UI_TEXT)
                surface.blit(hint_surf, (cx - hint_surf.get_width()//2, 580))
    
    def _get_phase_particle_color(self, scenario, alpha):
        if scenario == SCENARIO_FOREST:
            return (30, 120, 50)
        elif scenario == SCENARIO_VALLEY:
            return (180, 120, 60)
        elif scenario == SCENARIO_FORTRESS:
            return (80, 80, 120)
        elif scenario == SCENARIO_SWAMP:
            return (40, 100, 70)
        elif scenario == SCENARIO_VOLCANO:
            return (200, 60, 20)
        return (100, 100, 100)


# =============================================================================
# CENA DE FASE COMPLETADA
# =============================================================================
class PhaseCompleteScene(Scene):
    """Tela exibida após completar uma fase da campanha."""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.phase_completed = 1
        self.timer = 0
        self.ready_to_continue = False
        
        try:
            self.font_title = pygame.font.SysFont("impact", 72)
            self.font_sub = pygame.font.SysFont("impact", 36)
            self.font_hint = pygame.font.SysFont("segoeui", 22)
        except:
            self.font_title = pygame.font.Font(None, 90)
            self.font_sub = pygame.font.Font(None, 44)
            self.font_hint = pygame.font.Font(None, 26)
    
    def set_args(self, phase_completed=1, **kwargs):
        self.phase_completed = phase_completed
        self.timer = 0
        self.ready_to_continue = False
    
    def enter(self):
        self.timer = 0
        self.ready_to_continue = False
        self.manager.audio.play_sound("victory")
    
    def handle_event(self, event):
        if (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and self.ready_to_continue:
            next_phase = self.phase_completed + 1
            if next_phase > TOTAL_PHASES:
                # Campanha completa!
                self.manager.switch_scene("victory", winner="CAMPEÃO", score_p1=self.phase_completed, score_p2=0, is_campaign=True)
            else:
                self.manager.switch_scene("phase_intro", phase=next_phase)
    
    def update(self, dt):
        self.timer += dt
        if self.timer >= 1.5:
            self.ready_to_continue = True
    
    def draw(self, surface):
        surface.fill(UI_BG)
        
        t = pygame.time.get_ticks() / 1000
        cx = SCREEN_WIDTH // 2
        
        # Partículas de celebração
        for i in range(40):
            x = (math.sin(t * 1.2 + i * 1.5) * 300 + i * 35) % SCREEN_WIDTH
            y = (math.cos(t * 0.8 + i * 2) * 200 + i * 20) % SCREEN_HEIGHT
            color = random.choice([(255, 210, 60), (50, 200, 100), (100, 170, 255)])
            pygame.draw.circle(surface, color, (int(x), int(y)), random.choice([2, 3, 4]))
        
        # Título
        anim = min(1.0, self.timer / 0.8)
        scale_factor = 0.5 + anim * 0.5
        
        title_text = "FASE COMPLETADA!"
        title_surf = self.font_title.render(title_text, True, (50, 200, 100))
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        
        tx = cx - title_surf.get_width()//2
        ty = 180
        
        surface.blit(shadow_surf, (tx + 3, ty + 3))
        surface.blit(title_surf, (tx, ty))
        
        # Sub-título
        if self.timer > 0.4:
            config = PHASE_CONFIG.get(self.phase_completed, PHASE_CONFIG[1])
            sub_text = config["title"]
            sub_surf = self.font_sub.render(sub_text, True, UI_ACCENT)
            surface.blit(sub_surf, (cx - sub_surf.get_width()//2, 280))
        
        # Progresso visual
        if self.timer > 0.8:
            indicator_y = 380
            for i in range(1, TOTAL_PHASES + 1):
                ix = cx + (i - 3) * 60
                if i <= self.phase_completed:
                    color = (50, 200, 100)
                    radius = 14
                else:
                    color = (60, 60, 80)
                    radius = 10
                pygame.draw.circle(surface, color, (ix, indicator_y), radius)
                num_surf = self.font_hint.render(str(i), True, BLACK if i <= self.phase_completed else GRAY)
                surface.blit(num_surf, (ix - num_surf.get_width()//2, indicator_y - num_surf.get_height()//2))
                
                if i < TOTAL_PHASES:
                    line_color = (50, 200, 100) if i < self.phase_completed else (60, 60, 80)
                    pygame.draw.line(surface, line_color, (ix + radius + 5, indicator_y), (ix + 60 - radius - 5, indicator_y), 3)
        
        # Próxima fase info
        if self.timer > 1.2:
            next_phase = self.phase_completed + 1
            if next_phase <= TOTAL_PHASES:
                next_config = PHASE_CONFIG[next_phase]
                next_text = f"Próximo: {next_config['title']}"
                next_surf = self.font_sub.render(next_text, True, WHITE)
                surface.blit(next_surf, (cx - next_surf.get_width()//2, 440))
            else:
                next_text = "Você completou todas as fases!"
                next_surf = self.font_sub.render(next_text, True, UI_ACCENT)
                surface.blit(next_surf, (cx - next_surf.get_width()//2, 440))
        
        # Dica para continuar
        if self.ready_to_continue:
            blink = math.sin(t * 4) > 0
            if blink:
                hint_surf = self.font_hint.render("Pressione qualquer tecla para continuar...", True, UI_TEXT)
                surface.blit(hint_surf, (cx - hint_surf.get_width()//2, 550))


class GameScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.mode = "pvp" # pve, pvp, campaign
        self.scenario_id = 0
        self.current_phase = 0  # 0 = sem fase (PvP/PvE), 1-5 = campanha
        
        self.p1 = None
        self.p2 = None
        self.ai = None
        
        self.active_arrow = None
        self.current_turn = 1 # 1 ou 2
        self.state = "aiming" # aiming, shooting, flying, post_shot, game_over
        
        self.particles = ParticleSystem(manager.settings)
        self.shake = ScreenShake(manager.settings)
        self.hud = HUD()
        
        self.wind = 0.0
        self.timer = 0
        self.damage_numbers = []
        
        # Controle de rodadas
        self.p1_wins = 0
        self.p2_wins = 0
        self.current_round = 1
        
        self.arrow_type_p1 = ARROW_NORMAL
        self.arrow_type_p2 = ARROW_NORMAL
        
        self.camera_x = 0
        
        # Menu de Pausa integrado
        self.pause_menu = PauseMenu()
        self.pause_menu.set_actions(
            resume_action=self.pause_menu.close,
            restart_action=self._restart_match,
            menu_action=lambda: self.manager.switch_scene("menu")
        )

    def _restart_match(self):
        self.pause_menu.close()
        self.p1_wins = 0
        self.p2_wins = 0
        self.current_round = 1
        self._start_round()

    def set_args(self, mode="pvp", phase=0, **kwargs):
        self.mode = mode
        self.current_phase = phase if mode == "campaign" else 0
        self.p1_wins = 0
        self.p2_wins = 0
        self.current_round = 1
        self.camera_x = 0
        if self.pause_menu.is_active:
            self.pause_menu.close()
        self._start_round()

    def _start_round(self):
        # Define cenário
        if self.mode == "campaign" and self.current_phase > 0:
            config = PHASE_CONFIG.get(self.current_phase, PHASE_CONFIG[1])
            self.scenario_id = config["scenario"]
        else:
            self.scenario_id = random.choice([SCENARIO_FOREST, SCENARIO_VALLEY, SCENARIO_FORTRESS, SCENARIO_SWAMP, SCENARIO_VOLCANO])
        
        # Reset de jogadores
        self.p1 = Player(P1_START_X, 1, P1_PRIMARY, P1_SECONDARY)
        self.p2 = Player(P2_START_X, 2, P2_PRIMARY, P2_SECONDARY)
        
        # Vida baseada na fase (campanha) ou configurações normais
        p1_health = self.manager.settings.initial_health
        p2_health = self.manager.settings.initial_health
        
        if self.mode == "campaign" and self.current_phase > 0:
            config = PHASE_CONFIG.get(self.current_phase, PHASE_CONFIG[1])
            # Inimigo (P2) tem vida aumentada conforme a fase
            p2_health = int(self.manager.settings.initial_health * config["enemy_health_mult"])
        
        self.p1.set_max_health(p1_health)
        self.p2.set_max_health(p2_health)
        
        # Instancia IA se necessário
        if self.mode in ("pve", "campaign"):
            ai_difficulty = 0.5  # Padrão para PvE
            if self.mode == "campaign" and self.current_phase > 0:
                ai_difficulty = PHASE_CONFIG.get(self.current_phase, PHASE_CONFIG[1])["ai_difficulty"]
            self.ai = AIController(self.p2, self.p1, difficulty=ai_difficulty)
        else:
            self.ai = None
        
        self.state = "round_intro"
        self.timer = 2.5
        
        # Começa a câmera no jogador atual
        current_p = self.p1 if self.current_turn == 1 else self.p2
        self.camera_x = current_p.x - SCREEN_WIDTH//2 + (current_p.direction * 150)
        
        self._randomize_wind()

    def _randomize_wind(self):
        if self.mode == "campaign" and self.current_phase > 0:
            config = PHASE_CONFIG.get(self.current_phase, PHASE_CONFIG[1])
            wind_min, wind_max = config["wind_range"]
            if wind_max == 0:
                self.wind = 0
            else:
                self.wind = random.uniform(wind_min, wind_max)
                if abs(self.wind) < 15:
                    self.wind = 0
        elif self.manager.settings.wind_on:
            # -150 a 150
            self.wind = random.uniform(-150.0, 150.0)
            if abs(self.wind) < 20: 
                self.wind = 0 # Vento muito fraco
        else:
            self.wind = 0

    def enter(self):
        self.manager.audio.play_music("assets/music/game.ogg")

    def handle_event(self, event):
        # Menu de Pausa
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_menu.toggle()
            return
            
        if self.pause_menu.is_active:
            self.pause_menu.handle_event(event)
            return

        if self.state != "aiming":
            return
            
        # Ignora inputs se for o turno da IA
        if self.current_turn == 2 and self.mode in ("pve", "campaign"):
            return
            
        current_player = self.p1 if self.current_turn == 1 else self.p2
        
        if event.type == pygame.KEYDOWN:
            # Disparo
            is_shoot = False
            if self.current_turn == 1:
                is_shoot = (event.key in (pygame.K_SPACE, pygame.K_LSHIFT) or 
                            (self.mode in ("pve", "campaign") and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)))
            else:
                is_shoot = (event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER))
                
            if is_shoot:
                self._shoot(current_player)
            # Troca de flecha
            elif event.key in (pygame.K_q, pygame.K_1):
                self._cycle_arrow(-1)
            elif event.key in (pygame.K_e, pygame.K_2):
                self._cycle_arrow(1)

    def _cycle_arrow(self, direction):
        if self.current_turn == 1:
            self.arrow_type_p1 = (self.arrow_type_p1 + direction) % len(ARROW_TYPES)
        else:
            self.arrow_type_p2 = (self.arrow_type_p2 + direction) % len(ARROW_TYPES)

    def _shoot(self, player):
        pos, vec = player.shoot()
        if pos and vec:
            arrow_type = self.arrow_type_p1 if self.current_turn == 1 else self.arrow_type_p2
            if self.current_turn == 2 and self.mode in ("pve", "campaign"):
                arrow_type = self.ai.chosen_arrow_type
                
            self.active_arrow = Arrow(pos[0], pos[1], vec[0], vec[1], arrow_type, player.id)
            self.state = "flying"
            self.manager.audio.play_sound("shoot")

    def update(self, dt):
        if self.pause_menu.is_active:
            self.pause_menu.update(dt)
            return
            
        self.shake.update(dt)
        self.p1.update(dt)
        self.p2.update(dt)
        
        # Barreira Invisível (Limite Máximo de Distância)
        distance = abs(self.p1.x - self.p2.x)
        if distance > 1150:
            center = (self.p1.x + self.p2.x) / 2
            if self.p1.x < self.p2.x:
                self.p1.x = center - 1150 / 2
                self.p2.x = center + 1150 / 2
            else:
                self.p1.x = center + 1150 / 2
                self.p2.x = center - 1150 / 2
            self.p1.vx = 0
            self.p2.vx = 0

        self.particles.update(dt, GRAVITY)
        
        # Update damage numbers
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update(dt)]
        
        # Efeito de vento
        if self.wind != 0 and random.random() < 0.12:
            DustEffect.spawn(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), self.particles, 1)
            for p in self.particles.particles[-1:]:
                p.vx = self.wind * 0.8
        
        if self.state == "aiming":
            # Input contínuo
            keys = pygame.key.get_pressed()
            current_player = self.p1 if self.current_turn == 1 else self.p2
            
            # Se for IA, controla por ela
            if self.current_turn == 2 and self.mode in ("pve", "campaign"):
                if self.ai and self.ai.update(dt, self.wind):
                    self._shoot(current_player)
            else:
                # Controles manuais intuitivos
                if self.current_turn == 1:
                    # Potência (W ou S, ou Setas em PvE/Campanha)
                    if keys[pygame.K_w] or (self.mode in ("pve", "campaign") and keys[pygame.K_UP]):
                        current_player.adjust_power(1, dt)
                    if keys[pygame.K_s] or (self.mode in ("pve", "campaign") and keys[pygame.K_DOWN]):
                        current_player.adjust_power(-1, dt)
                    # Ângulo (A ou D, ou Setas em PvE/Campanha)
                    if keys[pygame.K_a] or (self.mode in ("pve", "campaign") and keys[pygame.K_LEFT]):
                        current_player.adjust_angle(1, dt)
                    if keys[pygame.K_d] or (self.mode in ("pve", "campaign") and keys[pygame.K_RIGHT]):
                        current_player.adjust_angle(-1, dt)
                else:
                    if keys[pygame.K_UP]: current_player.adjust_power(1, dt)
                    if keys[pygame.K_DOWN]: current_player.adjust_power(-1, dt)
                    if keys[pygame.K_LEFT]: current_player.adjust_angle(-1, dt)
                    if keys[pygame.K_RIGHT]: current_player.adjust_angle(1, dt)
                    
        elif self.state == "flying":
            if self.active_arrow:
                self.active_arrow.update(dt, self.wind)
                self._check_collisions()
                
                if self.active_arrow.is_destroyed:
                    self.active_arrow = None
                    self.state = "post_shot"
                    self.timer = 1.0 # Espera 1s antes de passar o turno
                    
        elif self.state == "post_shot":
            self.timer -= dt
            if self.timer <= 0:
                self._check_round_end()
                
        # Câmera Dinâmica
        target_cam_x = self.camera_x
        
        if self.state == "round_intro":
            self.timer -= dt
            other_p = self.p2 if self.current_turn == 1 else self.p1
            current_p = self.p1 if self.current_turn == 1 else self.p2
            
            # Vai para o adversário nos primeiros 1.5s, depois volta
            if self.timer > 1.5:
                target_cam_x = other_p.x - SCREEN_WIDTH//2 + (other_p.direction * 150)
            else:
                target_cam_x = current_p.x - SCREEN_WIDTH//2 + (current_p.direction * 150)
                
            if self.timer <= 0:
                self.state = "aiming"
                if self.current_turn == 2 and self.mode in ("pve", "campaign"):
                    if self.ai:
                        self.ai.start_turn()
                    
        elif self.state == "aiming":
            current_p = self.p1 if self.current_turn == 1 else self.p2
            target_cam_x = current_p.x - SCREEN_WIDTH//2 + (current_p.direction * 150)
        elif self.state == "flying" and self.active_arrow:
            target_cam_x = self.active_arrow.x - SCREEN_WIDTH//2
        elif self.state in ["post_shot", "game_over"]:
            target_p = self.p2 if self.current_turn == 1 else self.p1
            target_cam_x = target_p.x - SCREEN_WIDTH//2
            
        self.camera_x += (target_cam_x - self.camera_x) * 5 * dt

    def _check_collisions(self):
        arrow = self.active_arrow
        if not arrow or not arrow.is_active:
            return
            
        rect = arrow.get_rect()
        target = self.p2 if self.current_turn == 1 else self.p1
        hitboxes = target.get_hitbox()
        
        hit_type = None
        
        if rect.colliderect(hitboxes["head"]):
            hit_type = "head"
        elif rect.colliderect(hitboxes["body"]):
            hit_type = "body"
            
        if hit_type:
            # Acertou!
            damage = arrow.get_damage(is_headshot=(hit_type=="head"))
            
            # Calcula o knockback
            knock_base = 350 if hit_type == "head" else 200
            if arrow.type_id == ARROW_HEAVY: knock_base *= 1.5
            
            mag = math.hypot(arrow.vx, arrow.vy)
            if mag > 0:
                dir_x = arrow.vx / mag
                dir_y = min(-0.3, arrow.vy / mag - 0.5)
            else:
                dir_x = 1 if self.current_turn == 1 else -1
                dir_y = -0.5
                
            knock_x = dir_x * knock_base
            knock_y = dir_y * knock_base
            
            # Limite elástico
            other_p = self.p1 if target == self.p2 else self.p2
            if abs(target.x + knock_x * 0.5 - other_p.x) > 1100:
                knock_x = -knock_x * 0.8
                
            target.take_damage(damage, knockback_x=knock_x, knockback_y=knock_y)
            
            # Efeitos
            self.manager.audio.play_sound("headshot" if hit_type == "head" else "hit")
            self.shake.trigger(16 if hit_type == "head" else 8, 0.35)
            BloodEffect.spawn(arrow.x, arrow.y, self.particles, amount=26 if hit_type == "head" else 15)
            self.damage_numbers.append(DamageNumber(target.x, target.y - 100, damage, is_critical=(hit_type=="head")))
            
            # Explosão extra
            if arrow.type_id == ARROW_EXPLOSIVE:
                ExplosionEffect.spawn(arrow.x, arrow.y, self.particles)
                self.manager.audio.play_sound("explosion")
                self.shake.trigger(22, 0.4)
                
            arrow.is_active = False
            arrow.is_destroyed = True
            
        # Errou e bateu no chão
        elif arrow.y >= GROUND_Y:
            DustEffect.spawn(arrow.x, arrow.y, self.particles)
            self.manager.audio.play_sound("dirt")
            
            if arrow.type_id == ARROW_EXPLOSIVE:
                # Dano em área
                ExplosionEffect.spawn(arrow.x, arrow.y, self.particles)
                self.manager.audio.play_sound("explosion")
                self.shake.trigger(16, 0.35)
                
                # Checa distância pro target
                dist = abs(arrow.x - target.x)
                splash_radius = ARROW_TYPES[ARROW_EXPLOSIVE]["splash_radius"]
                if dist < splash_radius:
                    dmg = arrow.get_splash_damage()
                    
                    dir_x = 1 if target.x > arrow.x else -1
                    knock_x = dir_x * 250
                    knock_y = -350
                    
                    other_p = self.p1 if target == self.p2 else self.p2
                    if abs(target.x + knock_x * 0.5 - other_p.x) > 1100:
                        knock_x = -knock_x * 0.8
                        
                    target.take_damage(dmg, knockback_x=knock_x, knockback_y=knock_y)
                    BloodEffect.spawn(target.x, target.y, self.particles, 5)
                    self.damage_numbers.append(DamageNumber(target.x, target.y - 80, dmg, False))
                    
            arrow.is_active = False
            arrow.is_destroyed = True

    def _check_round_end(self):
        self.state = "game_over" # Previne chamadas múltiplas durante a transição
        if self.p1.is_dead or self.p2.is_dead:
            if self.p2.is_dead:
                self.p1_wins += 1
            else:
                self.p2_wins += 1
            
            # Modo Campanha
            if self.mode == "campaign":
                if self.p2.is_dead:
                    # Jogador venceu esta fase — vai para tela de fase completada
                    self.manager.switch_scene("phase_complete", phase_completed=self.current_phase)
                else:
                    # Jogador perdeu — Game Over na campanha
                    self.manager.switch_scene("victory", winner="IA", score_p1=0, score_p2=1, is_campaign=True, failed_phase=self.current_phase)
                return
                
            # Verifica se acabou a partida (PvP/PvE)
            req_wins = (self.manager.settings.rounds // 2) + 1
            if self.p1_wins >= req_wins or self.p2_wins >= req_wins:
                # Fim de jogo
                winner = "P1" if self.p1_wins >= req_wins else ("IA" if self.mode == "pve" and self.p2_wins >= req_wins else "P2")
                self.manager.switch_scene("victory", winner=winner, score_p1=self.p1_wins, score_p2=self.p2_wins)
            else:
                # Próximo round
                self.current_round += 1
                self._start_round()
        else:
            # Passa turno
            self.current_turn = 2 if self.current_turn == 1 else 1
            self._randomize_wind()
            self.state = "aiming"
            if self.current_turn == 2 and self.mode in ("pve", "campaign"):
                if self.ai:
                    self.ai.start_turn()

    def draw(self, surface):
        offset_x, offset_y = self.shake.get_offset()
        world = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        t = pygame.time.get_ticks() / 1000.0
        
        # 1. Céu com gradiente rico e corpos celestes
        if self.scenario_id == SCENARIO_FOREST:
            # Amanhecer florestal dourado
            draw_gradient_rect(world, pygame.Rect(0, 0, SCREEN_WIDTH, GROUND_Y), (30, 80, 150), (235, 205, 150))
            # Sol matinal dourado com auréola
            sun_x, sun_y = SCREEN_WIDTH - 220, 130
            for r, a in [(80, 25), (60, 45), (45, 90), (32, 230)]:
                s_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s_surf, (255, 245, 200, a), (r, r), r)
                world.blit(s_surf, (sun_x - r, sun_y - r))
                
        elif self.scenario_id == SCENARIO_VALLEY:
            # Pôr do sol épico em três tons
            draw_gradient_rect(world, pygame.Rect(0, 0, SCREEN_WIDTH, GROUND_Y), (95, 30, 70), (255, 160, 50))
            # Sol poente avermelhado gigante
            sun_x, sun_y = SCREEN_WIDTH - 260, 190
            for r, a in [(110, 20), (80, 50), (55, 120), (40, 240)]:
                s_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s_surf, (255, 200, 110, a), (r, r), r)
                world.blit(s_surf, (sun_x - r, sun_y - r))
                
        elif self.scenario_id == SCENARIO_FORTRESS:
            # Céu noturno estrelado
            draw_gradient_rect(world, pygame.Rect(0, 0, SCREEN_WIDTH, GROUND_Y), (12, 16, 32), (38, 48, 72))
            # Estrelas brilhantes
            for i in range(45):
                sx = (i * 97 + 13) % SCREEN_WIDTH
                sy = (i * 47 + 7) % (GROUND_Y - 140)
                twinkle = int(140 + 115 * math.sin(t * 3.0 + i))
                world.set_at((sx, sy), (twinkle, twinkle, min(255, twinkle + 20)))
            # Lua prateada com brilho
            moon_x, moon_y = SCREEN_WIDTH - 240, 110
            for r, a in [(55, 15), (42, 35), (28, 220)]:
                m_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(m_surf, (230, 235, 255, a), (r, r), r)
                world.blit(m_surf, (moon_x - r, moon_y - r))
            # Crateras da lua
            pygame.draw.circle(world, (200, 205, 225), (moon_x - 6, moon_y - 4), 6)
            pygame.draw.circle(world, (190, 195, 215), (moon_x + 8, moon_y + 6), 5)
            pygame.draw.circle(world, (200, 205, 225), (moon_x + 5, moon_y - 9), 4)
            
        elif self.scenario_id == SCENARIO_SWAMP:
            # Crepúsculo pantanoso misterioso
            draw_gradient_rect(world, pygame.Rect(0, 0, SCREEN_WIDTH, GROUND_Y), (16, 28, 24), (45, 85, 65))
            # Lua pálida filtrada por nuvens
            moon_x, moon_y = SCREEN_WIDTH - 250, 120
            pygame.draw.circle(world, (180, 210, 190), (moon_x, moon_y), 32)
            pygame.draw.circle(world, (24, 38, 32), (moon_x + 10, moon_y - 6), 26) # Quarto crescente
            
        elif self.scenario_id == SCENARIO_VOLCANO:
            # Céu escuro de cinzas com labaredas no horizonte
            draw_gradient_rect(world, pygame.Rect(0, 0, SCREEN_WIDTH, GROUND_Y), (26, 10, 10), (160, 40, 15))
            # Brilho de magma no horizonte
            for i in range(5):
                glow_r = 240 - i * 35
                glow_a = 20 + i * 15
                g_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(g_surf, (255, 80 + i * 20, 10, glow_a), (glow_r, glow_r), glow_r)
                world.blit(g_surf, (SCREEN_WIDTH // 2 - glow_r, GROUND_Y - glow_r // 2))

        # 2. Cenário de fundo procedural enriquecido
        self._draw_background(world)
        
        # 3. Chão com texturas, detalhes e camadas realistas
        self._draw_ground(world)

        # 4. Entidades do jogo
        self.p1.draw(world, offset_x=self.camera_x)
        self.p2.draw(world, offset_x=self.camera_x)
        
        if self.active_arrow:
            self.active_arrow.draw(world, offset_x=self.camera_x)
            
        self.particles.draw(world, offset_x=self.camera_x)
        
        for dn in self.damage_numbers:
            dn.draw(world, offset_x=self.camera_x)

        # Efeitos especiais sobrepostos ao mundo
        if self.scenario_id == SCENARIO_SWAMP:
            self._draw_fog(world)
        elif self.scenario_id == SCENARIO_VOLCANO:
            self._draw_embers(world)

        # Copia o mundo com offset de tremor para a tela final
        surface.blit(world, (int(offset_x), int(offset_y)))

        # 5. Interface HUD (nítida e fixa)
        current_player = self.p1 if self.current_turn == 1 else self.p2
        arrow_name = ARROW_TYPES[self.arrow_type_p1 if self.current_turn == 1 else self.arrow_type_p2]["name"]
        if self.current_turn == 2 and self.mode in ("pve", "campaign") and self.ai and self.ai.state != "waiting":
            arrow_name = ARROW_TYPES[self.ai.chosen_arrow_type]["name"]
            
        if self.mode == "campaign" and self.current_phase > 0:
            round_text = f"Fase {self.current_phase}/{TOTAL_PHASES} — {SCENARIO_NAMES.get(self.scenario_id, '')}"
        else:
            round_text = f"Rodada {self.current_round} — {SCENARIO_NAMES.get(self.scenario_id, '')}"
            
        hud_state = {
            'p1_health': self.p1.health,
            'p1_max': self.p1.max_health,
            'p2_health': self.p2.health,
            'p2_max': self.p2.max_health,
            'current_turn': self.current_turn,
            'is_ai': (self.mode in ("pve", "campaign")),
            'state': self.state,
            'angle': current_player.angle,
            'power': current_player.power,
            'arrow_name': arrow_name,
            'round_text': round_text,
            'wind': self.wind if (self.manager.settings.wind_on or (self.mode == "campaign" and self.wind != 0)) else None,
            'p1_wins': self.p1_wins,
            'p2_wins': self.p2_wins,
            'is_campaign': (self.mode == "campaign"),
            'current_phase': self.current_phase,
        }
        
        self.hud.draw(surface, hud_state)
        
        # 6. Menu de Pausa (se ativo)
        if self.pause_menu.is_active:
            self.pause_menu.draw(surface)

    def _draw_ground(self, surface):
        """Renderiza o chão com camadas, detalhes em relevo e vegetação viva."""
        ground_h = SCREEN_HEIGHT - GROUND_Y
        ground_rect = pygame.Rect(0, GROUND_Y, SCREEN_WIDTH, ground_h)
        t = pygame.time.get_ticks() / 1000.0
        
        if self.scenario_id == SCENARIO_FOREST:
            # Solo fértil escuro + gramado verde vivo
            draw_gradient_rect(surface, ground_rect, (45, 140, 45), (30, 80, 30))
            # Linha de grama superior
            pygame.draw.line(surface, (70, 185, 70), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
            # Tufos de grama e flores espalhados
            for i in range(0, SCREEN_WIDTH + 20, 24):
                sway = math.sin(t * 2.0 + i) * 2.0
                pygame.draw.line(surface, (90, 205, 70), (i, GROUND_Y), (i + 4 + sway, GROUND_Y - 7), 2)
                pygame.draw.line(surface, (80, 195, 60), (i + 4, GROUND_Y), (i + 8 + sway, GROUND_Y - 9), 2)
                # Flores silvestres ocasionais
                if i % 96 == 0:
                    pygame.draw.circle(surface, (255, 235, 60), (int(i + 4), GROUND_Y - 10), 3)
                    pygame.draw.circle(surface, (255, 255, 255), (int(i + 2), GROUND_Y - 11), 2)
                elif i % 144 == 0:
                    pygame.draw.circle(surface, (240, 60, 60), (int(i + 4), GROUND_Y - 10), 3)
                    
        elif self.scenario_id == SCENARIO_VALLEY:
            # Solo arenoso de canyon
            draw_gradient_rect(surface, ground_rect, (215, 175, 120), (160, 115, 70))
            pygame.draw.line(surface, (235, 195, 140), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
            # Seixos e fendas de areia
            for i in range(0, SCREEN_WIDTH, 48):
                pygame.draw.ellipse(surface, (140, 100, 60), (i + (i % 7) * 4, GROUND_Y + 12 + (i % 3) * 16, 16, 7))
                if i % 72 == 0:
                    # Tufo de capim seco
                    pygame.draw.line(surface, (200, 175, 90), (i, GROUND_Y), (i - 3, GROUND_Y - 7), 2)
                    pygame.draw.line(surface, (190, 165, 80), (i, GROUND_Y), (i + 4, GROUND_Y - 8), 2)
                    
        elif self.scenario_id == SCENARIO_FORTRESS:
            # Pavimento de lajotas de pedra da fortaleza
            draw_gradient_rect(surface, ground_rect, (85, 88, 98), (50, 52, 60))
            pygame.draw.line(surface, (130, 135, 150), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
            # Grade de lajotas de pedra
            for row in range(5):
                ry = GROUND_Y + row * 34
                pygame.draw.line(surface, (40, 42, 50), (0, ry), (SCREEN_WIDTH, ry), 2)
                shift = (row % 2) * 45
                for col in range(shift - 45, SCREEN_WIDTH + 90, 90):
                    pygame.draw.line(surface, (40, 42, 50), (col, ry), (col, ry + 34), 2)
                    
        elif self.scenario_id == SCENARIO_SWAMP:
            # Lama escura e poças de lodo verde
            draw_gradient_rect(surface, ground_rect, (32, 50, 36), (18, 28, 20))
            pygame.draw.line(surface, (45, 75, 50), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
            # Poças de lodo bioluminescente
            for i in range(7):
                px = (i * 200 + 40) % SCREEN_WIDTH
                py = GROUND_Y + 16 + (i % 4) * 26
                glow_a = int(60 + 30 * math.sin(t * 2.0 + i))
                pygame.draw.ellipse(surface, (50, 95, 60), (px, py, 95, 24))
                pygame.draw.ellipse(surface, (30, 65, 40), (px + 10, py + 4, 75, 16))
                # Vitória-régia
                pygame.draw.ellipse(surface, (50, 130, 60), (px + 25, py + 6, 20, 10))
                
        elif self.scenario_id == SCENARIO_VOLCANO:
            # Rocha basáltica escura com fissuras de lava incandescente
            draw_gradient_rect(surface, ground_rect, (45, 25, 22), (20, 10, 10))
            pygame.draw.line(surface, (95, 45, 25), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
            # Fissuras de magma pulsantes
            for i in range(8):
                fx = (i * 170 + 30) % SCREEN_WIDTH
                fy = GROUND_Y + 15 + (i % 4) * 28
                pulse = int(190 + 65 * math.sin(t * 3.5 + i * 1.5))
                # Brilho exterior alaranjado
                pygame.draw.ellipse(surface, (min(255, pulse + 20), 80, 0), (fx - 4, fy - 2, 78, 14))
                # Núcleo de lava amarela incandescente
                pygame.draw.ellipse(surface, (255, pulse, 50), (fx + 6, fy + 2, 58, 6))

    def _draw_background(self, surface):
        """Desenha elementos ricos em múltiplos planos de paralaxe com detalhes refinados."""
        bx = -self.camera_x * 0.28
        t = pygame.time.get_ticks() / 1000.0
        
        if self.scenario_id == SCENARIO_FOREST:
            # 1. Cordilheira distante em tons azuis/cinza
            for mx in range(int(bx * 0.4) % 900 - 900, SCREEN_WIDTH + 900, 900):
                # Picos nevados distantes
                pygame.draw.polygon(surface, (80, 110, 150), [(mx, GROUND_Y), (mx + 250, 240), (mx + 550, GROUND_Y)])
                pygame.draw.polygon(surface, (220, 235, 255), [(mx + 215, 275), (mx + 250, 240), (mx + 285, 275)])
                pygame.draw.polygon(surface, (70, 95, 135), [(mx + 380, GROUND_Y), (mx + 680, 200), (mx + 980, GROUND_Y)])
                pygame.draw.polygon(surface, (220, 235, 255), [(mx + 645, 235), (mx + 680, 200), (mx + 715, 235)])
            
            # 2. Camada intermediária de pinheiros
            for px in range(int(bx * 0.7) % 180 - 180, SCREEN_WIDTH + 180, 180):
                pygame.draw.polygon(surface, (40, 95, 65), [(px, GROUND_Y), (px + 45, 340), (px + 90, GROUND_Y)])
                pygame.draw.polygon(surface, (35, 85, 55), [(px + 60, GROUND_Y), (px + 105, 360), (px + 150, GROUND_Y)])
                
            # 3. Carvalhos antigos em primeiro plano com copas detalhadas
            for i in range(-4, 18):
                tx = int(bx + 140 + i * 260)
                if -120 < tx < SCREEN_WIDTH + 120:
                    # Tronco robusto com textura
                    pygame.draw.rect(surface, (85, 55, 30), (tx, GROUND_Y - 110, 24, 110), border_radius=4)
                    pygame.draw.rect(surface, (65, 40, 20), (tx + 16, GROUND_Y - 110, 8, 110))
                    # Raízes aparentes
                    pygame.draw.polygon(surface, (85, 55, 30), [(tx - 8, GROUND_Y), (tx + 5, GROUND_Y - 18), (tx + 12, GROUND_Y)])
                    pygame.draw.polygon(surface, (85, 55, 30), [(tx + 12, GROUND_Y), (tx + 18, GROUND_Y - 18), (tx + 32, GROUND_Y)])
                    # Copa densa (esferas sobrepostas com sombreamento)
                    foliage_y = GROUND_Y - 125
                    pygame.draw.circle(surface, (25, 85, 35), (tx + 12, foliage_y), 48)
                    pygame.draw.circle(surface, (35, 115, 45), (tx + 4, foliage_y - 12), 40)
                    pygame.draw.circle(surface, (45, 135, 55), (tx + 20, foliage_y - 10), 38)
                    pygame.draw.circle(surface, (60, 155, 65), (tx + 10, foliage_y - 25), 32)
                
        elif self.scenario_id == SCENARIO_VALLEY:
            # Mesas de arenito em camadas de canyon
            for mx in range(int(bx * 0.5) % 800 - 800, SCREEN_WIDTH + 800, 800):
                # Platô rochoso
                pygame.draw.polygon(surface, (170, 105, 65), [(mx, GROUND_Y), (mx + 60, 280), (mx + 320, 280), (mx + 380, GROUND_Y)])
                # Camadas estratificadas
                pygame.draw.line(surface, (190, 125, 80), (mx + 50, 310), (mx + 330, 310), 6)
                pygame.draw.line(surface, (150, 90, 50), (mx + 35, 360), (mx + 345, 360), 8)
                
            # Ruínas de aqueduto / arcos de pedra antigos
            for rx in range(int(bx * 0.8) % 650 - 650, SCREEN_WIDTH + 650, 650):
                # Pilares
                pygame.draw.rect(surface, (160, 150, 140), (rx + 80, GROUND_Y - 160, 35, 160))
                pygame.draw.rect(surface, (160, 150, 140), (rx + 220, GROUND_Y - 160, 35, 160))
                # Arco superior
                pygame.draw.rect(surface, (175, 165, 155), (rx + 70, GROUND_Y - 185, 195, 30), border_radius=4)
                pygame.draw.arc(surface, (160, 150, 140), pygame.Rect(rx + 115, GROUND_Y - 180, 105, 80), 0, math.pi, 12)
                
        elif self.scenario_id == SCENARIO_FORTRESS:
            # Muralha imponente ao fundo com ameias e torres
            wall_top = GROUND_Y - 190
            pygame.draw.rect(surface, (55, 58, 68), (0, wall_top, SCREEN_WIDTH, 190))
            
            # Ameias no topo da muralha
            for ax in range(int(bx * 0.9) % 70 - 70, SCREEN_WIDTH + 70, 70):
                pygame.draw.rect(surface, (55, 58, 68), (ax, wall_top - 32, 38, 32))
                pygame.draw.rect(surface, (70, 74, 86), (ax, wall_top - 32, 38, 5)) # Parapeito iluminado
                # Fenda para flechas (seteira)
                pygame.draw.rect(surface, (25, 27, 34), (ax + 16, wall_top + 45, 6, 30))
                
            # Torres de vigia com telhado cônico
            for tx in range(int(bx * 0.9) % 550 - 550, SCREEN_WIDTH + 550, 550):
                # Corpo da torre
                pygame.draw.rect(surface, (65, 68, 80), (tx, wall_top - 90, 85, 280))
                pygame.draw.rect(surface, (80, 84, 98), (tx, wall_top - 90, 85, 8))
                # Telhado cônico de ardósia azul
                pygame.draw.polygon(surface, (35, 45, 70), [(tx - 8, wall_top - 90), (tx + 42, wall_top - 185), (tx + 93, wall_top - 90)])
                pygame.draw.line(surface, (210, 180, 50), (tx + 42, wall_top - 185), (tx + 42, wall_top - 205), 3) # Estandarte
                # Brasas ardendo nos suportes da torre
                fire_flicker = math.sin(t * 12.0 + tx) * 4.0
                pygame.draw.circle(surface, (255, 140, 20), (tx + 42, int(wall_top - 82 + fire_flicker)), 9)
                pygame.draw.circle(surface, (255, 240, 80), (tx + 42, int(wall_top - 84 + fire_flicker)), 5)
                
        elif self.scenario_id == SCENARIO_SWAMP:
            # Árvores decrépitas retorcidas com musgo espanhol
            for i in range(-4, 18):
                tx = int(bx + 80 + i * 220)
                if -120 < tx < SCREEN_WIDTH + 120:
                    # Tronco curvado e retorcido
                    trunk_c = (48, 38, 30)
                    pygame.draw.line(surface, trunk_c, (tx, GROUND_Y), (tx - 12, GROUND_Y - 90), 8)
                    pygame.draw.line(surface, trunk_c, (tx - 12, GROUND_Y - 90), (tx + 22, GROUND_Y - 145), 6)
                    pygame.draw.line(surface, trunk_c, (tx + 22, GROUND_Y - 145), (tx + 65, GROUND_Y - 170), 4)
                    # Galhos secos pendentes
                    pygame.draw.line(surface, trunk_c, (tx - 12, GROUND_Y - 90), (tx - 55, GROUND_Y - 120), 4)
                    # Musgo pendurado (verde-oliva translúcido)
                    moss_surf = pygame.Surface((30, 55), pygame.SRCALPHA)
                    pygame.draw.polygon(moss_surf, (80, 110, 60, 140), [(5, 0), (25, 0), (18, 45), (10, 50)])
                    surface.blit(moss_surf, (tx + 30, GROUND_Y - 145))
                    
            # Cogumelos bioluminescentes no chão
            for i in range(-3, 16):
                mx = int(bx + 160 + i * 280)
                if -50 < mx < SCREEN_WIDTH + 50:
                    # Pé do cogumelo
                    pygame.draw.rect(surface, (90, 80, 75), (mx, GROUND_Y - 22, 7, 22), border_radius=2)
                    # Chapéu brilhante com luz pulsante
                    glow = int(190 + 65 * math.sin(t * 3.0 + i))
                    shroom_c = (40, glow, 220) if i % 2 == 0 else (glow, 40, 200)
                    pygame.draw.circle(surface, shroom_c, (mx + 3, GROUND_Y - 24), 13)
                    pygame.draw.circle(surface, (255, 255, 255), (mx + 1, GROUND_Y - 26), 3)
                    
        elif self.scenario_id == SCENARIO_VOLCANO:
            # Vulcão colossal em erupção ao fundo
            vcx = SCREEN_WIDTH // 2
            # Corpo do vulcão cônico gigante
            pygame.draw.polygon(surface, (50, 32, 28), [
                (vcx - 380, GROUND_Y), (vcx - 90, 110), (vcx + 90, 110), (vcx + 380, GROUND_Y)
            ])
            # Rios de lava escorrendo pelas encostas
            pygame.draw.line(surface, (255, 100, 10), (vcx - 50, 120), (vcx - 160, GROUND_Y), 5)
            pygame.draw.line(surface, (255, 140, 20), (vcx + 40, 120), (vcx + 140, GROUND_Y), 6)
            # Cratera incandescente
            crater_glow = int(210 + 45 * math.sin(t * 4.0))
            pygame.draw.polygon(surface, (crater_glow, max(0, crater_glow - 140), 10), [
                (vcx - 80, 115), (vcx, 135), (vcx + 80, 115)
            ])
            # Coluna de fumaça subindo da cratera
            for si in range(6):
                smoke_y = 100 - si * 22
                smoke_x = vcx + math.sin(t * 2.0 + si) * 15.0
                smoke_r = 18 + si * 8
                s_surf = pygame.Surface((smoke_r * 2, smoke_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s_surf, (40, 35, 35, 120 - si * 18), (smoke_r, smoke_r), smoke_r)
                surface.blit(s_surf, (int(smoke_x - smoke_r), int(smoke_y - smoke_r)))

    def _draw_fog(self, surface):
        """Desenha bancos de nevoeiro horizontal e vaga-lumes dançantes no pântano."""
        t = pygame.time.get_ticks() / 1000.0
        fog_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Neblina rasteira
        for i in range(7):
            fx = (math.sin(t * 0.2 + i * 1.6) * 220 + i * 210) % (SCREEN_WIDTH + 300) - 150
            fy = GROUND_Y - 95 + math.sin(t * 0.4 + i) * 25
            fw = 360 + i * 40
            fh = 65 + i * 12
            alpha = int(45 + 20 * math.sin(t * 0.7 + i * 2))
            pygame.draw.ellipse(fog_surf, (140, 175, 150, alpha), (int(fx), int(fy), fw, fh))
            
        # Vaga-lumes luminosos verdes e amarelos
        for i in range(22):
            fly_x = (math.sin(t * 0.9 + i * 2.3) * 160 + i * 62 + t * 15) % SCREEN_WIDTH
            fly_y = GROUND_Y - 40 - (i * 18 + math.sin(t * 1.8 + i) * 35) % 180
            pulse = math.sin(t * 5.0 + i * 2.0)
            if pulse > 0.1:
                size = 3 if pulse > 0.7 else 2
                pygame.draw.circle(fog_surf, (180, 255, 60, int(220 * pulse)), (int(fly_x), int(fly_y)), size)
                pygame.draw.circle(fog_surf, (220, 255, 160, int(120 * pulse)), (int(fly_x), int(fly_y)), size + 2)
        
        surface.blit(fog_surf, (0, 0))
    
    def _draw_embers(self, surface):
        """Desenha brasas e cinzas incandescentes flutuando no ar do vulcão."""
        t = pygame.time.get_ticks() / 1000.0
        
        for i in range(30):
            ex = (math.sin(t * 0.9 + i * 2.7) * 140 + i * 45 + t * 25) % SCREEN_WIDTH
            ey = (GROUND_Y - 20 - i * 19 - t * 60) % (GROUND_Y - 20)
            glow = int(190 + 65 * math.sin(t * 7.0 + i))
            c = (255, max(0, glow - 110), 10) if i % 3 != 0 else (60, 50, 50)
            size = 3 if (i % 5 == 0) else 2
            pygame.draw.circle(surface, c, (int(ex), int(ey)), size)


class VictoryScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.winner = ""
        self.score_p1 = 0
        self.score_p2 = 0
        self.is_campaign = False
        self.failed_phase = 0
        self.buttons = []
        
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 100
        
        self.btn_replay = Button(cx - 320, cy, 300, 60, "REINICIAR")
        self.btn_menu = Button(cx + 20, cy, 300, 60, "MENU PRINCIPAL", lambda: self.manager.switch_scene("menu"))
        self.btn_quit = Button(cx - 150, cy + 80, 300, 60, "SAIR DO JOGO", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        
        self.buttons = [self.btn_replay, self.btn_menu, self.btn_quit]
        
        try:
            self.font_title = pygame.font.SysFont("impact", 100)
            self.font_sub = pygame.font.SysFont("impact", 40)
        except:
            self.font_title = pygame.font.Font(None, 120)
            self.font_sub = pygame.font.Font(None, 60)

    def set_args(self, winner="P1", score_p1=1, score_p2=0, is_campaign=False, failed_phase=0):
        self.winner = winner
        self.score_p1 = score_p1
        self.score_p2 = score_p2
        self.is_campaign = is_campaign
        self.failed_phase = failed_phase
        
        # Configura botão de replay
        if is_campaign:
            if failed_phase > 0:
                # Perdeu na campanha — reiniciar da fase que perdeu
                self.btn_replay.text = "TENTAR NOVAMENTE"
                self.btn_replay.action = lambda: self.manager.switch_scene("phase_intro", phase=failed_phase)
            else:
                # Completou a campanha — reiniciar do início
                self.btn_replay.text = "NOVA CAMPANHA"
                self.btn_replay.action = lambda: self.manager.switch_scene("phase_intro", phase=1)
        else:
            # PvP / PvE — replay normal
            last_mode = "pvp"
            if "game" in self.manager.scenes:
                last_mode = self.manager.scenes["game"].mode
            self.btn_replay.text = "REINICIAR"
            self.btn_replay.action = lambda: self.manager.switch_scene("game", mode=last_mode)
        
        self.manager.audio.play_music("assets/music/menu.ogg")
        if self.winner in ("P1", "CAMPEÃO"):
            self.manager.audio.play_sound("victory")
        else:
            self.manager.audio.play_sound("defeat")

    def handle_event(self, event):
        pass

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for btn in self.buttons:
            was_clicked = btn.clicked
            btn.update(mouse_pos, mouse_click)
            if btn.clicked and not was_clicked:
                self.manager.audio.play_sound("click")

    def draw(self, surface):
        surface.fill(UI_BG)
        
        if self.is_campaign and self.winner == "CAMPEÃO":
            # Campanha completada!
            color = UI_ACCENT
            text = "CAMPANHA COMPLETADA!"
            sub = f"Todas as {TOTAL_PHASES} fases conquistadas!"
        elif self.is_campaign and self.failed_phase > 0:
            # Perdeu na campanha
            color = P2_ACCENT
            text = "DERROTA!"
            sub = f"Você caiu na Fase {self.failed_phase}/{TOTAL_PHASES}"
        else:
            # PvP/PvE normal
            color = P1_ACCENT if self.winner == "P1" else P2_ACCENT
            text = "JOGADOR 1 VENCEU!" if self.winner == "P1" else ("IA VENCEU!" if self.winner == "IA" else "JOGADOR 2 VENCEU!")
            sub = f"Placar Final: {self.score_p1} x {self.score_p2}"
        
        title_surf = self.font_title.render(text, True, color)
        surface.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 150))
        
        sub_surf = self.font_sub.render(sub, True, WHITE)
        surface.blit(sub_surf, (SCREEN_WIDTH//2 - sub_surf.get_width()//2, 280))
        
        for btn in self.buttons:
            btn.draw(surface)
