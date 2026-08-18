import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Ajuste o caminho da pasta onde o FAISS foi salvo
PASTA_VECTORSTORE = "vectorstore"  # Altere se a sua pasta tiver outro nome

# 2. Inicializa o modelo de embeddings (use a sua chave de API configurada no ambiente)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 3. Carrega e inspeciona o índice
if os.path.exists(PASTA_VECTORSTORE):
    vectorstore = FAISS.load_local(
        PASTA_VECTORSTORE, 
        embeddings, 
        allow_dangerous_deserialization=True
    )

    fontes = set()
    for doc in vectorstore.docstore._dict.values():
        if hasattr(doc, "metadata") and "source" in doc.metadata:
            fontes.add(doc.metadata["source"])

    print("\n📂 Fontes/PDFs carregados no FAISS:")
    for fonte in fontes:
        print(f" - {fonte}")
else:
    print(f"❌ A pasta '{PASTA_VECTORSTORE}' não foi encontrada.")