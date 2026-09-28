"""
Mestres Arqueiros — Inteligência Artificial
Controla o jogador 2 no modo PvE, simulando pensamento e erros humanos.
"""

import math
import random
from scripts.settings import *

class AIController:
    def __init__(self, ai_player, target_player, difficulty=0.5):
        self.me = ai_player
        self.target = target_player
        self.difficulty = max(0.0, min(1.0, difficulty))  # 0.0 = fácil, 1.0 = muito difícil
        self.state = "waiting" # waiting, thinking, aiming, ready_to_shoot
        self.timer = 0
        
        self.target_angle = 0
        self.target_power = 0
        self.chosen_arrow_type = ARROW_NORMAL
        
        # Último tiro (para ajuste fino)
        self.last_power = 0
        self.last_angle = 0
        self.last_distance = 0

    def start_turn(self):
        """Inicia a rotina de turno da IA."""
        self.state = "thinking"
        # IA mais difícil pensa mais rápido
        think_time = 1.5 - self.difficulty * 0.8
        self.timer = random.uniform(max(0.3, think_time - 0.3), think_time)
        
        # Escolhe flecha — IA difícil prefere flechas melhores
        if self.difficulty > 0.7:
            weights = [30, 35, 35]
        elif self.difficulty > 0.4:
            weights = [50, 25, 25]
        else:
            weights = [70, 15, 15]
            
        self.chosen_arrow_type = random.choices(
            [ARROW_NORMAL, ARROW_HEAVY, ARROW_EXPLOSIVE], 
            weights=weights
        )[0]

    def update(self, dt, wind):
        if self.state == "waiting":
            return False
            
        self.timer -= dt
        
        if self.state == "thinking" and self.timer <= 0:
            self._calculate_shot(wind)
            self.state = "aiming"
            
        elif self.state == "aiming":
            # Anima a mira gradativamente até o alvo calculado
            # Velocidade simulada dos controles
            diff_angle = self.target_angle - self.me.angle
            diff_power = self.target_power - self.me.power
            
            # Ajusta ângulo
            if abs(diff_angle) > ANGLE_SPEED * dt:
                sign = 1 if diff_angle > 0 else -1
                if self.me.direction == -1:
                    sign = -sign
                self.me.adjust_angle(sign, dt)
            else:
                self.me.angle = self.target_angle
                
            # Ajusta potência
            if abs(diff_power) > POWER_SPEED * dt:
                sign = 1 if diff_power > 0 else -1
                self.me.adjust_power(sign, dt)
            else:
                self.me.power = self.target_power
                
            # Se chegou nos alvos de mira, atira
            if self.me.angle == self.target_angle and self.me.power == self.target_power:
                self.state = "ready_to_shoot"
                self.timer = random.uniform(0.2, 0.6) # Delay antes de soltar
                
        elif self.state == "ready_to_shoot" and self.timer <= 0:
            self.state = "waiting"
            return True # Sinaliza que deve disparar
            
        return False

    def _calculate_shot(self, wind):
        """
        Lógica heurística para encontrar um bom ângulo/potência.
        A precisão depende de self.difficulty (0.0=fácil, 1.0=quase perfeito).
        """
        # Distância em X e Y
        dx = abs(self.target.x - self.me.x)
        dy = self.target.y - self.me.y # Quase sempre 0 (chão plano)
        
        # Parâmetros da flecha
        arrow_props = ARROW_TYPES[self.chosen_arrow_type]
        g = GRAVITY * arrow_props["weight"]
        v_mult = arrow_props["speed_mult"]
        
        # Equação de trajetória básica: Range = (v^2 * sin(2*theta)) / g
        # Fixamos o ângulo em um valor razoável e achamos a velocidade, 
        # ou fixamos velocidade alta e achamos o ângulo.
        
        strategy = random.choice(["high_arc", "direct"])
        
        if strategy == "high_arc":
            # Chute inicial de ângulo alto (60 a 80 graus)
            ideal_angle_deg = random.uniform(60, 75)
            theta = math.radians(ideal_angle_deg)
            
            # v = sqrt( (dx * g) / sin(2*theta) )
            try:
                v_needed = math.sqrt((dx * g) / math.sin(2*theta))
                # Ajusta para o multiplicador da flecha
                v_needed /= v_mult
            except ValueError:
                v_needed = MAX_POWER
                
        else: # direct
            # Chute inicial de ângulo baixo (15 a 45 graus)
            ideal_angle_deg = random.uniform(20, 45)
            theta = math.radians(ideal_angle_deg)
            try:
                v_needed = math.sqrt((dx * g) / math.sin(2*theta))
                v_needed /= v_mult
            except ValueError:
                v_needed = MAX_POWER

        # Erro escala inversamente com a dificuldade
        # difficulty=0 → erro grande; difficulty=1 → erro mínimo
        error_scale = 1.0 - self.difficulty * 0.85  # de 1.0 (fácil) a 0.15 (difícil)
        
        # Adiciona erro humano dependendo da distância e dificuldade
        error_margin = (dx / 150.0) * error_scale
        
        # Aplicando ruído
        v_needed += random.uniform(-10 * error_margin, 10 * error_margin)
        ideal_angle_deg += random.uniform(-1.5 * error_margin, 1.5 * error_margin)
        
        # Compensação de vento — IA difícil compensa melhor
        if wind != 0:
            # IA é P2, atira pra X negativo.
            # Vento positivo empurra flecha pra direita (contra o tiro de P2)
            wind_accuracy = 0.2 + self.difficulty * 0.5  # 0.2 (ruim) a 0.7 (bom)
            wind_comp = wind * wind_accuracy * random.uniform(0.85, 1.15)
            v_needed += wind_comp
            
        self.target_power = max(MIN_POWER, min(MAX_POWER, v_needed))
        
        # Se for P2, o ângulo real é de 180 para trás.
        # Ex: se o ângulo calculado foi 45, P2 deve mirar em 135 (180 - 45).
        real_angle = 180 - ideal_angle_deg
        
        # Restringe aos limites
        self.target_angle = max(180 - MAX_ANGLE, min(180 - MIN_ANGLE, real_angle))
        
        # Salva valores
        self.last_angle = self.target_angle
        self.last_power = self.target_power
