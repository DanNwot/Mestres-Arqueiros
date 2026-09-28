"""
Mestres Arqueiros — Configurações e Constantes Globais
Todas as constantes do jogo e classe de configurações mutáveis.
"""


# =============================================================================
# TELA
# =============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Mestres Arqueiros"

# =============================================================================
# FÍSICA
# =============================================================================
GRAVITY = 500.0
GROUND_Y = 550

# =============================================================================
# POSIÇÕES INICIAIS
# =============================================================================
P1_START_X = 200
P2_START_X = 1080

# =============================================================================
# CORES BÁSICAS
# =============================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# =============================================================================
# CORES DOS JOGADORES
# =============================================================================
P1_PRIMARY = (41, 98, 255)
P1_SECONDARY = (25, 60, 150)
P1_ACCENT = (100, 170, 255)

P2_PRIMARY = (220, 50, 50)
P2_SECONDARY = (150, 30, 30)
P2_ACCENT = (255, 110, 110)

# =============================================================================
# CORES DA INTERFACE
# =============================================================================
UI_BG = (20, 20, 30)
UI_BG_LIGHT = (35, 35, 50)
UI_BORDER = (60, 60, 80)
UI_TEXT = (230, 230, 240)
UI_ACCENT = (255, 210, 60)
UI_HOVER = (80, 80, 110)

# =============================================================================
# CORES DA BARRA DE VIDA
# =============================================================================
HEALTH_GREEN = (50, 200, 50)
HEALTH_YELLOW = (255, 200, 0)
HEALTH_RED = (220, 50, 50)

# =============================================================================
# CORES DE PELE
# =============================================================================
SKIN_COLOR = (235, 200, 170)
SKIN_DARK = (200, 165, 135)

# =============================================================================
# TIPOS DE FLECHAS
# =============================================================================
ARROW_NORMAL = 0
ARROW_HEAVY = 1
ARROW_EXPLOSIVE = 2

ARROW_TYPES = {
    ARROW_NORMAL: {
        "name": "Normal",
        "damage_min": 20,
        "damage_max": 40,
        "speed_mult": 1.0,
        "weight": 1.0,
        "color": (200, 200, 210),
        "head_damage_min": 50,
        "head_damage_max": 80,
    },
    ARROW_HEAVY: {
        "name": "Pesada",
        "damage_min": 30,
        "damage_max": 55,
        "speed_mult": 0.7,
        "weight": 1.5,
        "color": (120, 120, 140),
        "head_damage_min": 60,
        "head_damage_max": 90,
    },
    ARROW_EXPLOSIVE: {
        "name": "Explosiva",
        "damage_min": 20,
        "damage_max": 40,
        "speed_mult": 0.85,
        "weight": 1.2,
        "color": (255, 160, 50),
        "head_damage_min": 40,
        "head_damage_max": 65,
        "splash_damage_min": 5,
        "splash_damage_max": 25,
        "splash_radius": 80,
    },
}

# =============================================================================
# CONTROLES DE MIRA
# =============================================================================
MIN_ANGLE = 5
MAX_ANGLE = 85
MIN_POWER = 100
MAX_POWER = 800
ANGLE_SPEED = 55
POWER_SPEED = 250

# =============================================================================
# CENÁRIOS
# =============================================================================
SCENARIO_FOREST = 0
SCENARIO_VALLEY = 1
SCENARIO_FORTRESS = 2
SCENARIO_SWAMP = 3
SCENARIO_VOLCANO = 4

SCENARIO_NAMES = {
    SCENARIO_FOREST: "Floresta Antiga",
    SCENARIO_VALLEY: "Vale dos Arqueiros",
    SCENARIO_FORTRESS: "Fortaleza Real",
    SCENARIO_SWAMP: "Pântano Sombrio",
    SCENARIO_VOLCANO: "Vulcão Infernal",
}

# =============================================================================
# CONFIGURAÇÃO DE FASES (Campanha)
# =============================================================================
PHASE_CONFIG = {
    1: {
        "scenario": SCENARIO_FOREST,
        "enemy_health_mult": 1.0,
        "wind_range": (0, 0),       # Sem vento
        "ai_difficulty": 0.2,
        "title": "Fase 1 — Floresta Antiga",
        "desc": "Os primeiros desafios surgem na calma da floresta.",
    },
    2: {
        "scenario": SCENARIO_VALLEY,
        "enemy_health_mult": 1.2,
        "wind_range": (-60, 60),    # Vento leve
        "ai_difficulty": 0.4,
        "title": "Fase 2 — Vale dos Arqueiros",
        "desc": "O vento começa a soprar no vale...",
    },
    3: {
        "scenario": SCENARIO_FORTRESS,
        "enemy_health_mult": 1.4,
        "wind_range": (-100, 100),  # Vento moderado
        "ai_difficulty": 0.6,
        "title": "Fase 3 — Fortaleza Real",
        "desc": "As muralhas da fortaleza escondem perigos.",
    },
    4: {
        "scenario": SCENARIO_SWAMP,
        "enemy_health_mult": 1.6,
        "wind_range": (-130, 130),  # Vento forte
        "ai_difficulty": 0.75,
        "title": "Fase 4 — Pântano Sombrio",
        "desc": "O nevoeiro e o vento dificultam sua mira.",
    },
    5: {
        "scenario": SCENARIO_VOLCANO,
        "enemy_health_mult": 1.8,
        "wind_range": (-150, 150),  # Vento variável e forte
        "ai_difficulty": 0.9,
        "title": "Fase 5 — Vulcão Infernal",
        "desc": "O desafio final! Sobreviva ao calor do vulcão.",
    },
}

TOTAL_PHASES = 5


# =============================================================================
# CONFIGURAÇÕES MUTÁVEIS (Menu de Opções)
# =============================================================================
class GameSettings:
    """Configurações que o jogador pode alterar no menu de opções."""

    def __init__(self):
        self.music_on = True
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.blood_on = True
        self.screen_shake_on = True
        self.particles_on = True
        self.initial_health = 100
        self.rounds = 1
        self.wind_on = False
