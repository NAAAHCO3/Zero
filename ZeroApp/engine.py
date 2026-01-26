import pygame
import numpy as np
import random
import math
from config import ZERO_POS_NORMAL

class ZeroEngine:
    def __init__(self, size=64, pixel_size=4):
        self.size = size
        self.pixel_size = pixel_size
        self.fundo_cor = (5, 5, 10)
        
        y, x = np.ogrid[-size//2 : size//2, -size//2 : size//2]
        self.dist_map = np.sqrt(x**2 + y**2)
        self.angle_map = np.arctan2(y, x)
        
        self.current_dna = {
            "raio": 14, "picos": 0, "agito": 0.5, "freq": 1.0, "cor": (180, 180, 180)
        }
        self.transition_speed = 0.08

    def update(self, target_dna):
        for k in ["raio", "picos", "agito", "freq"]:
            self.current_dna[k] += (target_dna[k] - self.current_dna[k]) * self.transition_speed
        
        c_curr = np.array(self.current_dna["cor"])
        c_targ = np.array(target_dna["cor"])
        new_color = c_curr + (c_targ - c_curr) * self.transition_speed
        self.current_dna["cor"] = tuple(new_color.astype(int))

    def draw(self, screen, frame, emotion_name="neutro", pos=ZERO_POS_NORMAL, scale_mult=1, is_speaking=False):
        dna = self.current_dna
        
        # --- 1. CÁLCULO DA RESPIRAÇÃO REATIVA ---
        tempo_vida = pygame.time.get_ticks() * 0.002
        
        # Se estiver falando, o pulso fica mais rápido e forte
        freq_voz = 2.5 if is_speaking else 1.0
        amp_voz = 0.12 if is_speaking else 0.06
        
        pulso = 1.0 + amp_voz * math.sin(tempo_vida * dna["freq"] * freq_voz)
        
        # Jitter extra se estiver falando (tremor de voz digital)
        jitter = random.uniform(-0.6, 0.6) if is_speaking else (random.uniform(-0.2, 0.2) if dna["agito"] > 3 else 0)
        
        # --- 2. RENDERIZAÇÃO DO GLOW DINÂMICO ---
        cor_base = dna["cor"]
        pix = self.pixel_size * scale_mult
        raio_real = dna["raio"] * pulso * pix
        centro_absoluto = (pos[0] + (self.size * pix) // 2, pos[1] + (self.size * pix) // 2)

        # Se falar, o brilho (Alpha) dobra de intensidade
        alpha_base = 90 if is_speaking else 45

        for i in range(3, 0, -1):
            raio_g = raio_real + (i * 12 * scale_mult)
            alpha = int(alpha_base / i)
            s = pygame.Surface((raio_g * 2, raio_g * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*cor_base, alpha), (raio_g, raio_g), raio_g)
            screen.blit(s, (centro_absoluto[0] - raio_g, centro_absoluto[1] - raio_g))

        # --- 3. CONSTRUÇÃO DO CORPO ---
        t = frame * dna["freq"] * 0.15 
        surf = pygame.Surface((self.size, self.size))
        surf.fill(self.fundo_cor)
        
        mod = np.sin(dna["picos"] * self.angle_map + t) * dna["agito"]
        mod += (dna["agito"] / 2) * np.cos(4 * self.angle_map - t)
        
        # Threshold agora reage ao pulso e jitter de voz
        threshold_map = (dna["raio"] * pulso + jitter) + mod
        
        mask = self.dist_map < threshold_map
        indices = np.argwhere(mask)
        
        prob_noise = 0.92 if emotion_name == "zen" else 0.75
        if emotion_name in ["analitico", "foco", "caotico", "alerta"]:
            prob_noise = 0.65 

        cor_brilho = (255, 255, 255)

        for r, c in indices:
            dist = self.dist_map[r, c]
            thr = threshold_map[r, c]
            
            if dist > thr - 1.2: 
                col = cor_base
            elif dist < 3.5: 
                col = cor_brilho if random.random() > 0.4 else cor_base
            else: 
                if random.random() > prob_noise:
                    col = tuple(int(ch * 0.5) for ch in cor_base)
                else:
                    continue                
            surf.set_at((c, r), col)

        scaled = pygame.transform.scale(surf, (int(self.size * pix), int(self.size * pix)))
        screen.blit(scaled, pos)