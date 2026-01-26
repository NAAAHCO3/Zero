import pyttsx3
import threading

class VoiceSystem:
    def __init__(self):
        # Inicializa o motor de voz do sistema operacional
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)    # Velocidade da fala
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 a 1.0)
        
        # A flag de voz deve estar alinhada exatamente com o restante do bloco
        self.is_speaking = False 
        
        # Tenta selecionar uma voz em Portugues se disponivel
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def _speak_worker(self, text):
        """Worker para rodar em thread separada e nao travar o Pygame"""
        try:
            self.is_speaking = True # Comecou a falar
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Erro no audio: {e}")
        finally:
            self.is_speaking = False # Terminou de falar

    def speak(self, text):
        """Dispara a fala em uma nova thread"""
        thread = threading.Thread(target=self._speak_worker, args=(text,))
        thread.daemon = True
        thread.start()