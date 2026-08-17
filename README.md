```markdown
# 🤖 NOC Troubleshooting Agent (Gleen) — RAG Avançado com Busca Híbrida

O **NOC Troubleshooting Agent (Gleen)** é um assistente virtual baseado em **RAG (Retrieval-Augmented Generation)** projetado para auxiliar analistas de operações de rede (NOC) no diagnóstico rápido e assertivo de problemas em infraestruturas **TCP/IP e roteamento Cisco IOS (OSPF, HSRP, Camada 3)**.

---

## 📐 Arquitetura da Solução

O agente combina **Machine Learning Supervisionado** na camada de segurança com **Search & Retrieval Híbrido** e **LLMs de última geração**, garantindo zero custo adicional de tokens na etapa de busca e eliminação de alucinações.

```text
[ Usuário / Streamlit UI ]
           │
           ▼
[ Guardrail ML (scikit-learn / joblib) ]
           │
           ├──► (Fora do Escopo) ──► [ Mensagem Amigável de Bloqueio ]
           │
           ▼ (Dentro do Escopo)
[ Reescrita Conversacional de Contexto (Gemini Flash) ]
           │
           ▼
[ Ensemble Retriever (Busca Híbrida 50/50) ]
           ├──► BM25 Retriever (Match de termos exatos/CLI)
           └──► FAISS Vector Store (Embeddings HuggingFace - Semântica)
           │
           ▼ (Top-K Chunks Relevantes)
[ LLM Engine (Gemini 2.5 Flash / Flash Lite) ]
           │
           ▼
[ Resposta Técnica Concisa + Fontes Citadas ]

```

### Componentes Principais

* **Guardrail de Escopo por ML:** Classificador leve treinado com `scikit-learn` (Pipeline TF-IDF + Naive Bayes) exportado em `.joblib`, validando localmente se a pergunta é sobre redes antes de invocar a LLM.
* **Memória Conversacional e Contextualização:** Módulo de reescrita usando histórico recente que resolve pronomes vagos ("dele", "deles", "esse comando") para perguntas autônomas.
* **Busca Híbrida (BM25 + FAISS):** `EnsembleRetriever` do LangChain que funde a precisão léxica do BM25 (comandos CLI exatos) com a proximidade semântica do FAISS.
* **Engine de Inferência Estrita:** Prompting avançado focado na operação de NOC, restringindo as respostas aos manuais técnicos e formatando saídas diretas.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Interface:** Streamlit
* **Machine Learning / Guardrail:** `scikit-learn`, `joblib`
* **Orquestração RAG & Retrievers:** `langchain`, `langchain-community`, `langchain-text-splitters`, `langchain-classic`, `rank_bm25`
* **Vector Store & Embeddings:** FAISS (`faiss-cpu`), `sentence-transformers` (`all-MiniLM-L6-v2` via `HuggingFaceEmbeddings`)
* **LLM Engine:** Google Gemini SDK (`google-genai`) — `gemini-3.5-flash-lite` / `gemini-2.5-flash`

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

* Python 3.10 ou superior
* Git instalado
* Chave de API do Google Gemini (`GEMINI_API_KEY`)

### 1. Clonar o Repositório

```bash
git clone [https://github.com/seu-usuario/noc-troubleshooting-agent.git](https://github.com/seu-usuario/noc-troubleshooting-agent.git)
cd noc-troubleshooting-agent

```

### 2. Configurar o Ambiente Virtual

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

```

### 3. Instalar as Dependências

```bash
pip install -r requirements.txt

```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto contendo:

```env
GEMINI_API_KEY="sua-chave-api-gemini-aqui"

```

### 5. Treinar o Classificador de ML (Guardrail)

Execute o script para gerar o binário de Machine Learning local:

```bash
python src/train_classifier.py

```

### 6. Iniciar a Aplicação

```bash
streamlit run src/app.py

```

---

## 💡 Guia de Uso

O agente aceita dúvidas operacionais, troubleshooting de conectividade e comandos técnicos Cisco IOS/TCP-IP.

### Exemplos de Perguntas Suportadas:

* **Sintaxe & Comandos CLI:** *"Como vejo a tabela de rotas do roteador?"*, *"Qual o comando para ver os vizinhos OSPF?"*
* **Troubleshooting L3 / L7:** *"O ping responde mas não consigo acessar o serviço na porta 80. Como isolar?"*
* **Análise Física / Interface:** *"Meus pacotes estão caindo na interface serial, como checar os contadores de erro?"*
* **Perguntas Sequenciais (Com Memória):**
1. *"Quais são os estados de formação de vizinhança do OSPF?"*
2. *"E qual o comando para ver a lista deles no equipamento?"*



---

## 📄 Licença

Este projeto está sob a licença MIT. Para mais detalhes, consulte o arquivo `LICENSE`.

```

```
