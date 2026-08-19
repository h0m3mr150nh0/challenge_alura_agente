🤖 NOC Troubleshooting Agent (Gleen) - Base RAG Otimizada
O NOC Troubleshooting Agent (Gleen) é um assistente virtual baseado em RAG (Retrieval-Augmented Generation) projetado para auxiliar analistas de rede e operações de NOC no diagnóstico rápido e assertivo de problemas em infraestruturas TCP/IP e roteamento Cisco IOS.

📐 Arquitetura da Solução
A arquitetura do agente foi projetada com foco em alta precisão de busca (Retrieval) e baixa latência de resposta, utilizando táticas de engenharia de contexto para evitar alucinações.

[ Usuário / Chat Interface ]
             │
             ▼
      [ API Gateway / Agent ]
             │
             ├──► (1) Consulta Semântica com FAQ Anchors
             │
             ▼
     [ Vector Database ] ──(Embeddings)──► [ Documentos MD/PDF Chunked ]
             │
             ▼ (Retorna Top-K Chunks Relevantes)
             │
      [ LLM (RAG Engine) ]
             │
             ▼
 [ Resposta Estruturada com Sintaxe + Exemplos ]
Componentes Principais:
Base de Conhecimento Estruturada: Documentos técnicos em Markdown/PDF processados com hierarquia estrita e âncoras semânticas de FAQ para elevar a similaridade vetorial.

Embeddings & Vector Store: Indexação vetorial para busca por proximidade em linguagem natural e termos operacionais de rede.

Engine de Inferência: Prompts estritos que restringem o escopo da LLM apenas aos documentos ingeridos, garantindo respostas fundamentadas e com citação de fontes.

🛠️ Tecnologias Utilizadas
Linguagem: Python 3.10+

Orquestração RAG: LangChain / LlamaIndex

Vector Store: ChromaDB / FAISS / Qdrant

Modelos LLM/Embeddings: OpenAI / Google Gemini / HuggingFace

Interface / API: FastAPI / Streamlit / Gradio

🚀 Como Executar o Projeto
Pré-requisitos
Python 3.10 ou superior

Git instalado

Chave de API configurada (.env)

1. Clonar o Repositório
Bash
git clone https://github.com/seu-usuario/noc-troubleshooting-agent.git
cd noc-troubleshooting-agent
2. Configurar o Ambiente Virtual
Bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.venv\Scripts\activate
3. Instalar as Dependências
Bash
pip install -r requirements.txt
4. Configurar Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto contendo:

Snippet di codice
OPENAI_API_KEY="sua-chave-aqui"
# Ou GEMINI_API_KEY="sua-chave-aqui"
VECTOR_DB_PATH="./data/vectorstore"
5. Ingestão dos Documentos na Base Vetorial
Bash
python ingest.py
6. Iniciar a Aplicação
Bash
python main.py
💡 Guia de Uso
O agente aceita tanto perguntas diretas de comandos quanto dúvidas operacionais e conceituais de suporte a redes.

Exemplos de Perguntas Suportadas:
Sintaxe e Execução: "como faço um teste de ping?", "qual a sintaxe do comando traceroute no Windows?"

Testes de Aplicação: "como testar se a porta 80 do servidor está aberta via telnet?"

Troubleshooting Cisco: "como ver o uso de CPU no roteador Cisco?", "como fazer debug de pacotes IP com segurança?"

Diagnóstico de Protocolo: "como identificar conflito de IP através da tabela ARP?"

📸 Evidências do Projeto
1. Resolução de Sintaxe e Exemplos Diretos
Diferente de consultas genéricas, a inclusão de âncoras semânticas garante respostas operacionais imediatas (com sintaxe e exemplos de código para Cisco IOS, Windows e Linux):

2. Restrição de Escopo e Segurança
O agente identifica quando a pergunta está fora da base de conhecimento ou fora do escopo de atendimento NOC, evitando alucinações de respostas não fundamentadas:

📄 Licença
Este projeto está sob a licença MIT. Para mais detalhes, consulte o arquivo LICENSE.