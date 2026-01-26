import pygame
import threading
import random
from config import *
from engine import ZeroEngine
from emotions import EmotionSystem
from chat import ChatSystem
from monitor import HardwareMonitor
from llm_client import LLMClient
from voice_system import VoiceSystem 

def main():
    # 1. INICIALIZAÇÃO CORE
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PROJECT ZERO v4.5 - Responsive Voice")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("lucidaconsole", 14)

    # 2. INSTÂNCIA DOS MÓDULOS
    engine = ZeroEngine()
    emotions = EmotionSystem()
    monitor = HardwareMonitor()
    chat = ChatSystem(font)
    llm = LLMClient(model_name='llama3') 
    voice = VoiceSystem() 

    # Variáveis de Controle
    modo_atual = "normal"
    modo_widget = False
    is_thinking = False
    deve_falar_resposta = False 
    frame = 0

    # --- SEQUÊNCIA DE BOOT ---
    boot_logs = [
        "--- INICIALIZANDO PROJECT ZERO v4.5 ---",
        "[OK] NUCLEO DE CONSCIENCIA: ESTAVEL",
        "[OK] SISTEMA DE VOZ: RESPONSIVO",
        "--- SISTEMA PRONTO PARA OPERACAO ---"
    ]
    
    for log in boot_logs:
        screen.fill(BG_COLOR)
        chat.history.append(log)
        chat.draw(screen)
        pygame.display.flip()
        pygame.time.wait(350)

    chat.show_help()

    # 3. LOOP PRINCIPAL
    while True:
        perfil = MODOS_SISTEMA[modo_atual]
        actual_w = screen.get_width()
        
        if modo_widget and actual_w != WIDGET_SIZE[0]:
            screen = pygame.display.set_mode(WIDGET_SIZE)
        elif not modo_widget and actual_w != WIDTH:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))

        screen.fill(BG_COLOR)

        # --- LÓGICA SENSORIAL E RESPOSTA ---
        cpu_stable, ram_stable = monitor.get_stats()
        
        response = llm.get_response()
        if response:
            chat.process_and_add(response, "Zero", emotion_system=emotions)
            if deve_falar_resposta:
                voice.speak(response)
                deve_falar_resposta = False
            is_thinking = False

        emotions.update_from_hardware(cpu_stable)
        emotions.idle_check() 

        # --- RENDERIZAÇÃO ---
        target_dna = emotions.get_current_dna()
        engine.update(target_dna)
        
        base_x = ZERO_POS_NORMAL[0] + perfil["offset"][0]
        base_y = ZERO_POS_NORMAL[1] + perfil["offset"][1]
        
        # Tremores extras em estados críticos
        if emotions.current_state in ["caotico", "alerta", "nervoso"]:
            base_x += random.randint(-3, 3)
            base_y += random.randint(-3, 3)

        if not modo_widget:
            # INTERFACE COMPLETA (Agora com is_speaking sincronizado)
            engine.draw(screen, frame, 
                        emotion_name=emotions.current_state, 
                        pos=(base_x, base_y), 
                        scale_mult=perfil["escala"],
                        is_speaking=voice.is_speaking) # <--- Sincronia de voz
            
            chat.draw(screen)
            
            # Gráficos de Status
            y_bench = 380
            cor_atual = engine.current_dna["cor"]
            for label, val in {"CPU": cpu_stable, "RAM": ram_stable}.items():
                pygame.draw.rect(screen, (20, 20, 40), (610, y_bench, 160, 12)) 
                pygame.draw.rect(screen, cor_atual, (610, y_bench, int(1.6 * val), 12)) 
                screen.blit(font.render(f"{label}: {val:.1f}%", True, (200, 200, 200)), (610, y_bench - 18))
                y_bench += 45

            tag_text = f"ESTADO: [{emotions.current_state.upper()}]"
            screen.blit(font.render(f"SYNC LEVEL: {emotions.sync_level}%", True, (255, 255, 255)), (610, y_bench))
            screen.blit(font.render(tag_text, True, cor_atual), (610, y_bench + 20))
            screen.blit(font.render(f"MODO: {modo_atual.upper()}", True, TEXT_SYSTEM), (610, y_bench + 40))
			
            if is_thinking:
                pygame.draw.circle(screen, cor_atual, (45, HEIGHT - 22), 3)
                screen.blit(font.render("SINCRONIZANDO...", True, cor_atual), (60, HEIGHT - 30))
        else:
            # MODO WIDGET (Também responsivo à voz)
            w_x, w_y = WIDGET_SIZE[0]//2 - 128, WIDGET_SIZE[1]//2 - 128
            engine.draw(screen, frame, emotion_name=emotions.current_state, 
                        pos=(w_x, w_y), scale_mult=0.8, is_speaking=voice.is_speaking)

        # --- ENTRADA DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    modo_widget = not modo_widget
                
                if not modo_widget and not is_thinking:
                    if event.key == pygame.K_RETURN:
                        msg = chat.input_text.strip().lower()
                        if msg:
                            chat.input_text = ""
                            
                            if msg.startswith("/call "):
                                pergunta = msg.replace("/call ", "")
                                chat.process_and_add(f"(VOZ) {pergunta}", "User")
                                deve_falar_resposta = True
                                is_thinking = True
                                llm.ask(pergunta, chat.context_memory, emotions.current_state)
                            
                            elif msg.startswith("/"):
                                if msg in ["/estudo", "/jogo", "/normal"]:
                                    modo_atual = msg.replace("/", "")
                                    aviso = f"Protocolo {modo_atual} ativado."
                                    chat.history.append(f"--- [SISTEMA] {aviso.upper()} ---")
                                    voice.speak(aviso) 
                                    emotions.update_from_llm(MODOS_SISTEMA[modo_atual]["dna"])
                                else:
                                    chat.process_and_add(msg, "User", emotion_system=emotions)
                            else:
                                chat.process_and_add(msg, "User")
                                is_thinking = True
                                llm.ask(msg, chat.context_memory, emotions.current_state)
                                
                    elif event.key == pygame.K_BACKSPACE:
                        chat.input_text = chat.input_text[:-1]
                    else:
                        if event.unicode.isprintable():
                            chat.input_text += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN and not modo_widget:
                if event.button == 4: chat.scroll_y = min(0, chat.scroll_y + 30)
                if event.button == 5: chat.scroll_y -= 30

        pygame.display.flip()
        frame += 1
        clock.tick(perfil["fps"])

if __name__ == "__main__":
    main()