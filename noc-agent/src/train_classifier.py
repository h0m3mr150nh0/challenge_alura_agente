import os
import joblib
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_escopo.joblib")

# Função auxiliar para remover acentos e padronizar o texto
def normalizar_texto(texto):
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# Dataset expandido para maior robustez no NOC e cobertura completa do CCNA
dados_treino = [
    # 🟢 DENTRO DO ESCOPO (NOC / OSPF / TCP-IP / HSRP / Switching / STP / Subnetting / Diagnóstico)
    ("o que e ospf?", 1),
    ("como ver a tabela de roteamento?", 1),
    ("nao consigo acessar o servidor", 1),
    ("ping respondendo mas sem web", 1),
    ("qual o comando para ver os vizinhos do ospf?", 1),
    ("problema de conectividade ip na interface", 1),
    ("como configurar hsrp no roteador?", 1),
    ("como testar a porta 80 via telnet?", 1),
    ("o servidor fica em outra rede", 1),
    ("pingo no roteador mas nao navega", 1),
    ("nao consigo acessar meu email", 1),
    ("como ver o estado do vizinho?", 1),
    ("pacotes caindo na interface serial", 1),
    ("erro de dns ao resolver dominio", 1),
    ("como limpar os contadores de erro da interface?", 1),
    ("o que e protocolo ip e mascara de subrede?", 1),
    ("como ver a memoria cpu do equipamento?", 1),
    ("mostrar rotas aprendidas pelo bgp e ospf", 1),
    ("falha de adjacencia no roteador cisco", 1),
    ("como usar o traceroute para rastrear a rota?", 1),
    ("porta do switch caiu", 1),
    ("interface serial com erro de crc", 1),
    ("latencia alta na conexao", 1),
    ("como configurar rota estatica", 1),
    ("problema de mtu no enlace", 1),
    ("o traceroute esta dando timeout", 1),
    ("como ver as estatisticas da interface", 1),
    
    # Adições essenciais: Switching, STP, Root Bridge e Subnetting (CCNA 200-301)
    ("como o algoritmo do spanning tree elege o root bridge de uma rede?", 1),
    ("root bridge", 1),
    ("spanning tree protocol", 1),
    ("como o switch toma a decisão de encaminhamento de um quadro unicast desconhecido", 1),
    ("unknown unicast", 1),
    ("qual o comando para ver a tabela mac do switch", 1),
    ("como configurar portas de acesso e troncos vlan", 1),
    ("o que e encapsulamento 802.1q", 1),
    ("como diagnosticar erro de duplex mismatch na interface", 1),
    ("quais contadores de erro indicam colisões tardias", 1),
    ("como calcular o subnet id e o broadcast de um ip", 1),
    ("qual a formula para calcular o numero de hosts usaveis", 1),
    ("como funcionam as rotas estáticas e o default gateway", 1),
    ("quais os estados de vizinhança do ospf", 1),
    ("como configurar o roteamento inter-vlan com router-on-a-stick", 1),

    # 🔴 FORA DO ESCOPO (Geral / Outros assuntos)
    ("qual a receita de bolo de cenoura?", 0),
    ("quem ganhou o jogo de futebol ontem?", 0),
    ("qual a cotacao do dolar hoje?", 0),
    ("me conte uma piada engraçada", 0),
    ("qual a melhor loja para comprar celular?", 0),
    ("como esta o clima em salvador?", 0),
    ("recomende um filme de acao", 0),
    ("como fazer um curriculo profissional?", 0),
    ("quanto custa uma passagem de aviao?", 0),
    ("me ajude a resolver essa conta de matematica", 0),
    ("como instalar o windows 11 no pc?", 0),
    ("qual a capital da frança?", 0),
    ("qual a escalacao do flamengo", 0),
    ("me indique uma receita de lasanha", 0),
    ("qual a previsao do tempo para o fim de semana", 0),
    ("como trocar a pelicula do celular", 0),
    ("qual o melhor carro eletrico do mercado", 0),
]

def treinar_e_salvar_modelo():
    # Normaliza todos os textos de treino para evitar problemas com acentos
    X_raw, y = zip(*dados_treino)
    X = [normalizar_texto(texto) for texto in X_raw]
    
    # Pipeline com ngramas (1, 2) e MultinomialNB
    modelo = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2)),
        MultinomialNB(alpha=0.1)
    )
    
    modelo.fit(X, y)
    joblib.dump(modelo, MODEL_PATH)
    print(f"✅ Modelo de Machine Learning otimizado e salvo em: {MODEL_PATH}")

if __name__ == "__main__":
    treinar_e_salvar_modelo()