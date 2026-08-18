import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# Caminho onde o modelo treinado será salvo
MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_escopo.joblib")

# Dataset de treino: (Texto, Classe) -> 1: Dentro do Escopo NOC | 0: Fora do Escopo
dados_treino = [
    # 🟢 DENTRO DO ESCOPO (NOC / OSPF / TCP-IP / HSRP / Diagnóstico)
    ("o que e ospf?", 1),
    ("como ver a tabela de roteamento?", 1),
    ("não consigo acessar o servidor", 1),
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
]

def treinar_e_salvar_modelo():
    X, y = zip(*dados_treino)
    
    # Criando o Pipeline: Vetorização TF-IDF + Classificador Naive Bayes
    modelo = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), lowercase=True),
        MultinomialNB(alpha=0.1)
    )
    
    # Treinamento
    modelo.fit(X, y)
    
    # Salvando em arquivo binário
    joblib.dump(modelo, MODEL_PATH)
    print(f"✅ Modelo de Machine Learning treinado e salvo com sucesso em: {MODEL_PATH}")

if __name__ == "__main__":
    treinar_e_salvar_modelo()