"""
Script de diagnóstico: verifica se a seção de sintaxe/exemplos de comandos
(ex: "traceroute <IP>", "tracert <IP>") realmente está indexada no
vectorstore atual, e o que o retrieval está trazendo para diferentes
perguntas.

Rode este script no MESMO ambiente onde está a pasta vectorstore/ e as
dependências (langchain, huggingface, etc). Ele NÃO chama a API do Gemini,
então não consome créditos.
"""

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings()
vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True,
)

# 1️⃣ Quantos chunks existem no total no índice?
total_chunks = vectorstore.index.ntotal
print(f"\n📦 Total de chunks indexados: {total_chunks}\n")

# 2️⃣ Busca direta pelo texto que sabemos que existe no PDF (seção 8.1)
#    Se isso não aparecer em NENHUM resultado, a seção não foi indexada
#    (ou foi indexada de forma fragmentada/corrompida).
queries_teste = [
    "sintaxe do comando traceroute",
    "traceroute <endereço_IP_ou_hostname>",
    "exemplo de uso traceroute 10.0.0.1",
    "guia rápido de comandos",
]

for q in queries_teste:
    print(f"🔎 Query: {q!r}")
    docs = vectorstore.similarity_search_with_score(q, k=5)
    for i, (doc, score) in enumerate(docs, 1):
        contem_sintaxe = "Sintaxe" in doc.page_content or "traceroute <" in doc.page_content.lower()
        marcador = "✅ TEM SINTAXE" if contem_sintaxe else ""
        print(f"  [{i}] score={score:.4f} {marcador}")
        print(f"      {doc.page_content[:200]!r}")
    print()

# 3️⃣ Varre TODOS os chunks do índice procurando literalmente por "traceroute <"
#    (não depende de embedding/similaridade, é busca de texto bruta)
print("🔍 Varredura bruta em todos os chunks por 'traceroute <' ou 'Sintaxe':")
encontrou = False
for doc_id, doc in vectorstore.docstore._dict.items():
    if "traceroute <" in doc.page_content.lower() or "sintaxe" in doc.page_content.lower():
        encontrou = True
        print(f"  ✅ Encontrado no chunk {doc_id}:")
        print(f"     {doc.page_content[:300]!r}\n")

if not encontrou:
    print("  ❌ NENHUM chunk no índice contém 'traceroute <' ou 'Sintaxe'.")
    print("  ➡️  Isso confirma que o vectorstore está DESATUALIZADO em relação")
    print("      ao PDF atual e precisa ser regenerado (rodar o script de")
    print("      ingestão de novo com o PDF mais recente).")
