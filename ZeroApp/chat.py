import pygame
import json
import os
import re
from datetime import datetime
from config import CHAT_RECT, TEXT_USER, TEXT_ZERO, TEXT_SYSTEM, MEMORY_FILE, ESPECIES, COMANDOS

class ChatSystem:
    def __init__(self, font):
        self.font = font
        self.history = []
        self.input_text = ""
        self.scroll_y = 0 
        self.context_memory = self.load_memory()
        
        now = datetime.now().strftime("%H:%M")
        self.history.append(f"--- SESSÃO INICIADA: {now} ---")

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

    def save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.context_memory[-20:], f, indent=4)

    def show_help(self):
        """Exibe a lista de comandos formatada no chat"""
        self.history.append("--- COMANDOS DE ADMINISTRADOR ---")
        for cmd, desc in COMANDOS.items():
            # Alinha o comando à esquerda para estética de terminal
            formatted_cmd = cmd.ljust(10)
            self.history.append(f"{formatted_cmd} : {desc}")
        self.history.append("---------------------------------")
        self.scroll_to_bottom()

    def process_and_add(self, text, sender, emotion_system=None):
        # --- SISTEMA DE COMANDOS ---
        clean_text = text.strip().lower()
        
        if sender == "User":
            if clean_text == "/reset":
                self.context_memory = []
                self.history.append("--- [SISTEMA] MEMORIA RESETADA ---")
                self.save_memory()
                if emotion_system: emotion_system.current_state = "neutro"
                return
            
            if clean_text == "/help":
                self.show_help()
                return

        role = "assistant" if sender == "Zero" else "user"
        prefix = "Zero: " if sender == "Zero" else "> "
        
        if sender == "Zero" and emotion_system:
            # 1. Busca por Tag Formal no início
            match = re.search(r'^\[(\w+)\]', text.lower())
            tag_encontrada = None
            
            if match:
                tag_encontrada = match.group(1)
                text = re.sub(r'^\[\w+\]\s*[-]*\s*', '', text)
            
            # 2. Plano B (Apenas se não for emergência de hardware)
            elif emotion_system.current_state not in ["alerta", "caotico"]:
                start_of_text = text.lower()[:40]
                for possivel_tag in ESPECIES.keys():
                    if possivel_tag in start_of_text:
                        tag_encontrada = possivel_tag
                        break
                text = re.sub(r'\[.*?\]\s*', '', text)
            
            if tag_encontrada and tag_encontrada in ESPECIES:
                emotion_system.update_from_llm(tag_encontrada)

        if sender != "System":
            # Adiciona apenas se não for log de sistema
            if not text.startswith("---"):
                self.context_memory.append({'role': role, 'content': text.strip()})
                self.save_memory()

        # Quebra de linha inteligente para o Pygame
        words = text.split(' ')
        line = prefix
        for word in words:
            if self.font.size(line + word)[0] < (CHAT_RECT.width - 40):
                line += word + " "
            else:
                self.history.append(line)
                line = "      " + word + " "
        self.history.append(line)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        total_h = len(self.history) * 20
        if total_h > CHAT_RECT.height - 30:
            self.scroll_y = CHAT_RECT.height - 30 - total_h

    def draw(self, screen):
        # Fundo e bordas do Chat
        pygame.draw.rect(screen, (5, 5, 12), CHAT_RECT)
        pygame.draw.rect(screen, (40, 40, 70), CHAT_RECT, 2)
        
        surf = pygame.Surface((CHAT_RECT.width-4, CHAT_RECT.height-4))
        surf.fill((5, 5, 12))
        
        for i, line in enumerate(self.history):
            # Lógica de Cores: Usuário (Verde), Zero (Cinza), Sistema (Roxo/Azul)
            color = TEXT_USER if "> " in line[:3] else TEXT_ZERO
            if "---" in line or "[" in line[:1]: 
                color = TEXT_SYSTEM
            
            surf.blit(self.font.render(line, True, color), (15, 15 + i*20 + self.scroll_y))
        
        screen.blit(surf, (CHAT_RECT.x + 2, CHAT_RECT.y + 2))
        
        # Cursor piscante no Input
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        inp = self.input_text
        if self.font.size("> " + inp)[0] > (CHAT_RECT.width - 40): 
            inp = "..." + inp[-40:]
        
        screen.blit(self.font.render("> " + inp + cursor, True, TEXT_USER), (CHAT_RECT.x + 15, CHAT_RECT.bottom + 15))