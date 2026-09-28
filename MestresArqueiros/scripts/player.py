"""
Mestres Arqueiros — Classe do Jogador (Arqueiro)
Gerencia estado, física, hitboxes e renderização em alta definição com sprites e animações.
"""

import math
import os
import pygame
from scripts.settings import *

_PLAYER_SPRITES = {}

def get_player_sprite(player_id):
    if player_id not in _PLAYER_SPRITES:
        filename = f"archer_p{player_id}.png"
        path = os.path.join("assets", "sprites", filename)
        if os.path.exists(path):
            try:
                _PLAYER_SPRITES[player_id] = pygame.image.load(path).convert_alpha()
            except Exception:
                _PLAYER_SPRITES[player_id] = None
        else:
            _PLAYER_SPRITES[player_id] = None
    return _PLAYER_SPRITES.get(player_id)

_BOW_SPRITE = None

def get_bow_sprite():
    global _BOW_SPRITE
    if _BOW_SPRITE is None:
        path = os.path.join("assets", "sprites", "bow.png")
        if os.path.exists(path):
            try:
                _BOW_SPRITE = pygame.image.load(path).convert_alpha()
            except Exception:
                _BOW_SPRITE = None
    return _BOW_SPRITE


class Player:
    def __init__(self, x, id, color_primary, color_secondary):
        self.id = id
        
        # Posição base (pés)
        self.x = x
        self.y = GROUND_Y
        
        # Dimensões aproximadas do arqueiro
        self.width = 46
        self.height = 92
        
        # Vida
        self.max_health = 100
        self.health = 100
        self.is_dead = False
        
        # Física
        self.vx = 0
        self.vy = 0
        
        # Mira
        self.direction = 1 if self.id == 1 else -1  # 1=Direita, -1=Esquerda
        self.angle = 45 if self.id == 1 else 135
        self.power = 400
        
        # Estado de animação
        self.state = "idle"  # idle, aiming, shooting, hit, dead
        self.anim_timer = 0
        
        # Cores (Paleta do personagem)
        self.color_primary = color_primary
        self.color_secondary = color_secondary
        self.color_skin = SKIN_COLOR if id == 1 else SKIN_DARK
        self.color_accent = P1_ACCENT if id == 1 else P2_ACCENT
        
        # Sprites
        self.sprite = get_player_sprite(self.id)
        self.bow_sprite = get_bow_sprite()

    def set_max_health(self, amount):
        self.max_health = amount
        self.health = amount
        self.is_dead = False

    def get_hitbox(self):
        """Retorna as hitboxes precisas de corpo e cabeça para detecção de colisão."""
        base_rect = pygame.Rect(self.x - self.width//2, self.y - self.height, self.width, self.height)
        
        # Cabeça (topo - 24px)
        head_radius = 16
        head_rect = pygame.Rect(self.x - head_radius, self.y - self.height - 4, head_radius * 2, head_radius * 2 + 4)
        
        # Corpo (torso e pernas)
        body_rect = pygame.Rect(self.x - self.width//2, self.y - self.height + head_radius * 2, self.width, self.height - head_radius * 2)
        
        return {"head": head_rect, "body": body_rect, "full": base_rect}

    def take_damage(self, amount, knockback_x=0, knockback_y=0):
        if self.is_dead:
            return False
            
        self.health -= amount
        self.state = "hit"
        self.anim_timer = 0.45
        
        # Reseta o ângulo padrão
        self.angle = 45 if self.id == 1 else 135
        
        # Aplica o knockback
        self.vx = knockback_x
        self.vy = knockback_y
        
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.state = "dead"
            
        return self.is_dead

    def update(self, dt):
        # Aplica Gravidade e Movimento
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Atrito e Colisão com o Chão
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            # Atrito no chão
            self.vx -= self.vx * 6.0 * dt
            if abs(self.vx) < 5:
                self.vx = 0
                
        # Timers de animação
        if self.state in ["hit", "shooting"]:
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self.state = "idle"

    def adjust_angle(self, amount, dt):
        """Ajusta ângulo garantindo limites lógicos dependendo da direção."""
        if self.state not in ["idle", "aiming"]:
            return
            
        self.state = "aiming"
        delta = amount * ANGLE_SPEED * dt
        
        if self.direction == 1:
            self.angle += delta
            self.angle = max(MIN_ANGLE, min(MAX_ANGLE, self.angle))
        else:
            self.angle -= delta  # Invertido para P2
            self.angle = max(180 - MAX_ANGLE, min(180 - MIN_ANGLE, self.angle))

    def adjust_power(self, amount, dt):
        """Ajusta a potência do disparo."""
        if self.state not in ["idle", "aiming"]:
            return
            
        self.state = "aiming"
        self.power += amount * POWER_SPEED * dt
        self.power = max(MIN_POWER, min(MAX_POWER, self.power))

    def shoot(self):
        """Muda estado para disparo e retorna vetor de lançamento."""
        if self.state in ["hit", "dead"]:
            return None, None
            
        self.state = "shooting"
        self.anim_timer = 0.25
        
        # Componentes X e Y da velocidade da flecha
        rad = math.radians(self.angle)
        vx = math.cos(rad) * self.power
        vy = -math.sin(rad) * self.power  # Y cresce para baixo no pygame
        
        # Ponto de saída na ponta do arco
        spawn_x = self.x + math.cos(rad) * 32
        spawn_y = self.y - 50 - math.sin(rad) * 32
        
        return (spawn_x, spawn_y), (vx, vy)

    def draw(self, surface, offset_x=0):
        """Desenha o personagem com sprites em HD, sombra realista e arco articulado."""
        bx = int(self.x - offset_x)
        by = int(self.y)
        
        # 1. Sombra suave no chão
        shadow_surf = pygame.Surface((56, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (15, 20, 30, 110), (0, 0, 56, 16))
        surface.blit(shadow_surf, (bx - 28, by - 8))
        
        # 2. Se estiver morto (derrotado)
        if self.is_dead:
            # Poça de sangue sutil
            puddle_surf = pygame.Surface((70, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(puddle_surf, (140, 15, 15, 140), (0, 0, 70, 20))
            surface.blit(puddle_surf, (bx - 35, by - 6))
            
            if self.sprite:
                # Rotaciona sprite caído no chão
                rot_deg = 80 if self.direction == 1 else -80
                dead_sprite = pygame.transform.rotate(self.sprite, rot_deg)
                # Escurece
                dark_surf = pygame.Surface(dead_sprite.get_size(), pygame.SRCALPHA)
                dark_surf.fill((60, 60, 80, 100))
                dead_sprite.blit(dark_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(dead_sprite, (bx - dead_sprite.get_width()//2, by - dead_sprite.get_height() + 10))
            else:
                # Fallback de arqueiro caído
                pygame.draw.rect(surface, (80, 80, 90), (bx - 35, by - 22, 70, 20), border_radius=6)
                pygame.draw.circle(surface, self.color_skin, (bx + self.direction * 35, by - 12), 12)
            return

        # 3. Animação de respiração / idle
        breathe = 0
        if self.state in ["idle", "aiming"]:
            breathe = math.sin(pygame.time.get_ticks() / 320.0) * 2.0
            
        render_y = by - 110 + int(breathe)
        
        # 4. Desenho do Arqueiro (Sprite ou Procedural)
        if self.sprite:
            char_surf = self.sprite.copy()
            
            # Se tomou dano (flash vermelho)
            if self.state == "hit":
                flash_surf = pygame.Surface(char_surf.get_size(), pygame.SRCALPHA)
                flash_surf.fill((255, 80, 80, 180))
                char_surf.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
            surface.blit(char_surf, (bx - 50, render_y))
        else:
            # Fallback procedural
            self._draw_procedural_body(surface, bx, by, breathe)
            
        # 5. Desenho do Arco e Corda (Articulado com a mira)
        self._draw_bow_and_arrow(surface, bx, by, breathe)

    def _draw_bow_and_arrow(self, surface, bx, by, breathe):
        """Renderiza o arco giratório, a corda esticada e a flecha engatilhada."""
        shoulder_x = bx + (self.direction * 6)
        shoulder_y = by - 56 + int(breathe)
        
        rad = math.radians(self.angle)
        dir_x = math.cos(rad)
        dir_y = -math.sin(rad)
        
        # Distância do braço da frente
        arm_len = 24
        hand_x = shoulder_x + dir_x * arm_len
        hand_y = shoulder_y + dir_y * arm_len
        
        # Distância do recuo da corda baseada na potência
        pull_factor = (self.power - MIN_POWER) / max(1, (MAX_POWER - MIN_POWER))
        pull_dist = 6 + pull_factor * 22
        
        back_hand_x = hand_x - dir_x * pull_dist
        back_hand_y = hand_y - dir_y * pull_dist
        
        # Comprimento e ângulo do arco
        bow_radius = 28
        perp_x = -dir_y
        perp_y = dir_x
        
        # Pontas do arco
        tip1_x = hand_x + perp_x * bow_radius - dir_x * 4
        tip1_y = hand_y + perp_y * bow_radius - dir_y * 4
        
        tip2_x = hand_x - perp_x * bow_radius - dir_x * 4
        tip2_y = hand_y - perp_y * bow_radius - dir_y * 4
        
        # Arco curvado (madeira nobre com sombreamento)
        curve_pts = [
            (int(tip1_x), int(tip1_y)),
            (int(hand_x + dir_x * 6), int(hand_y + dir_y * 6)),
            (int(tip2_x), int(tip2_y))
        ]
        # Sombra do arco
        pygame.draw.lines(surface, (70, 40, 15), False, [(p[0] + 1, p[1] + 1) for p in curve_pts], 4)
        # Corpo do arco
        pygame.draw.lines(surface, (165, 95, 40), False, curve_pts, 3)
        # Detalhe dourado nas pontas
        pygame.draw.circle(surface, (230, 190, 60), (int(tip1_x), int(tip1_y)), 3)
        pygame.draw.circle(surface, (230, 190, 60), (int(tip2_x), int(tip2_y)), 3)
        
        # Corda do arco
        if self.state in ["aiming", "idle"]:
            # Corda puxada até a mão de trás
            pygame.draw.line(surface, (245, 245, 255), (int(tip1_x), int(tip1_y)), (int(back_hand_x), int(back_hand_y)), 1)
            pygame.draw.line(surface, (245, 245, 255), (int(tip2_x), int(tip2_y)), (int(back_hand_x), int(back_hand_y)), 1)
            
            # Braço de trás puxando a corda
            pygame.draw.line(surface, self.color_secondary, (shoulder_x - self.direction * 6, shoulder_y + 2), (int(back_hand_x), int(back_hand_y)), 4)
            pygame.draw.circle(surface, (75, 48, 25), (int(back_hand_x), int(back_hand_y)), 4)  # Luva
            
            # Flecha carregada no arco
            arrow_tip_x = hand_x + dir_x * 20
            arrow_tip_y = hand_y + dir_y * 20
            pygame.draw.line(surface, (210, 180, 130), (int(back_hand_x), int(back_hand_y)), (int(arrow_tip_x), int(arrow_tip_y)), 2)
            # Ponta da flecha
            pygame.draw.circle(surface, (230, 230, 240), (int(arrow_tip_x), int(arrow_tip_y)), 2)
        else:
            # Corda solta reta
            pygame.draw.line(surface, (245, 245, 255), (int(tip1_x), int(tip1_y)), (int(tip2_x), int(tip2_y)), 1)

        # Braço da frente segurando o arco
        pygame.draw.line(surface, self.color_secondary, (shoulder_x, shoulder_y), (int(hand_x), int(hand_y)), 4)
        pygame.draw.circle(surface, (75, 48, 25), (int(hand_x), int(hand_y)), 4)

        # 6. Indicador visual sutil da trajetória inicial (primeiros 6 pontos)
        if self.state == "aiming":
            self._draw_trajectory_dots(surface, hand_x, hand_y, dir_x, dir_y)

    def _draw_trajectory_dots(self, surface, sx, sy, dx, dy):
        """Desenha pontos discretos e elegantes mostrando a direção inicial."""
        v0 = self.power * 0.95
        vx = dx * v0
        vy = dy * v0
        
        t_step = 0.05
        cur_x = sx
        cur_y = sy
        
        for step in range(1, 8):
            t = step * t_step
            dot_x = cur_x + vx * t
            dot_y = cur_y + vy * t + 0.5 * GRAVITY * (t ** 2)
            
            # Ponto elegante com alpha decrescente
            alpha = max(20, int(220 * (1.0 - step / 8.0)))
            size = max(1, 4 - step // 2)
            dot_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (*self.color_accent, alpha), (size, size), size)
            surface.blit(dot_surf, (int(dot_x - size), int(dot_y - size)))

    def _draw_procedural_body(self, surface, bx, by, breathe):
        """Fallback procedural com alta qualidade caso o sprite não carregue."""
        c_prim = (255, 100, 100) if self.state == "hit" else self.color_primary
        c_sec = self.color_secondary
        c_skin = self.color_skin
        
        leg_w, leg_h = 11, 32
        pygame.draw.rect(surface, c_sec, (bx - 14, by - leg_h, leg_w, leg_h), border_radius=4)
        pygame.draw.rect(surface, c_sec, (bx + 3, by - leg_h, leg_w, leg_h), border_radius=4)
        
        trunk_w, trunk_h = 26, 38
        trunk_y = by - leg_h - trunk_h + int(breathe)
        pygame.draw.rect(surface, c_prim, (bx - trunk_w//2, trunk_y, trunk_w, trunk_h), border_radius=6)
        
        head_r = 15
        head_y = trunk_y - head_r - 2
        pygame.draw.circle(surface, c_skin, (bx, head_y), head_r)
        pygame.draw.arc(surface, c_sec, (bx - head_r, head_y - head_r, head_r*2, head_r*2), 0, math.pi, 4)
