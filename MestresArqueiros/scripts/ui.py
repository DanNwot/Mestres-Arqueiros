"""
Mestres Arqueiros — Componentes de Interface
Botões, HUD, barras de vida, transições e menu de pausa.
"""

import math
import pygame
from scripts.settings import *

_FONT_CACHE = {}

def get_font(size, bold=False):
    """Retorna uma fonte do sistema bonita com cache imediato para alta performance."""
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
        
    font = None
    try:
        fonts = ["segoeui", "roboto", "arial", "tahoma", "verdana"]
        avail = pygame.font.get_fonts()
        for f in fonts:
            if f in avail:
                font = pygame.font.SysFont(f, size, bold=bold)
                break
    except Exception:
        pass
        
    if font is None:
        try:
            font = pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            font = pygame.font.Font(None, int(size * 1.2))
            
    _FONT_CACHE[key] = font
    return font


def draw_gradient_rect(surface, rect, color_top, color_bottom, border_radius=0):
    """Desenha um retângulo com gradiente vertical suave e ultra-rápido via smoothscale."""
    w, h = rect.width, rect.height
    if w <= 0 or h <= 0:
        return
        
    # Superfície 1x2 escalada com interpolação bilinear de hardware
    tiny = pygame.Surface((1, 2), pygame.SRCALPHA)
    tiny.set_at((0, 0), color_top)
    tiny.set_at((0, 1), color_bottom)
    grad = pygame.transform.smoothscale(tiny, (w, h))
    
    if border_radius > 0:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=border_radius)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
    surface.blit(grad, rect.topleft)


def draw_glass_panel(surface, rect, base_color=(30, 30, 50), alpha=180, border_radius=16, border_color=None):
    """Desenha um painel com efeito glassmorphism."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # Fundo semi-transparente
    pygame.draw.rect(panel, (*base_color, alpha), panel.get_rect(), border_radius=border_radius)
    
    # Brilho no topo (simula reflexo de vidro)
    highlight_h = max(1, rect.height // 3)
    highlight_rect = pygame.Rect(0, 0, rect.width, highlight_h)
    highlight_surf = pygame.Surface((rect.width, highlight_h), pygame.SRCALPHA)
    for y in range(highlight_h):
        a = int(40 * (1 - y / highlight_h))
        pygame.draw.line(highlight_surf, (255, 255, 255, a), (0, y), (rect.width, y))
    # Aplica máscara com border radius
    mask = pygame.Surface((rect.width, highlight_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=border_radius)
    highlight_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    panel.blit(highlight_surf, (0, 0))
    
    # Borda
    if border_color is None:
        border_color = (255, 255, 255, 40)
    pygame.draw.rect(panel, border_color, panel.get_rect(), width=1, border_radius=border_radius)
    
    surface.blit(panel, rect.topleft)


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = get_font(28, bold=True)
        self.is_hovered = False
        self.clicked = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.hover_glow = 0.0  # Animação de brilho no hover

    def update(self, mouse_pos, mouse_click):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered:
            self.target_scale = 1.05
            self.hover_glow = min(1.0, self.hover_glow + 0.08)
            if mouse_click and not self.clicked:
                self.clicked = True
                if self.action:
                    self.action()
            elif not mouse_click:
                self.clicked = False
        else:
            self.target_scale = 1.0
            self.hover_glow = max(0.0, self.hover_glow - 0.06)
            self.clicked = False
            
        # Interpolação suave de escala
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface):
        is_pressed = self.is_hovered and pygame.mouse.get_pressed()[0]
        y_offset = 6 if is_pressed else 0
        
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        x = self.rect.centerx - w // 2
        y = self.rect.centery - h // 2 + y_offset
        
        draw_rect = pygame.Rect(x, y, w, h)
        
        # Glow exterior (brilho quando hover)
        if self.hover_glow > 0.01:
            glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
            glow_alpha = int(40 * self.hover_glow)
            pygame.draw.rect(glow_surf, (100, 150, 255, glow_alpha), glow_surf.get_rect(), border_radius=16)
            surface.blit(glow_surf, (x - 10, y - 10))
        
        # Sombra profunda 3D (não se move quando o botão é pressionado)
        shadow_rect = pygame.Rect(x, self.rect.centery - h // 2 + 8, w, h)
        pygame.draw.rect(surface, (10, 10, 20), shadow_rect, border_radius=12)
        
        # Gradiente de fundo do botão
        if self.is_hovered:
            top_color = (95, 135, 255)
            bot_color = (55, 85, 200)
        else:
            top_color = (60, 90, 210)
            bot_color = (30, 50, 150)
        
        draw_gradient_rect(surface, draw_rect, top_color, bot_color, border_radius=12)
        
        # Highlight/Brilho no topo
        highlight = pygame.Rect(x + w * 0.1, y + 3, w * 0.8, 3)
        hl_color = (160, 190, 255) if self.is_hovered else (100, 130, 230)
        pygame.draw.rect(surface, hl_color, highlight, border_radius=2)
        
        # Borda sutil
        pygame.draw.rect(surface, (120, 160, 255, 80) if self.is_hovered else (80, 110, 200, 60), draw_rect, width=1, border_radius=12)

        # Texto com sombra direcional
        shadow_surf = self.font.render(self.text, True, (10, 15, 40))
        text_surf = self.font.render(self.text, True, WHITE)
        
        text_rect = text_surf.get_rect(center=draw_rect.center)
        text_rect.y += 2 # Compensação visual devido ao estilo 3D
        
        surface.blit(shadow_surf, (text_rect.x, text_rect.y + 2))
        surface.blit(text_surf, text_rect)


class Toggle:
    def __init__(self, x, y, label, initial_state, action=None):
        self.rect = pygame.Rect(x, y, 60, 30)
        self.label = label
        self.state = initial_state
        self.action = action
        self.font = get_font(24)
        self.is_hovered = False
        self.clicked = False
        
        # Posição do slider do toggle
        self.slider_x = self.rect.right - 25 if self.state else self.rect.left + 5

    def update(self, mouse_pos, mouse_click):
        # Hitbox expandida para incluir o texto
        hitbox = pygame.Rect(self.rect.x, self.rect.y, self.rect.width + 200, self.rect.height)
        self.is_hovered = hitbox.collidepoint(mouse_pos)
        
        if self.is_hovered and mouse_click and not self.clicked:
            self.clicked = True
            self.state = not self.state
            if self.action:
                self.action(self.state)
        elif not mouse_click:
            self.clicked = False
            
        # Anima o slider
        target_x = self.rect.right - 25 if self.state else self.rect.left + 5
        self.slider_x += (target_x - self.slider_x) * 0.2

    def draw(self, surface):
        # Texto
        text_surf = self.font.render(self.label, True, WHITE)
        surface.blit(text_surf, (self.rect.right + 20, self.rect.centery - text_surf.get_height() // 2))
        
        # Fundo do toggle com sombra interna
        bg_color = (50, 200, 100) if self.state else (70, 70, 90)
        pygame.draw.rect(surface, (20, 20, 25), pygame.Rect(self.rect.x, self.rect.y+3, self.rect.width, self.rect.height), border_radius=15)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=15)
        
        # Slider (bolinha 3D)
        pygame.draw.circle(surface, (20, 20, 30), (int(self.slider_x) + 10, self.rect.centery + 3), 12)
        pygame.draw.circle(surface, WHITE, (int(self.slider_x) + 10, self.rect.centery), 12)


class Slider:
    def __init__(self, x, y, width, label, initial_value, action=None):
        self.rect = pygame.Rect(x, y, width, 10)
        self.label = label
        self.value = initial_value  # 0.0 a 1.0
        self.action = action
        self.font = get_font(24)
        self.is_dragging = False

    def update(self, mouse_pos, mouse_click):
        handle_rect = pygame.Rect(self.rect.x + int(self.value * self.rect.width) - 10, self.rect.centery - 10, 20, 20)
        
        # Hitbox generosa
        hitbox = self.rect.inflate(0, 40)
        
        if mouse_click:
            if hitbox.collidepoint(mouse_pos) or handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
        else:
            self.is_dragging = False
            
        if self.is_dragging:
            # Calcula novo valor baseado na posição X do mouse
            rel_x = max(0, min(mouse_pos[0] - self.rect.x, self.rect.width))
            self.value = rel_x / self.rect.width
            if self.action:
                self.action(self.value)

    def draw(self, surface):
        # Label
        text_surf = self.font.render(f"{self.label}: {int(self.value * 100)}%", True, WHITE)
        surface.blit(text_surf, (self.rect.right + 20, self.rect.centery - text_surf.get_height() // 2))
        
        # Linha de fundo com profundidade
        pygame.draw.rect(surface, (30, 30, 40), pygame.Rect(self.rect.x, self.rect.y+2, self.rect.width, self.rect.height), border_radius=5)
        pygame.draw.rect(surface, (70, 70, 90), self.rect, border_radius=5)
        
        # Linha preenchida
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.value * self.rect.width), self.rect.height)
        if filled_rect.width > 0:
            pygame.draw.rect(surface, (85, 120, 255), filled_rect, border_radius=5)
            
        # Alça (handle) 3D
        handle_x = self.rect.x + int(self.value * self.rect.width)
        pygame.draw.circle(surface, (20, 20, 30), (handle_x, self.rect.centery + 3), 14)
        pygame.draw.circle(surface, WHITE, (handle_x, self.rect.centery), 14)
        
        if self.is_dragging:
            pygame.draw.circle(surface, (130, 160, 255), (handle_x, self.rect.centery), 16, width=3)


class HealthBar:
    def __init__(self, x, y, width, height, max_health, is_right_aligned=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_health = max_health
        self.current_health = max_health
        self.target_health = max_health
        self.is_right = is_right_aligned
        self.font = get_font(18, bold=True)
        # Delayed bar for damage visualization
        self.delayed_health = max_health

    def update(self, current_health):
        self.target_health = max(0, min(current_health, self.max_health))
        # Animação suave de descida de vida
        self.current_health += (self.target_health - self.current_health) * 0.1
        # Delayed bar desce mais devagar
        if self.delayed_health > self.current_health:
            self.delayed_health += (self.current_health - self.delayed_health) * 0.03

    def draw(self, surface):
        # Sombra exterior
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=6)
        
        # Fundo escuro
        pygame.draw.rect(surface, (20, 20, 30), self.rect, border_radius=6)
        
        # Calcula cor (gradiente baseado na vida)
        health_pct = self.current_health / self.max_health
        delayed_pct = self.delayed_health / self.max_health
        
        if health_pct > 0.6:
            color_top = (80, 230, 80)
            color_bot = (40, 180, 40)
        elif health_pct > 0.3:
            color_top = (255, 230, 60)
            color_bot = (220, 170, 0)
        else:
            color_top = (255, 80, 60)
            color_bot = (200, 30, 30)
            
        # Barra de delayed damage (mostra o dano que vai ser perdido — cor mais escura)
        delayed_width = int((self.rect.width - 4) * max(delayed_pct, health_pct))
        if delayed_width > 0:
            if self.is_right:
                delayed_rect = pygame.Rect(self.rect.right - 2 - delayed_width, self.rect.y + 2, delayed_width, self.rect.height - 4)
            else:
                delayed_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, delayed_width, self.rect.height - 4)
            pygame.draw.rect(surface, (180, 60, 60), delayed_rect, border_radius=4)
        
        # Preenchimento principal com gradiente
        fill_width = int((self.rect.width - 4) * health_pct)
        if fill_width > 0:
            if self.is_right:
                fill_rect = pygame.Rect(self.rect.right - 2 - fill_width, self.rect.y + 2, fill_width, self.rect.height - 4)
            else:
                fill_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, fill_width, self.rect.height - 4)
            draw_gradient_rect(surface, fill_rect, color_top, color_bot, border_radius=4)
            
            # Brilho no topo da barra de vida
            shine_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, max(1, fill_rect.height // 3))
            shine_surf = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shine_surf, (255, 255, 255, 50), shine_surf.get_rect(), border_radius=3)
            surface.blit(shine_surf, shine_rect.topleft)
        
        # Borda
        pygame.draw.rect(surface, (80, 80, 100), self.rect, width=2, border_radius=6)
            
        # Texto centralizado
        text = f"{int(self.target_health)}/{self.max_health}"
        text_surf = self.font.render(text, True, WHITE)
        shadow = self.font.render(text, True, BLACK)
        surface.blit(shadow, (self.rect.centerx - shadow.get_width()//2 + 1, self.rect.centery - shadow.get_height()//2 + 1))
        surface.blit(text_surf, (self.rect.centerx - text_surf.get_width()//2, self.rect.centery - text_surf.get_height()//2))


class HUD:
    def __init__(self):
        self.font_large = get_font(34, bold=True)
        self.font_medium = get_font(22)
        self.font_small = get_font(16)
        self.font_icon = get_font(18, bold=True)
        
    def draw(self, surface, state):
        """
        state dict contains:
        p1_health, p1_max, p2_health, p2_max, 
        current_turn (1 or 2), 
        angle, power, arrow_name, round_text, wind (optional)
        """
        # Painel superior de fundo com glassmorphism
        top_panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 130)
        draw_glass_panel(surface, top_panel_rect, base_color=(10, 10, 20), alpha=160, border_radius=0)
        
        # Barra P1 (Esquerda)
        bar_w = 280
        p1_bar = HealthBar(20, 18, bar_w, 22, state['p1_max'])
        p1_bar.target_health = state['p1_health']
        p1_bar.current_health = state['p1_health'] # Force instant for HUD draw call
        p1_bar.delayed_health = state['p1_health']
        p1_bar.draw(surface)
        
        # Ícone P1
        pygame.draw.circle(surface, P1_PRIMARY, (12, 29), 8)
        pygame.draw.circle(surface, P1_ACCENT, (12, 29), 8, 2)
        
        p1_name = self.font_medium.render("JOGADOR 1", True, P1_ACCENT)
        surface.blit(p1_name, (20, 44))
        
        # Barra P2 (Direita)
        p2_bar = HealthBar(SCREEN_WIDTH - bar_w - 20, 18, bar_w, 22, state['p2_max'], is_right_aligned=True)
        p2_bar.target_health = state['p2_health']
        p2_bar.current_health = state['p2_health']
        p2_bar.delayed_health = state['p2_health']
        p2_bar.draw(surface)
        
        # Ícone P2
        pygame.draw.circle(surface, P2_PRIMARY, (SCREEN_WIDTH - 12, 29), 8)
        pygame.draw.circle(surface, P2_ACCENT, (SCREEN_WIDTH - 12, 29), 8, 2)
        
        p2_label = "JOGADOR 2" if not state.get('is_ai') else "IA"
        p2_name = self.font_medium.render(p2_label, True, P2_ACCENT)
        surface.blit(p2_name, (SCREEN_WIDTH - 20 - p2_name.get_width(), 44))
        
        # Placar central
        score_text = f"{state.get('p1_wins', 0)}  ×  {state.get('p2_wins', 0)}"
        score_surf = self.font_large.render(score_text, True, UI_ACCENT)
        surface.blit(score_surf, (SCREEN_WIDTH//2 - score_surf.get_width()//2, 6))
        
        # Turno Atual (Centro Top)
        turn_color = P1_ACCENT if state['current_turn'] == 1 else P2_ACCENT
        turn_text = f"TURNO: JOGADOR {state['current_turn']}"
        if state['current_turn'] == 2 and state.get('is_ai'):
            turn_text = "TURNO: IA"
            
        turn_surf = self.font_medium.render(turn_text, True, turn_color)
        surface.blit(turn_surf, (SCREEN_WIDTH//2 - turn_surf.get_width()//2, 40))
        
        # Rodada
        round_surf = self.font_small.render(state['round_text'], True, UI_TEXT)
        surface.blit(round_surf, (SCREEN_WIDTH//2 - round_surf.get_width()//2, 65))
        
        # Indicador de Fase (Campanha)
        if state.get('is_campaign') and state.get('current_phase', 0) > 0:
            from scripts.settings import TOTAL_PHASES
            phase = state['current_phase']
            indicator_y = 85
            cx = SCREEN_WIDTH // 2
            for i in range(1, TOTAL_PHASES + 1):
                ix = cx + (i - 3) * 30
                if i < phase:
                    color = (50, 200, 100)
                    radius = 5
                elif i == phase:
                    color = UI_ACCENT
                    radius = 7
                else:
                    color = (60, 60, 80)
                    radius = 4
                pygame.draw.circle(surface, color, (ix, indicator_y), radius)
        
        # Vento (se aplicável)
        if state.get('wind') is not None:
            wind = state['wind']
            wind_y = 100
            
            # Indicador visual de vento com setas
            dir_str = ">>>" if wind > 0 else "<<<"
            intensity = abs(wind) / 150.0
            wind_color_r = int(100 + 155 * intensity)
            wind_color = (wind_color_r, max(50, 200 - int(150 * intensity)), 255)
            
            wind_text = f"VENTO: {abs(wind):.0f} {dir_str}"
            wind_surf = self.font_small.render(wind_text, True, wind_color)
            surface.blit(wind_surf, (SCREEN_WIDTH//2 - wind_surf.get_width()//2, wind_y))
        
        # Info de Mira (Inferior Centro) com glassmorphism
        if state['state'] == 'aiming':
            info_w, info_h = 660, 58
            info_bg = pygame.Rect(SCREEN_WIDTH//2 - info_w//2, SCREEN_HEIGHT - 92, info_w, info_h)
            
            draw_glass_panel(surface, info_bg, base_color=(15, 15, 30), alpha=210, border_radius=14,
                           border_color=(100, 140, 255, 80))
            
            # Textos com ícones e destaque
            angle_text = f"⟨ ÂNGULO: {int(state['angle'])}° ⟩"
            power_text = f"⚡ FORÇA: {int(state['power'])}"
            type_text = f"➤ {state['arrow_name']}"
            
            t1 = self.font_medium.render(angle_text, True, WHITE)
            t2 = self.font_medium.render(power_text, True, UI_ACCENT)
            t3 = self.font_medium.render(type_text, True, (180, 210, 255))
            
            surface.blit(t1, (info_bg.left + info_bg.width//6 - t1.get_width()//2, info_bg.centery - t1.get_height()//2))
            surface.blit(t2, (info_bg.left + info_bg.width//2 - t2.get_width()//2, info_bg.centery - t2.get_height()//2))
            surface.blit(t3, (info_bg.left + info_bg.width*5//6 - t3.get_width()//2, info_bg.centery - t3.get_height()//2))
            
            # Separadores verticais sutis
            sep_color = (80, 110, 180, 90)
            pygame.draw.line(surface, sep_color, (info_bg.left + info_bg.width//3, info_bg.top + 10), 
                           (info_bg.left + info_bg.width//3, info_bg.bottom - 10), 1)
            pygame.draw.line(surface, sep_color, (info_bg.left + info_bg.width*2//3, info_bg.top + 10), 
                           (info_bg.left + info_bg.width*2//3, info_bg.bottom - 10), 1)
                           
            # Barra de Dicas de Controle (Logo abaixo da barra de mira)
            ctrl_text = "W/S ou ↑/↓: Força   •   A/D ou ←/→: Ângulo   •   ESPAÇO: Atirar   •   Q/E: Tipo de Flecha"
            ctrl_surf = self.font_small.render(ctrl_text, True, (200, 210, 240))
            cx = SCREEN_WIDTH // 2 - ctrl_surf.get_width() // 2
            cy = SCREEN_HEIGHT - 26
            
            # Fundo suave para a dica de controle
            pill_rect = pygame.Rect(cx - 16, cy - 4, ctrl_surf.get_width() + 32, ctrl_surf.get_height() + 8)
            draw_glass_panel(surface, pill_rect, base_color=(10, 10, 25), alpha=160, border_radius=10, border_color=(70, 90, 140, 50))
            surface.blit(ctrl_surf, (cx, cy))
        
        # Hint de pausa (canto superior direito, dentro do painel)
        pause_hint = self.font_small.render("ESC = Pausa", True, (160, 170, 200))
        surface.blit(pause_hint, (SCREEN_WIDTH - pause_hint.get_width() - 14, 105))


# =============================================================================
# MENU DE PAUSA
# =============================================================================
class PauseMenu:
    """Menu de pausa sobreposto ao jogo, com efeito de glassmorphism."""
    
    def __init__(self):
        self.is_active = False
        self.anim_progress = 0.0  # 0 = fechado, 1 = totalmente aberto
        
        try:
            self.font_title = pygame.font.SysFont("impact", 64)
            self.font_sub = pygame.font.SysFont("segoeui", 22)
        except:
            self.font_title = pygame.font.Font(None, 80)
            self.font_sub = pygame.font.Font(None, 26)
        
        # Botões do menu de pausa
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        
        self.btn_resume = Button(cx - 150, cy - 40, 300, 55, "CONTINUAR")
        self.btn_restart = Button(cx - 150, cy + 30, 300, 55, "REINICIAR")
        self.btn_menu = Button(cx - 150, cy + 100, 300, 55, "MENU PRINCIPAL")
        self.btn_quit = Button(cx - 150, cy + 170, 300, 55, "SAIR DO JOGO")
        
        self.buttons = [self.btn_resume, self.btn_restart, self.btn_menu, self.btn_quit]
        
        # Ações serão setadas pelo GameScene
        self.btn_quit.action = lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        # Snapshot do jogo para efeito de blur
        self.game_snapshot = None
    
    def toggle(self):
        """Alterna entre pausado e não-pausado."""
        self.is_active = not self.is_active
        if self.is_active:
            self.anim_progress = 0.0
    
    def open(self):
        self.is_active = True
        self.anim_progress = 0.0
    
    def close(self):
        self.is_active = False
    
    def set_actions(self, resume_action, restart_action, menu_action):
        """Define as ações dos botões."""
        self.btn_resume.action = resume_action
        self.btn_restart.action = restart_action
        self.btn_menu.action = menu_action
    
    def capture_snapshot(self, surface):
        """Captura o estado atual do jogo para usar como fundo."""
        self.game_snapshot = surface.copy()
    
    def handle_event(self, event):
        """Retorna True se o evento foi consumido pelo menu de pausa."""
        if not self.is_active:
            return False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        
        return True  # Consome todos os eventos quando pausado
    
    def update(self, dt):
        if not self.is_active:
            return
        
        # Anima a abertura
        self.anim_progress = min(1.0, self.anim_progress + dt * 4.0)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for btn in self.buttons:
            btn.update(mouse_pos, mouse_click)
    
    def draw(self, surface):
        if not self.is_active:
            return
        
        # Overlay escuro com animação
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_alpha = int(160 * self.anim_progress)
        overlay.fill((0, 0, 0, overlay_alpha))
        surface.blit(overlay, (0, 0))
        
        if self.anim_progress < 0.2:
            return
        
        # Painel central com glassmorphism
        panel_w = 400
        panel_h = 380
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_target_y = SCREEN_HEIGHT // 2 - panel_h // 2 - 20
        
        # Animação de slide para baixo
        slide_progress = min(1.0, (self.anim_progress - 0.1) / 0.6)
        ease = 1 - (1 - slide_progress) ** 3  # Ease-out cubic
        panel_y = int(panel_target_y - 60 + 60 * ease)
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_glass_panel(surface, panel_rect, base_color=(20, 20, 40), alpha=220, border_radius=20,
                        border_color=(100, 140, 255, 60))
        
        # Título
        title_surf = self.font_title.render("PAUSADO", True, UI_ACCENT)
        shadow_surf = self.font_title.render("PAUSADO", True, (0, 0, 0))
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        ty = panel_y + 20
        surface.blit(shadow_surf, (tx + 2, ty + 2))
        surface.blit(title_surf, (tx, ty))
        
        # Linha decorativa abaixo do título
        line_y = ty + title_surf.get_height() + 8
        line_w = 200
        line_x = SCREEN_WIDTH // 2 - line_w // 2
        pygame.draw.line(surface, (100, 140, 255, 100), (line_x, line_y), (line_x + line_w, line_y), 2)
        
        # Atualiza posição dos botões para acompanhar o painel
        btn_start_y = line_y + 20
        for i, btn in enumerate(self.buttons):
            btn.rect.x = SCREEN_WIDTH // 2 - 150
            btn.rect.y = btn_start_y + i * 70
        
        # Botões
        if slide_progress > 0.3:
            for btn in self.buttons:
                btn.draw(surface)
        
        # Dica no rodapé do painel
        hint_surf = self.font_sub.render("Pressione ESC para continuar", True, (120, 120, 160))
        surface.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, panel_y + panel_h - 35))


class FadeTransition:
    def __init__(self, duration=0.5):
        self.duration = duration
        self.time = duration
        self.is_fading = False
        self.fade_type = "in" # "in" (escuro pra claro) ou "out" (claro pra escuro)
        self.on_complete = None
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill(BLACK)

    def start(self, fade_type, on_complete=None):
        self.is_fading = True
        self.fade_type = fade_type
        self.time = 0
        self.on_complete = on_complete

    def update(self, dt):
        if not self.is_fading:
            return
            
        self.time += dt
        if self.time >= self.duration:
            self.is_fading = False
            self.time = self.duration
            if self.on_complete:
                self.on_complete()

    def draw(self, surface):
        if not self.is_fading and self.fade_type == "in" and self.time >= self.duration:
            return # Completamente invisível
            
        if self.duration <= 0:
            return
            
        progress = self.time / self.duration
        progress = max(0, min(1, progress))
        
        if self.fade_type == "in":
            alpha = int((1.0 - progress) * 255)
        else:
            alpha = int(progress * 255)
            
        self.surface.set_alpha(alpha)
        surface.blit(self.surface, (0, 0))
