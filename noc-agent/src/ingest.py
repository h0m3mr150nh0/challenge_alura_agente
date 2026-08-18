import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

all_docs = []

for file in os.listdir("knowledge"):
    if file.endswith(".pdf"):
        path = os.path.join("knowledge", file)
        print(f"📄 Carregando: {file}")

        loader = PyPDFLoader(path)
        docs = loader.load()

        # adiciona metadata (IMPORTANTE)
        for doc in docs:
            doc.metadata["source"] = file

        all_docs.extend(docs)

print(f"\n📚 Total de páginas carregadas: {len(all_docs)}")

# dividir em chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=250,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_documents(all_docs)

print(f"✂️ Total de chunks: {len(chunks)}")

print("🔧 Criando embeddings...")

embeddings = HuggingFaceEmbeddings()

print("💾 Criando vectorstore...")

vectorstore = FAISS.from_documents(chunks, embeddings)

print("💾 Salvando vectorstore...")

vectorstore.save_local("vectorstore")

print("✅ Vectorstore criado com sucesso!")