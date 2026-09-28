"""
Mestres Arqueiros — Sistema de Flechas e Física Balística
Implementa a classe base e os diferentes tipos de flechas com sprites em HD e partículas.
"""

import math
import os
import random
import pygame
from scripts.settings import *

_ARROW_SPRITES = {}

def get_arrow_sprite(type_id):
    if type_id not in _ARROW_SPRITES:
        mapping = {
            ARROW_NORMAL: "arrow_normal.png",
            ARROW_HEAVY: "arrow_heavy.png",
            ARROW_EXPLOSIVE: "arrow_explosive.png",
        }
        filename = mapping.get(type_id, "arrow_normal.png")
        path = os.path.join("assets", "sprites", filename)
        if os.path.exists(path):
            try:
                _ARROW_SPRITES[type_id] = pygame.image.load(path).convert_alpha()
            except Exception:
                _ARROW_SPRITES[type_id] = None
        else:
            _ARROW_SPRITES[type_id] = None
    return _ARROW_SPRITES.get(type_id)


class Arrow:
    def __init__(self, x, y, vx, vy, type_id, owner_id):
        self.type_id = type_id
        self.owner_id = owner_id
        
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        
        # Propriedades do tipo
        props = ARROW_TYPES[type_id]
        self.name = props["name"]
        self.weight = props["weight"]
        
        # Multiplicador de velocidade no momento do disparo
        self.vx *= props["speed_mult"]
        self.vy *= props["speed_mult"]
        
        self.color = props["color"]
        self.is_active = True
        self.is_destroyed = False
        
        self.length = 34
        self.angle = math.atan2(self.vy, self.vx)
        
        self.trail = []  # [(x, y, alpha, size)]
        self.trail_timer = 0
        self.sprite = get_arrow_sprite(type_id)

    def get_damage(self, is_headshot=False):
        props = ARROW_TYPES[self.type_id]
        if is_headshot:
            return random.randint(props["head_damage_min"], props["head_damage_max"])
        else:
            return random.randint(props["damage_min"], props["damage_max"])

    def get_splash_damage(self):
        if self.type_id == ARROW_EXPLOSIVE:
            props = ARROW_TYPES[ARROW_EXPLOSIVE]
            return random.randint(props["splash_damage_min"], props["splash_damage_max"])
        return 0

    def update(self, dt, wind_power=0):
        if not self.is_active:
            return
            
        # Rastro dinâmico
        self.trail_timer -= dt
        if self.trail_timer <= 0:
            self.trail.append({
                "x": self.x,
                "y": self.y,
                "life": 0.35,
                "max_life": 0.35,
                "type": self.type_id
            })
            self.trail_timer = 0.02
            
        # Atualiza partículas do rastro
        for p in self.trail:
            p["life"] -= dt
        self.trail = [p for p in self.trail if p["life"] > 0]
            
        # Física
        # Vento (afeta X)
        self.vx += wind_power * dt
        
        # Gravidade (afeta Y com peso da flecha)
        self.vy += GRAVITY * self.weight * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Atualiza rotação baseada no vetor de velocidade
        self.angle = math.atan2(self.vy, self.vx)
        
        # Limites (saiu da arena)
        if self.x < -600 or self.x > SCREEN_WIDTH + 600 or self.y > GROUND_Y + 120:
            self.is_active = False
            self.is_destroyed = True

    def draw(self, surface, offset_x=0):
        if self.is_destroyed:
            return
            
        # 1. Desenha o rastro luminoso / de fumaça / de fogo
        for p in self.trail:
            prog = p["life"] / p["max_life"]
            px = int(p["x"] - offset_x)
            py = int(p["y"])
            alpha = int(180 * prog)
            
            if p["type"] == ARROW_EXPLOSIVE:
                # Fogo e faíscas incandescentes
                size = max(1, int(7 * prog))
                t_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                c = random.choice([(255, 140, 20), (255, 60, 10), (255, 220, 50)])
                pygame.draw.circle(t_surf, (*c, alpha), (size, size), size)
                surface.blit(t_surf, (px - size, py - size))
            elif p["type"] == ARROW_HEAVY:
                # Rastro de poeira metálica cinzenta
                size = max(1, int(4 * prog))
                t_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, (160, 165, 180, alpha), (size, size), size)
                surface.blit(t_surf, (px - size, py - size))
            else:
                # Rastro sutil de vento/velocidade ciano/branco
                size = max(1, int(3 * prog))
                t_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                c = P1_ACCENT if self.owner_id == 1 else P2_ACCENT
                pygame.draw.circle(t_surf, (*c, alpha), (size, size), size)
                surface.blit(t_surf, (px - size, py - size))

        # 2. Desenha a flecha
        arrow_deg = -math.degrees(self.angle)
        
        if self.sprite:
            # Sprite HD rotacionado
            rot_sprite = pygame.transform.rotate(self.sprite, arrow_deg)
            rect = rot_sprite.get_rect(center=(int(self.x - offset_x), int(self.y)))
            surface.blit(rot_sprite, rect.topleft)
        else:
            # Fallback procedural detalhado
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            
            head_x = (self.x - offset_x) + cos_a * (self.length / 2)
            head_y = self.y + sin_a * (self.length / 2)
            
            tail_x = (self.x - offset_x) - cos_a * (self.length / 2)
            tail_y = self.y - sin_a * (self.length / 2)
            
            # Haste da flecha
            pygame.draw.line(surface, self.color, (int(tail_x), int(tail_y)), (int(head_x), int(head_y)), 3)
            
            # Penas (cauda)
            feather_color = P1_ACCENT if self.owner_id == 1 else P2_ACCENT
            f_len = 7
            f1_x = tail_x + math.cos(self.angle + math.pi * 0.75) * f_len
            f1_y = tail_y + math.sin(self.angle + math.pi * 0.75) * f_len
            f2_x = tail_x + math.cos(self.angle - math.pi * 0.75) * f_len
            f2_y = tail_y + math.sin(self.angle - math.pi * 0.75) * f_len
            pygame.draw.line(surface, feather_color, (int(tail_x), int(tail_y)), (int(f1_x), int(f1_y)), 2)
            pygame.draw.line(surface, feather_color, (int(tail_x), int(tail_y)), (int(f2_x), int(f2_y)), 2)
            
            # Ponta
            head_color = (255, 120, 20) if self.type_id == ARROW_EXPLOSIVE else (220, 220, 240)
            h1_x = head_x - math.cos(self.angle + math.pi/5) * 8
            h1_y = head_y - math.sin(self.angle + math.pi/5) * 8
            h2_x = head_x - math.cos(self.angle - math.pi/5) * 8
            h2_y = head_y - math.sin(self.angle - math.pi/5) * 8
            pygame.draw.polygon(surface, head_color, [(int(head_x), int(head_y)), (int(h1_x), int(h1_y)), (int(h2_x), int(h2_y))])

    def get_rect(self):
        """Retorna rect minúsculo na ponta para colisão precisa."""
        head_x = self.x + math.cos(self.angle) * (self.length / 2)
        head_y = self.y + math.sin(self.angle) * (self.length / 2)
        return pygame.Rect(head_x - 3, head_y - 3, 6, 6)
