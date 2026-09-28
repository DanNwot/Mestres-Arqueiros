"""
Mestres Arqueiros — Gerador de Sprites em Alta Definição
Gera sprites nítidos e detalhados em assets/sprites/ com sombreamento e efeitos.
"""

import os
import math
import pygame

os.makedirs("assets/sprites", exist_ok=True)
pygame.init()

def create_archer_sprite(primary_color, secondary_color, skin_color, accent_color, is_p1=True):
    """Gera um arqueiro medieval altamente estilizado e detalhado (100x120px)."""
    surf = pygame.Surface((100, 120), pygame.SRCALPHA)
    
    # Centro do arqueiro no sprite
    cx = 50
    ground_y = 115
    
    # 1. Aljava nas costas (Quiver) com flechas visíveis
    quiver_rect = pygame.Rect(cx - 24 if is_p1 else cx + 10, ground_y - 82, 14, 46)
    # Rotação leve da aljava
    q_surf = pygame.Surface((20, 50), pygame.SRCALPHA)
    pygame.draw.rect(q_surf, (80, 50, 25), (4, 10, 12, 38), border_radius=4)
    pygame.draw.rect(q_surf, (110, 75, 40), (4, 10, 12, 38), width=1, border_radius=4)
    pygame.draw.line(q_surf, (180, 140, 50), (4, 18), (15, 18), 2) # Fivela dourada
    # Penas das flechas saindo da aljava
    for fi, fo in enumerate([-3, 0, 3]):
        feather_c = (230, 230, 240) if fi % 2 == 0 else accent_color
        pygame.draw.line(q_surf, (160, 130, 90), (10 + fo, 12), (10 + fo * 1.5, 2), 2)
        pygame.draw.polygon(q_surf, feather_c, [(10 + fo * 1.5, 2), (8 + fo * 1.5, 6), (12 + fo * 1.5, 6)])
    
    q_rot = pygame.transform.rotate(q_surf, -15 if is_p1 else 15)
    surf.blit(q_rot, (cx - 28 if is_p1 else cx + 8, ground_y - 88))
    
    # 2. Pernas e Botas de Couro
    # Perna traseira
    leg_back_x = cx - 14 if is_p1 else cx + 4
    pygame.draw.rect(surf, (40, 40, 50), (leg_back_x, ground_y - 45, 10, 28), border_radius=3)
    # Bota traseira
    pygame.draw.rect(surf, (60, 40, 25), (leg_back_x - 1, ground_y - 20, 12, 19), border_radius=3)
    pygame.draw.rect(surf, (90, 60, 35), (leg_back_x - 1, ground_y - 20, 12, 4)) # Aba da bota
    
    # Perna dianteira
    leg_front_x = cx + 2 if is_p1 else cx - 12
    pygame.draw.rect(surf, secondary_color, (leg_front_x, ground_y - 45, 11, 28), border_radius=3)
    # Bota dianteira
    pygame.draw.rect(surf, (75, 48, 30), (leg_front_x - 2, ground_y - 20, 14, 20), border_radius=4)
    pygame.draw.rect(surf, (110, 75, 45), (leg_front_x - 2, ground_y - 20, 14, 4))
    
    # 3. Tronco e Túnica/Armadura
    trunk_w = 26
    trunk_h = 36
    trunk_x = cx - trunk_w // 2
    trunk_y = ground_y - 78
    
    # Camada base da túnica
    pygame.draw.rect(surf, primary_color, (trunk_x, trunk_y, trunk_w, trunk_h), border_radius=6)
    
    # Detalhe de ombreira de couro / cota
    shoulder_w = trunk_w + 6
    pygame.draw.rect(surf, (65, 45, 30), (cx - shoulder_w // 2, trunk_y, shoulder_w, 10), border_radius=4)
    pygame.draw.rect(surf, accent_color, (cx - shoulder_w // 2, trunk_y + 8, shoulder_w, 2)) # Friso dourado/vermelho
    
    # Cinto com fivela dourada
    belt_y = trunk_y + trunk_h - 10
    pygame.draw.rect(surf, (45, 30, 20), (trunk_x - 1, belt_y, trunk_w + 2, 7))
    pygame.draw.rect(surf, (220, 180, 50), (cx - 4, belt_y + 1, 8, 5), border_radius=1)
    
    # Faixa transversal (Bandoleira do peito)
    strap_pts = [(trunk_x + 3, trunk_y + 2), (trunk_x + trunk_w - 4, belt_y + 5), 
                 (trunk_x + trunk_w - 7, belt_y + 6), (trunk_x, trunk_y + 5)]
    pygame.draw.polygon(surf, (55, 35, 20), strap_pts)
    
    # 4. Cabeça, Capuz/Cabelo e Rosto
    head_r = 13
    head_cx = cx
    head_cy = trunk_y - head_r - 2
    
    # Capuz/Cabelo (fundo)
    pygame.draw.circle(surf, secondary_color, (head_cx, head_cy), head_r + 2)
    # Rosto (pele)
    pygame.draw.circle(surf, skin_color, (head_cx + (2 if is_p1 else -2), head_cy), head_r - 1)
    # Capuz/Elmo (topo e laterais)
    pygame.draw.arc(surf, primary_color, (head_cx - head_r - 1, head_cy - head_r - 2, (head_r + 1) * 2, (head_r + 1) * 2), 
                    0.2, math.pi - 0.2, 5)
    
    # Olho expressivo
    eye_x = head_cx + (5 if is_p1 else -5)
    eye_y = head_cy - 1
    # Esclera branca
    pygame.draw.ellipse(surf, (240, 240, 255), (eye_x - 3, eye_y - 2, 6, 4))
    # Íris/Pupila
    pupil_c = (30, 90, 180) if is_p1 else (200, 40, 40)
    pygame.draw.circle(surf, pupil_c, (eye_x + (1 if is_p1 else -1), eye_y), 2)
    # Sobrancelha focada
    pygame.draw.line(surf, (40, 25, 15), (eye_x - 4, eye_y - 4), (eye_x + 3, eye_y - 3), 2)
    
    # Faixa/Bandana na testa com nó e ponta flutuante
    headband_y = head_cy - 6
    pygame.draw.rect(surf, accent_color, (head_cx - head_r + 1, headband_y, head_r * 2 - 2, 3), border_radius=1)
    # Ponta da fita balançando atrás da cabeça
    ribbon_x = head_cx - (head_r + 2 if is_p1 else -head_r)
    pygame.draw.line(surf, accent_color, (ribbon_x, headband_y + 1), (ribbon_x - (10 if is_p1 else -10), headband_y + 8), 3)
    pygame.draw.line(surf, accent_color, (ribbon_x - (10 if is_p1 else -10), headband_y + 8), (ribbon_x - (16 if is_p1 else -16), headband_y + 6), 2)
    
    # 5. Braços e Manoplas
    arm_x = cx + (8 if is_p1 else -8)
    arm_y = trunk_y + 10
    # Ombro
    pygame.draw.circle(surf, secondary_color, (arm_x, arm_y), 6)
    # Braço dianteiro
    hand_x = cx + (20 if is_p1 else -20)
    hand_y = arm_y + 16
    pygame.draw.line(surf, secondary_color, (arm_x, arm_y), (hand_x, hand_y), 5)
    # Luva/Manopla de couro
    pygame.draw.circle(surf, (80, 50, 30), (hand_x, hand_y), 5)
    
    return surf

def create_bow_sprite():
    """Gera um arco recurvo finamente desenhado (40x80px)."""
    surf = pygame.Surface((40, 80), pygame.SRCALPHA)
    
    # Curva elegante do arco de teixo/madeira nobre
    pts = [
        (8, 6), (18, 18), (24, 30), (26, 40), (24, 50), (18, 62), (8, 74)
    ]
    # Sombra da madeira
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (80, 45, 20), (pts[i][0] + 1, pts[i][1]), (pts[i+1][0] + 1, pts[i+1][1]), 5)
    # Corpo do arco
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (150, 85, 35), pts[i], pts[i+1], 4)
    # Friso metálico nos nós
    pygame.draw.circle(surf, (220, 180, 60), (26, 40), 4) # Empunhadura
    pygame.draw.circle(surf, (230, 200, 80), (8, 6), 3)   # Ponta superior
    pygame.draw.circle(surf, (230, 200, 80), (8, 74), 3)  # Ponta inferior
    
    # Corda de linho reforçada
    pygame.draw.line(surf, (240, 240, 255), (8, 6), (12, 40), 1)
    pygame.draw.line(surf, (240, 240, 255), (12, 40), (8, 74), 1)
    
    return surf

def create_arrow_sprites():
    """Gera sprites individuais de cada tipo de flecha (50x16px)."""
    arrows = {}
    
    # 1. Flecha Normal
    s_norm = pygame.Surface((50, 16), pygame.SRCALPHA)
    # Haste de madeira polida
    pygame.draw.line(s_norm, (180, 140, 95), (6, 8), (42, 8), 3)
    pygame.draw.line(s_norm, (215, 175, 125), (6, 7), (42, 7), 1) # Brilho
    # Penas fletching azuis e brancas
    pygame.draw.polygon(s_norm, (60, 130, 240), [(6, 8), (2, 3), (12, 3), (10, 8)])
    pygame.draw.polygon(s_norm, (220, 230, 255), [(6, 8), (2, 13), (12, 13), (10, 8)])
    # Ponta de ferro triangular afiada
    pygame.draw.polygon(s_norm, (220, 225, 235), [(42, 4), (49, 8), (42, 12)])
    pygame.draw.polygon(s_norm, (150, 155, 165), [(42, 8), (49, 8), (42, 12)])
    arrows["arrow_normal"] = s_norm
    
    # 2. Flecha Pesada (Broadhead de Ferro Escuro)
    s_hvy = pygame.Surface((50, 16), pygame.SRCALPHA)
    # Haste de freixo reforçada com tiras metálicas
    pygame.draw.line(s_hvy, (100, 75, 55), (6, 8), (40, 8), 4)
    pygame.draw.line(s_hvy, (130, 135, 145), (15, 6), (17, 10), 2)
    pygame.draw.line(s_hvy, (130, 135, 145), (28, 6), (30, 10), 2)
    # Penas cinza-chumbo
    pygame.draw.polygon(s_hvy, (90, 90, 105), [(6, 8), (1, 2), (14, 2), (11, 8)])
    pygame.draw.polygon(s_hvy, (70, 70, 85), [(6, 8), (1, 14), (14, 14), (11, 8)])
    # Ponta maciça serrilhada
    pygame.draw.polygon(s_hvy, (170, 175, 185), [(40, 2), (50, 8), (40, 14), (43, 8)])
    arrows["arrow_heavy"] = s_hvy
    
    # 3. Flecha Explosiva
    s_exp = pygame.Surface((50, 16), pygame.SRCALPHA)
    # Haste escura encantada
    pygame.draw.line(s_exp, (80, 50, 40), (6, 8), (38, 8), 3)
    # Penas de fênix vermelho-alaranjadas
    pygame.draw.polygon(s_exp, (240, 70, 20), [(6, 8), (1, 2), (13, 2), (10, 8)])
    pygame.draw.polygon(s_exp, (255, 160, 40), [(6, 8), (1, 14), (13, 14), (10, 8)])
    # Frasco / Ogiva explosiva incandescente com brilho
    pygame.draw.circle(s_exp, (255, 180, 30), (41, 8), 5)
    pygame.draw.polygon(s_exp, (255, 60, 10), [(41, 4), (49, 8), (41, 12)])
    pygame.draw.circle(s_exp, (255, 255, 200), (41, 8), 2) # Núcleo brilhante
    arrows["arrow_explosive"] = s_exp
    
    return arrows

def create_wind_indicator_sprite():
    """Gera o cata-vento / bandeira de direção de vento (60x60px)."""
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    # Haste dourada com esfera no topo
    pygame.draw.line(surf, (150, 120, 40), (30, 15), (30, 55), 3)
    pygame.draw.circle(surf, (220, 180, 50), (30, 14), 4)
    # Base de pedra
    pygame.draw.ellipse(surf, (100, 100, 110), (22, 50, 16, 8))
    # Flâmula / Bandeira (será rotacionada/esticada em tempo real)
    pygame.draw.polygon(surf, (220, 60, 60), [(30, 18), (52, 25), (30, 32)])
    return surf

if __name__ == "__main__":
    from scripts.settings import P1_PRIMARY, P1_SECONDARY, P1_ACCENT, P2_PRIMARY, P2_SECONDARY, P2_ACCENT, SKIN_COLOR, SKIN_DARK
    
    # 1. Arqueiro P1
    p1_sprite = create_archer_sprite(P1_PRIMARY, P1_SECONDARY, SKIN_COLOR, P1_ACCENT, is_p1=True)
    pygame.image.save(p1_sprite, "assets/sprites/archer_p1.png")
    
    # 2. Arqueiro P2
    p2_sprite = create_archer_sprite(P2_PRIMARY, P2_SECONDARY, SKIN_DARK, P2_ACCENT, is_p1=False)
    pygame.image.save(p2_sprite, "assets/sprites/archer_p2.png")
    
    # 3. Arco
    bow_sprite = create_bow_sprite()
    pygame.image.save(bow_sprite, "assets/sprites/bow.png")
    
    # 4. Flechas
    arrow_sprites = create_arrow_sprites()
    for name, s in arrow_sprites.items():
        pygame.image.save(s, f"assets/sprites/{name}.png")
        
    # 5. Cata-vento
    wind_sprite = create_wind_indicator_sprite()
    pygame.image.save(wind_sprite, "assets/sprites/wind_indicator.png")
    
    print("All game sprites created successfully in assets/sprites/!")
