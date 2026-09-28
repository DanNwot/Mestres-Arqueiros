"""
Mestres Arqueiros — Efeitos Visuais
Sistema de partículas em alta definição, sangue, explosões, brasas e números de dano animados.
"""

import math
import random
import pygame

_EFFECT_FONTS = {}

def get_effect_font(size, bold=True):
    key = (size, bold)
    if key not in _EFFECT_FONTS:
        try:
            for fname in ["impact", "arialblack", "trebuchetms", "segoeui"]:
                try:
                    f = pygame.font.SysFont(fname, size, bold=bold)
                    if f:
                        _EFFECT_FONTS[key] = f
                        break
                except Exception:
                    continue
        except Exception:
            pass
        if key not in _EFFECT_FONTS:
            _EFFECT_FONTS[key] = pygame.font.Font(None, int(size * 1.2))
    return _EFFECT_FONTS[key]


class Particle:
    def __init__(self, x, y, vx, vy, life, color, size, gravity_effect=1.0, shape="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity_effect = gravity_effect
        self.shape = shape
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

    def update(self, dt, gravity):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gravity * self.gravity_effect * dt
        self.angle += self.rot_speed * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface, offset_x=0):
        if self.life <= 0:
            return
        
        prog = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(255 * prog)
        cur_size = max(1, int(self.size * prog))
        
        px = int(self.x - offset_x)
        py = int(self.y)
        
        if self.shape == "spark":
            # Traço fino de faísca
            l = cur_size * 2
            rad = math.radians(self.angle)
            dx = math.cos(rad) * l
            dy = math.sin(rad) * l
            pygame.draw.line(surface, (*self.color, alpha), (px - dx, py - dy), (px + dx, py + dy), max(1, cur_size // 2))
        else:
            surf = pygame.Surface((cur_size * 2, cur_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (cur_size, cur_size), cur_size)
            surface.blit(surf, (px - cur_size, py - cur_size))


class ParticleSystem:
    def __init__(self, settings):
        self.settings = settings
        self.particles = []

    def add_particle(self, particle):
        if self.settings.particles_on:
            self.particles.append(particle)

    def update(self, dt, gravity):
        self.particles = [p for p in self.particles if p.update(dt, gravity)]

    def draw(self, surface, offset_x=0):
        for p in self.particles:
            p.draw(surface, offset_x)


class BloodEffect:
    @staticmethod
    def spawn(x, y, particle_system, amount=16):
        if not particle_system.settings.blood_on:
            return
        
        for _ in range(amount):
            vx = random.uniform(-180, 180)
            vy = random.uniform(-260, 40)
            life = random.uniform(0.4, 1.2)
            size = random.uniform(2.5, 6.0)
            
            # Matizes de sangue realista (vermelho vivo a carmesim escuro)
            r = random.randint(180, 255)
            g = random.randint(10, 35)
            b = random.randint(10, 35)
            
            p = Particle(x, y, vx, vy, life, (r, g, b), size, gravity_effect=0.85)
            particle_system.add_particle(p)


class ExplosionEffect:
    @staticmethod
    def spawn(x, y, particle_system, radius=80):
        if not particle_system.settings.particles_on:
            return
            
        # Clarão luminoso central
        particle_system.add_particle(Particle(x, y, 0, 0, 0.25, (255, 255, 220), radius, gravity_effect=0))
        
        # Bolas de fogo incandescentes
        for _ in range(35):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 380)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.3, 0.75)
            size = random.uniform(6, 16)
            
            color = random.choice([
                (255, 140, 0), (255, 210, 20), (255, 60, 10), (240, 240, 200), (90, 80, 80)
            ])
            
            p = Particle(x, y, vx, vy, life, color, size, gravity_effect=0.2)
            particle_system.add_particle(p)

        # Faíscas velozes
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(180, 450)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.2, 0.5)
            p = Particle(x, y, vx, vy, life, (255, 220, 100), 3, gravity_effect=0.4, shape="spark")
            particle_system.add_particle(p)


class DustEffect:
    @staticmethod
    def spawn(x, y, particle_system, amount=12):
        if not particle_system.settings.particles_on:
            return
            
        for _ in range(amount):
            vx = random.uniform(-70, 70)
            vy = random.uniform(-110, -10)
            life = random.uniform(0.4, 0.9)
            size = random.uniform(3, 7)
            
            color = (random.randint(110, 150), random.randint(95, 130), random.randint(80, 110))
            p = Particle(x, y, vx, vy, life, color, size, gravity_effect=0.25)
            particle_system.add_particle(p)


class DamageNumber:
    def __init__(self, x, y, amount, is_critical=False):
        self.x = x
        self.y = y
        self.amount = amount
        self.is_critical = is_critical
        self.life = 1.4
        self.max_life = 1.4
        self.vy = -110
        self.scale_timer = 0.0
        
        self.font = get_effect_font(38 if is_critical else 26, bold=True)
            
        self.text = f"-{amount}"
        if is_critical:
            self.text = f"★ {amount} CRÍTICO! ★"
            self.color = (255, 215, 0)
        else:
            self.color = (255, 255, 255)

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 40 * dt  # Desacelera a subida
        self.scale_timer += dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface, offset_x=0):
        if self.life <= 0:
            return
            
        prog = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(255 * prog)
        
        # Pop inicial (efeito de impacto)
        if self.scale_timer < 0.15:
            scale = 1.0 + (0.15 - self.scale_timer) * 2.0
        else:
            scale = 1.0
            
        text_surf = self.font.render(self.text, True, self.color)
        outline_surf = self.font.render(self.text, True, (0, 0, 0))
        
        if scale != 1.0:
            nw = int(text_surf.get_width() * scale)
            nh = int(text_surf.get_height() * scale)
            text_surf = pygame.transform.scale(text_surf, (nw, nh))
            outline_surf = pygame.transform.scale(outline_surf, (nw, nh))
            
        text_surf.set_alpha(alpha)
        outline_surf.set_alpha(alpha)
        
        w, h = text_surf.get_size()
        pos = (int(self.x - offset_x - w/2), int(self.y - h/2))
        
        # Contorno sombreado 8-way
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            surface.blit(outline_surf, (pos[0] + dx, pos[1] + dy))
            
        surface.blit(text_surf, pos)


class ScreenShake:
    def __init__(self, settings):
        self.settings = settings
        self.intensity = 0
        self.duration = 0
        self.offset = [0, 0]

    def trigger(self, intensity, duration):
        if not self.settings.screen_shake_on:
            return
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            current_intensity = self.intensity * (self.duration / max(0.001, self.duration + dt))
            self.offset = [
                random.uniform(-current_intensity, current_intensity),
                random.uniform(-current_intensity, current_intensity)
            ]
        else:
            self.offset = [0, 0]
            self.intensity = 0

    def get_offset(self):
        return self.offset
