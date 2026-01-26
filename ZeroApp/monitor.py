import psutil
from config import HIST_SIZE

class HardwareMonitor:
    def __init__(self):
        self.cpu_history = []
        self.ram_history = []
        self.hist_size = HIST_SIZE

    def get_stats(self):
        """
        Lê a CPU e RAM e calcula a média móvel para estabilização.
        Retorna: (cpu_media, ram_media)
        """
        # Coleta os dados brutos
        cpu_raw = psutil.cpu_percent()
        ram_raw = psutil.virtual_memory().percent
        
        # Adiciona ao histórico
        self.cpu_history.append(cpu_raw)
        self.ram_history.append(ram_raw)
        
        # Mantém o tamanho do histórico controlado (definido no config.py)
        if len(self.cpu_history) > self.hist_size:
            self.cpu_history.pop(0)
        if len(self.ram_history) > self.hist_size:
            self.ram_history.pop(0)
            
        # Calcula a média
        cpu_stable = sum(self.cpu_history) / len(self.cpu_history)
        ram_stable = sum(self.ram_history) / len(self.ram_history)
        
        return cpu_stable, ram_stable

    def get_process_count(self):
        """Opcional: Retorna o número de processos rodando (útil para humor caótico)"""
        return len(psutil.pids())