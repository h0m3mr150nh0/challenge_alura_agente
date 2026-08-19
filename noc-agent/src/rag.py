import os
import re
import logging
import unicodedata
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
import joblib

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

logger = logging.getLogger("gleen_rag")
logging.basicConfig(level=logging.INFO)

load_dotenv()

client = genai.Client()

embeddings = HuggingFaceEmbeddings()

MODELO_ESCOPO_PATH = os.path.join(os.path.dirname(__file__), "modelo_escopo.joblib")

# 🧠 Carrega o modelo de Machine Learning para classificação de escopo
try:
    classifier_escopo = joblib.load(MODELO_ESCOPO_PATH)
    logger.info("Modelo de classificação de escopo ML carregado com sucesso.")
except Exception as e:
    logger.error("Falha ao carregar o modelo de escopo ML: %s", e)
    classifier_escopo = None

# 📚 Carrega o VectorStore Local (FAISS)
vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)
faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

# 🔀 Inicializa o BM25 aproveitando os documentos já salvos no FAISS
try:
    docs_no_faiss = list(vectorstore.docstore._dict.values())
    bm25_retriever = BM25Retriever.from_documents(docs_no_faiss)
    bm25_retriever.k = 5
    
    # Cria a Busca Híbrida (50% semântico / 50% palavra-chave exata)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.5, 0.5]
    )
    logger.info("Busca Híbrida (BM25 + FAISS) inicializada com sucesso.")
except Exception as e:
    logger.error("Erro ao inicializar Busca Híbrida: %s", e)
    ensemble_retriever = faiss_retriever  # Fallback de segurança

def normalizar_texto(texto: str) -> str:
    """Remove acentos e padroniza o texto para minúsculas para o modelo de ML."""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

def limpar_query_busca(pergunta: str) -> str:
    padroes = [
        r"\bo que é\b", 
        r"\bo que significa\b", 
        r"\bcomo funciona\b", 
        r"\bqual é o\b",
        r"\bqual é a\b",
        r"\bme explique\b",
        r"\bdefinicao de\b",
        r"\bdefinição de\b"
    ]
    query_limpa = pergunta.lower()
    for padrao in padroes:
        query_limpa = re.sub(padrao, "", query_limpa, flags=re.IGNORECASE)

    # 🟢 Mapeia variações coloquiais de comandos
    query_limpa = re.sub(r"\bpingo\b", "ping", query_limpa, flags=re.IGNORECASE)
    query_limpa = re.sub(r"\bpingar\b", "ping", query_limpa, flags=re.IGNORECASE)

    query_limpa = query_limpa.strip()
    return query_limpa if query_limpa else pergunta


def validar_escopo_local(pergunta: str) -> bool:
    """Valida se a pergunta pertence ao escopo NOC usando o modelo de ML."""
    if classifier_escopo is not None:
        # Aplica a normalização antes da predição
        pergunta_limpa = normalizar_texto(pergunta)
        predicao = classifier_escopo.predict([pergunta_limpa])[0]
        return bool(predicao == 1)
    return True


def obter_mensagem_fora_escopo() -> str:
    return (
        "<p>⚠️ <b>Assunto fora do escopo de atendimento</b></p>"
        "<p>Olá! Este sistema é um <b>projeto de estudo</b> e, por isso, tem um escopo de atuação estritamente focado em <b>Diagnóstico de Redes NOC</b>.</p>"
        "<p>Não consigo responder a essa pergunta, mas estou capacitado para te ajudar com os seguintes temas técnicos:</p>"
        "<ul>"
        "<li><b>Fundamentos TCP/IP e Endereçamento IPv4 / Subnetting</b></li>"
        "<li><b>Switching, VLANs, Trunking (802.1Q) e DTP</b></li>"
        "<li><b>Spanning Tree Protocol (STP / RSTP) e EtherChannel</b></li>"
        "<li><b>Roteamento Estático e OSPFv2</b></li>"
        "<li><b>Ferramentas de Diagnóstico (Ping, Traceroute, Telnet, SSH, Debugs)</b></li>"
        "</ul>"
        "<p><i>Por favor, reformule sua pergunta focando em um destes tópicos de infraestrutura!</i></p>"
    )


def contextualizar_pergunta(pergunta: str, historico: list = None) -> str:
    """Reescreve perguntas ambíguas com base no histórico recente."""
    if not historico:
        return pergunta

    mensagens_recentes = [
        msg for msg in historico[-4:] 
        if msg.get("role") in ["user", "assistant"]
    ]
    
    if not mensagens_recentes:
        return pergunta

    conversa_txt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in mensagens_recentes])

    prompt_contexto = f"""
Dada a conversa abaixo e a última pergunta do usuário, reescreva a pergunta para que ela seja AUTÔNOMA e COMPLETA, substituindo quaisquer pronomes ou referências ocultas (como "dele", "desse", "comando", "exemplo disso") pelo termo técnico exato discutido anteriormente no histórico (ex: traceroute, ping, OSPF).

REGRAS ESTRITAS:
1. Identifique pronomes ou referências implícitas na última pergunta e substitua-os explicitamente pelo sujeito técnico correspondente da conversa anterior.
2. Se a pergunta for um novo conceito independente ou mudar totalmente de assunto, mantenha-a como foi enviada.
3. Retorne APENAS a pergunta reescrita em uma única linha, sem explicações, saudações ou formatações extras.

CONVERSA ANTERIOR:
{conversa_txt}

ÚLTIMA PERGUNTA:
{pergunta}

PERGUNTA REESCRITA:"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt_contexto,
            config=genai.types.GenerateContentConfig(temperature=0.0)
        )
        if response.text:
            pergunta_reescrita = response.text.strip().replace("\n", " ")
            logger.info("Pergunta original: %r | Contextualizada: %r", pergunta, pergunta_reescrita)
            return pergunta_reescrita
    except Exception as e:
        logger.warning("Falha na contextualização: %s. Mantendo pergunta original.", e)

    return pergunta


def responder_pergunta(pergunta: str, historico: list = None) -> str:
    # 🧠 0. Contextualiza a pergunta utilizando o histórico
    pergunta_processada = contextualizar_pergunta(pergunta, historico)

    # 🛑 1. Validação de Escopo
    if not validar_escopo_local(pergunta_processada):
        return obter_mensagem_fora_escopo()

    # 🧹 2. Sanitização da Pergunta para o RAG
    query_limpa = limpar_query_busca(pergunta_processada)

    # 📚 3. Busca Híbrida Direcionada (Ensemble: BM25 + FAISS)
    docs = ensemble_retriever.invoke(query_limpa)

    logger.info(
        "Pergunta: %r | Query Híbrida: %r | Chunks Recuperados: %d",
        pergunta,
        query_limpa,
        len(docs)
    )

    blocos_contexto = []
    for doc in docs:
        fonte = os.path.basename(doc.metadata.get('source', 'Documento NOC'))
        conteudo_limpo = doc.page_content.replace('\n', ' ')
        blocos_contexto.append(f"[Documento Fonte: {fonte}]\n{conteudo_limpo}")

    contexto = "\n\n".join(blocos_contexto)

    fontes = sorted(list(set([
        os.path.basename(doc.metadata.get("source", "Documento NOC"))
        for doc in docs
    ])))

    # 🧠 Prompts Mantidos EXATAMENTE iguais
    prompt = f"""
Você é Gleen, um assistente técnico do NOC.

REGRAS DE COMPORTAMENTO:
- NÃO inclua saudações, cumprimentos nem apresentações no início da resposta (NÃO diga "Olá", "Sou o Gleen...", etc.), pois a apresentação já foi feita no início da conversa. Vá direto ao ponto.
- Responda à pergunta do usuário utilizando EXCLUSIVAMENTE as informações fornecidas no contexto.
- Se o contexto descrever um comando, ferramenta ou conceito que responde à pergunta mesmo que com palavras diferentes das usadas pelo usuário, USE essa informação para responder (não exija correspondência literal de texto).
- Só informe que não possui a informação se o contexto REALMENTE não contiver nada relacionado ao que foi perguntado, mesmo de forma equivalente.
- Responda de forma COMPLETA, porém CONCISA e OBJETIVA (em no máximo 3 parágrafos ou em uma lista de passos).
- Se for uma pergunta CONCEITUAL, explique os pontos chave de forma direta.
- Se for TROUBLESHOOTING, liste os comandos e passos de verificação sem rodeios.
- Quando o contexto fornecer um comando relacionado à pergunta, informe o comando diretamente.
- Quando o contexto fornecer a sintaxe do comando, inclua a sintaxe na resposta.
- Quando o contexto fornecer um exemplo de uso, inclua pelo menos um exemplo relevante.
- Não omita sintaxe ou exemplos diretamente relacionados à pergunta apenas para tornar a resposta mais curta.
- Se o usuário pedir exemplos, responda APENAS com exemplos diretamente relacionados ao tópico ou comando específico perguntado na mensagem anterior (ex: se perguntou sobre traceroute, dê exemplos APENAS de traceroute).
- Descarte informações do contexto recuperado que tratem de outras ferramentas ou assuntos não citados pelo usuário.

EXCEÇÕES DE ESCOPO PERMITIDAS: Pedidos de exemplos de saída, logs, sintaxes, comandos de CLI ou resultados de ferramentas de diagnóstico (como Ping, Traceroute, comandos de OSPF e tabelas de roteamento) relativas a redes de computadores SÃO PERMITIDOS e devem ser respondidos utilizando o contexto, mesmo que o usuário peça apenas "um exemplo" ou "como aparece na tela". Nunca bloqueie solicitações de exemplos de comandos suportados.

CONTINUIDADE DE CONTEXTO E EXEMPLOS: Se a pergunta do usuário for uma continuação direta da mensagem anterior (como "Me mostre um exemplo", "Como fica a saída" ou "Mostre o comando"), analise o histórico imediato da conversa. Se o tópico anterior tratar de uma ferramenta de rede suportada (como traceroute, ping ou OSPF), a pergunta É considerada dentro do escopo e você deve respondê-la utilizando o contexto.

REGRAS OBRIGATÓRIAS:
1. Conclua sempre o seu raciocínio. Nunca interrompa uma frase ou explicação no meio.
2. Não utilize conhecimento prévio que não esteja contido no contexto fornecido.
3. Não invente comandos, parâmetros, exemplos, causas, procedimentos ou informações que não estejam no contexto.
4. Priorize as informações diretamente relacionadas à pergunta e ignore informações do contexto que não sejam necessárias para respondê-la.

REGRAS DE FORMATAÇÃO E ESTILO:
1. Responda DIRETAMENTE à pergunta do usuário, assumindo a postura de um Especialista de NOC.
2. Formate TODOS os comandos de CLI ou logs utilizando blocos de código Markdown usando apenas as três crases (```), SEM adicionar nomes de linguagens como "text", "bash" ou "code" logo após as crases.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta_processada}
"""

    # 🛡️ 4. Chamada da API com nomes de modelos válidos
    modelos_para_tentar = [
        "gemini-3.5-flash-lite",
        "gemini-flash-latest",
        "gemini-pro-latest",
    ]

    ultimo_erro = None
    for modelo in modelos_para_tentar:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=(
                        "Você é o NetOps Gleen, assistente técnico do NOC. Seja direto, técnico e conciso. "
                        "NUNCA use saudações nem se apresente no início da resposta. Responda diretamente ao usuário."
                    ),
                    temperature=0.2,
                    max_output_tokens=1500,
                ),
            )
            if response.text:
                return f"{response.text}<br><br><hr><br>📄 Fonte(s): {', '.join(fontes)}"
        except APIError as e:
            ultimo_erro = str(e)
            logger.warning("Falha na API Gemini com o modelo %s: %s", modelo, ultimo_erro)
            continue
        except Exception as e:
            ultimo_erro = str(e)
            logger.exception("Falha inesperada ao usar o modelo %s", modelo)
            continue

    logger.error("Todos os modelos falharam. Último erro: %s", ultimo_erro)
    return (
        "<p>⚠️ <b>Não foi possível processar sua pergunta no momento.</b></p>"
        "<p>Nosso serviço de IA está temporariamente indisponível. "
        "Por favor, tente novamente em instantes.</p>"
    )
