# import google.generativeai as genai
# import os

# api_key = os.getenv("GEMINI_API_KEY")

# print("API KEY:", api_key)  # DEBUG

# genai.configure(api_key=api_key)

# # 🔍 listar modelos disponíveis
# print("\nModelos disponíveis:")
# for m in genai.list_models():
    # print(m.name)

# # 🔥 usar modelo mais compatível possível
# model = genai.GenerativeModel("models/text-bison-001")

# try:
    # response = model.generate_content("Explain OSPF in simple terms")

    # print("\nResposta:")
    # print(response.text)

# except Exception as e:
    # print("\nERRO:")
    # print(e)
    
# import os
# from openai import OpenAI

# # Subtitua pela sua chave atual (ou garanta que esteja no .env)
# XAI_API_KEY = os.getenv("GROK_API_KEY") 

# client = OpenAI(
    # api_key=XAI_API_KEY,
    # base_url="https://api.x.ai/v1"
# )

# try:
    # print("🔎 Consultando modelos disponíveis para a sua API Key...\n")
    # models = client.models.list()
    
    # print("✅ Modelos encontrados:")
    # for model in models.data:
        # print(f" - {model.id}")

# except Exception as e:
    # print("❌ Erro ao listar modelos:")
    # print(e)
    
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

try:
    print("🚀 Testando conexão com a API do Gemini...\n")

    # Usando o modelo flash mais recente liberado para a sua conta
    chat = client.chats.create(model="gemini-1.5-flash")
    response = chat.send_message("Responda apenas: Conexão com o Gemini realizada com sucesso!")

    print("✅ Resposta do Gemini:")
    print(response.text)

except Exception as e:
    print("\n❌ Erro ao conectar:")
    print(e)

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

print("🚀 Verificando modelos disponíveis para a sua API Key...\n")

try:
    # 1. Lista todos os modelos ativos na sua conta
    modelos_disponiveis = []
    
    for m in client.models.list():
        # Filtra apenas modelos que suportam geração de texto (generateContent)
        metodos = getattr(m, "supported_generation_methods", [])
        if "generateContent" in metodos or not metodos:
            nome_limpo = m.name.replace("models/", "")
            modelos_disponiveis.append(nome_limpo)
            print(f"  • {nome_limpo}")

    print("\n--------------------------------------------------")
    
    if modelos_disponiveis:
        # 2. Testa a geração com o primeiro modelo da lista
        modelo_teste = modelos_disponiveis[0]
        print(f"🧪 Testando chamada real no modelo: '{modelo_teste}'...\n")
        
        response = client.models.generate_content(
            model=modelo_teste,
            contents="Responda apenas: Conexão efetuada com sucesso!"
        )
        print(f"✅ SUCESSO: {response.text.strip()}")
    else:
        print("⚠️ Nenhum modelo de texto foi retornado para esta chave.")

except Exception as e:
    print(f"❌ Erro ao listar/testar modelos: {e}")