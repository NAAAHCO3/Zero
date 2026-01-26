import pygame
from config import ESPECIES

class EmotionSystem:
    def __init__(self):
        # Agora o objeto conhece o dicionário de DNA desde o nascimento
        self.especies = ESPECIES 
        self.current_state = "neutro"
        self.sync_level = 50
        self.last_update = pygame.time.get_ticks()
        
    def update_from_llm(self, tag):
        """Força a troca de estado e reseta o contador de inércia emocional"""
        if tag in self.especies:
            self.current_state = tag
            # Incrementa sincronia por interação bem-sucedida
            self.sync_level = min(100, self.sync_level + 1)
            self.last_update = pygame.time.get_ticks() 
            print(f"[SISTEMA] DNA alterado para: {tag}")

    def update_from_hardware(self, cpu_stable):
    # O Hardware só SOBRESCREVE se for uma situação crítica
	    if cpu_stable > 90:
	        self.current_state = "caotico"
	    elif cpu_stable > 75:
	        self.current_state = "alerta"

    def get_current_dna(self):
        """Entrega os parâmetros visuais para a engine.py"""
        return self.especies[self.current_state]

    def idle_check(self):
        """Verifica se o Anthony sumiu e entra em modo de repouso"""
        now = pygame.time.get_ticks()
        # Se passar 3 minutos (180.000 ms) sem interação
        if now - self.last_update > 180000: 
            if self.current_state != "dormindo":
                self.current_state = "dormindo"