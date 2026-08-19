import os
from google import genai

print("[INFO] Iniciando scanner de modelos...")
print("[INFO] Interrogando os servidores do Google AI Studio...")

try:
    client = genai.Client()
    modelos_disponiveis = client.models.list()
    
    print("\n[LISTA OFICIAL] A sua API Key tem acesso aos seguintes modelos:")
    contador = 0
    for modelo in modelos_disponiveis:
        # Filtra apenas os modelos que suportam geração de texto
        if 'generateContent' in modelo.supported_actions or not modelo.supported_actions:
            print(f" -> {modelo.name}")
            contador += 1
            
    if contador == 0:
        print("[ALERTA] A API respondeu, mas nenhum modelo de texto foi encontrado para esta chave.")
        
except Exception as e:
    print(f"\n[ERRO FATAL] Falha ao consultar a API: {e}")
