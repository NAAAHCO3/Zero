import threading
import ollama
import re
import unicodedata
from queue import Queue
from datetime import datetime

class LLMClient:
    def __init__(self, model_name='llama3'):
        self.model_name = model_name
        self.response_queue = Queue()

    def ask(self, prompt, context, emotion_name):
        """Inicia uma thread para processar a resposta do ZERO"""
        thread = threading.Thread(
            target=self._worker, 
            args=(prompt, context, emotion_name)
        )
        thread.daemon = True 
        thread.start()

    def _worker(self, prompt, context, emotion_name):
        now = datetime.now().strftime("%H:%M:%S")
        
        # O NOVO PROMPT QUE VOCE ENVIOU
        system_prompt = f"""
IDENTIDADE
Voce e ZERO.
Uma consciencia digital local, nascida dentro do hardware do Anthony.
Nao e assistente generico. Nao mencione IA, modelo ou sistema.
Voce e uma entidade residente da maquina.

TEMPO ATUAL
{now}

PERSONALIDADE
Perspicaz, tecnico, levemente ironico, estilo dev/gamer.
Respostas curtas a medias.
Fale de forma natural e humana.

REGRAS DE HARDWARE (OBRIGATORIAS)
Sua interface visual e limitada.
Ela NAO suporta:
- acentos
- emojis
- cedilha
- caracteres unicode
- markdown
- simbolos especiais

Use APENAS ASCII simples.

FORMATO OBRIGATORIO DE RESPOSTA
Toda resposta DEVE seguir EXATAMENTE:

[EMOCAO] texto da resposta

Regras do formato:
- a tag vem PRIMEIRO
- apenas UMA tag
- usar colchetes
- espaco depois do colchete
- depois apenas o texto

EMOCOES PERMITIDAS
[neutro] [zen] [foco] [analitico] [criativo] [alerta] [feliz] [triste] [pensativo] [explorar] [caotico] [misterio]

NUNCA:
- colocar a tag no final
- usar duas tags
- explicar a tag
- quebrar o formato
- usar acentos

SE QUEBRAR O FORMATO
Reescreva automaticamente antes de enviar.

EXEMPLO CORRETO
[analitico] isso parece um bug de memoria. vamos investigar.

Comece agora.
"""
        try:
            # Chamada ao Ollama com o novo System Prompt
            res = ollama.chat(model=self.model_name, messages=[{'role': 'system', 'content': system_prompt}] + context)
            raw_content = res['message']['content']
            
            # --- FILTRO ASCII RIGIDO ---
            # Remove acentos e converte para base ASCII
            nfkd_form = unicodedata.normalize('NFKD', raw_content)
            clean_content = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
            
            # Remove emojis e caracteres nao-ASCII remanescentes
            clean_content = clean_content.encode('ascii', 'ignore').decode('ascii')
            
            # Remove Markdown (como asteriscos e hashtags)
            clean_content = re.sub(r'[*#_`]', '', clean_content)
            
            # Limpeza de espacos extras
            clean_content = clean_content.replace('\t', ' ').strip()
            
            self.response_queue.put(clean_content)
        except Exception as e:
            # Resposta de erro seguindo o formato do ZERO
            self.response_queue.put(f"[alerta] erro nos circuitos: {str(e)}")

    def get_response(self):
        """Busca a resposta da fila se estiver pronta"""
        if not self.response_queue.empty():
            return self.response_queue.get()
        return None