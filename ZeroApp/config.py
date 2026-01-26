import pygame

# --- CONFIGURAÇÕES DE JANELA ---
WIDTH, HEIGHT = 900, 580
WIDGET_SIZE = (280, 280)
ZERO_POS_NORMAL = (610, 80)
CHAT_RECT = pygame.Rect(30, 30, 540, 450)

# --- CORES DO SISTEMA ---
BG_COLOR = (2, 2, 5)
WIDGET_BG = (0, 0, 0)
TEXT_USER = (0, 255, 120)
TEXT_ZERO = (210, 210, 210)
TEXT_SYSTEM = (100, 100, 150)

# --- DEFINIÇÕES DE "DNA" (ESTADOS EMOCIONAIS) ---
ESPECIES = {
    "neutro":    {"raio": 14, "picos": 0,  "agito": 0.5, "freq": 1.0, "cor": (180, 180, 180)},
    "zen":       {"raio": 15, "picos": 0,  "agito": 0.05, "freq": 0.1, "cor": (255, 255, 255)},
    "foco":      {"raio": 12, "picos": 12, "agito": 0.3, "freq": 5.0, "cor": (0, 180, 255)},
    "analitico": {"raio": 12, "picos": 6,  "agito": 0.8, "freq": 4.0, "cor": (0, 255, 255)},
    "criativo":  {"raio": 16, "picos": 3,  "agito": 3.0, "freq": 1.5, "cor": (150, 50, 255)},
    "alerta":    {"raio": 10, "picos": 15, "agito": 4.5, "freq": 4.0, "cor": (255, 50, 50)},
    "feliz":     {"raio": 18, "picos": 4,  "agito": 1.0, "freq": 2.0, "cor": (255, 220, 0)},
    "triste":    {"raio": 13, "picos": 2,  "agito": 0.4, "freq": 0.5, "cor": (50, 80, 150)},
    "pensativo": {"raio": 14, "picos": 5,  "agito": 1.0, "freq": 1.5, "cor": (100, 255, 200)},
    "explorar":  {"raio": 15, "picos": 10, "agito": 1.5, "freq": 2.5, "cor": (255, 100, 0)},
    "caotico":   {"raio": 8,  "picos": 15, "agito": 6.0, "freq": 6.0, "cor": (200, 0, 255)},
    "misterio":  {"raio": 14, "picos": 6,  "agito": 2.0, "freq": 0.5, "cor": (60, 60, 80)},
    "nervoso":   {"raio": 11, "picos": 20, "agito": 5.0, "freq": 7.0, "cor": (255, 120, 0)},
    "orgulhoso": {"raio": 20, "picos": 8,  "agito": 0.8, "freq": 1.2, "cor": (255, 255, 0)},
    "confuso":   {"raio": 12, "picos": 3,  "agito": 2.5, "freq": 0.5, "cor": (180, 255, 100)},
    "dormindo":  {"raio": 14, "picos": 0,  "agito": 0.2, "freq": 0.2, "cor": (40, 40, 60)}
}

# --- PERFIS DE COMPORTAMENTO ---
MODOS_SISTEMA = {
    "normal": {"escala": 1.0, "fps": 60, "dna": "neutro", "offset": (0,0)},
    "estudo": {"escala": 1.2, "fps": 30, "dna": "foco",   "offset": (0,0)},
    "jogo":   {"escala": 0.6, "fps": 20, "dna": "zen",    "offset": (0,0)}
}

# --- COMANDOS DISPONÍVEIS ---
COMANDOS = {
    "/estudo": "Ativa modo Foco, reduz FPS e aumenta escala.",
    "/jogo":   "Modo compacto, minimiza uso de CPU e move ZERO para o canto.",
    "/normal": "Restaura escala e performance padrão.",
    "/reset":  "Limpa a memória de contexto da IA.",
    "/help":   "Exibe esta lista de comandos."
}

# --- PARÂMETROS TÉCNICOS ---
FPS = 60
HIST_SIZE = 20
MEMORY_FILE = "memory.json"