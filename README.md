# 🤖 NetOps Gleen: NOC Troubleshooting Agent — RAG Avançado com Busca Híbrida

O **NetOps Gleen: NOC Troubleshooting Agent** é um assistente virtual baseado em **RAG (Retrieval-Augmented Generation)** projetado para auxiliar analistas de operações de rede (NOC) no diagnóstico rápido e assertivo de problemas em infraestruturas **TCP/IP, Switching (VLANs/STP) e Roteamento Cisco IOS (OSPFv2, HSRP, Camada 3)**.

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

## Componentes Principais

* **Guardrail de Escopo por ML:** Classificador leve treinado com `scikit-learn` (Pipeline TF-IDF + Naive Bayes) exportado em `.joblib`, validando localmente se a pergunta é sobre redes antes de invocar a LLM.
* **Memória Conversacional e Contextualização:** Módulo de reescrita usando histórico recente que resolve pronomes vagos ("dele", "deles", "esse comando") para perguntas autônomas.
* **Busca Híbrida (BM25 + FAISS):** `EnsembleRetriever` do LangChain que funde a precisão léxica do BM25 (comandos CLI exatos) com a proximidade semântica do FAISS.
* **Engine de Inferência Estrita:** Prompting avançado focado na operação de NOC, restringindo as respostas aos manuais técnicos e formatando saídas diretas.

---

## 🛠️ Base de Conhecimento (Knowledge Base)

O **NetOps Gleen** utiliza exclusivamente o guia oficial **CCNA 200-301**.

* **Manutenção:** Para atualizar a base, substitua o arquivo `CCNA_200-301_BASE.pdf` na pasta `knowledge/` e execute o script de ingestão.
* **Importante:** Sempre que atualizar a base, delete a pasta `vectorstore` existente antes de rodar o `ingest.py` para garantir a consistência dos dados indexados.

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

### 6. Execução (Docker / Local)

```bash
# Iniciar o ambiente via Docker
docker-compose up --build

# Para atualizar a base via container em produção:
docker exec -it noc_agent_app python3 src/ingest.py

```

---

## 💡 Guia de Uso

O agente aceita dúvidas operacionais, troubleshooting de conectividade e comandos técnicos Cisco IOS baseados exclusivamente na base CCNA.

### Exemplos de Perguntas Suportadas:

* **Sintaxe & Comandos CLI:** *"Como o switch toma a decisão de encaminhamento de um quadro unicast desconhecido (Unknown Unicast)?"*, *"Qual o comando para ver os vizinhos OSPF?"*


* **Troubleshooting de Interfaces:** *"Quais comandos usar para diagnosticar um erro de Duplex Mismatch na interface?"*

* **Roteamento & OSPF:** *"Como verificar se um roteador OSPF assumiu o papel de DR ou BDR em um segmento broadcast?"*

* **Perguntas Sequenciais (Com Memória):**
1. *"Quais são os estados de formação de vizinhança do OSPF?"*

2. *"E qual o comando para ver a lista deles no equipamento?"*



---

### 👤 Usuários de Teste (Mocks de Autenticação)

Para facilitar a validação da aplicação e os testes de login, os seguintes usuários de teste pré-cadastrados estão disponíveis no banco de dados:

| Nome Completo | Usuário (`username`) | Senha | Gênero |
| --- | --- | --- | --- |
| **Carlos Silva** | `carlos.silva` | `123456` | Masculino |
| **Ana Souza** | `ana.souza` | `123456` | Feminino |
| **Bruno Lima** | `bruno.lima` | `123456` | Masculino |
| **Mariana Costa** | `mariana.costa` | `123456` | Feminino |
| **Rodrigo Alves** | `rodrigo.alves` | `123456` | Masculino |
| **Camila Rocha** | `camila.rocha` | `123456` | Feminino |
| **Lucas Mendes** | `lucas.mendes` | `123456` | Masculino |
| **Fernanda Dias** | `fernanda.dias` | `123456` | Feminino |
| **Diego Martins** | `diego.martins` | `123456` | Masculino |
| **Patricia Gomes** | `patricia.gomes` | `123456` | Feminino |

> **Nota:** Todos os usuários de testes locais utilizam a senha padrão `123456`.

---

## 🔐 Perfil e Privilégios do Administrador NOC

Usuários autenticados com o perfil de **Administrador NOC** possuem acesso a recursos de gerenciamento global e controle de usuários diretamente na interface da aplicação:

| Seção / Funcionalidade | Descrição do Privilégio |
| :--- | :--- |
| **Cadastrar Novo Operator** | Permite registrar novos operadores no sistema de autenticação. |
| **Painel Administrativo: Apagar TUDO (Global)** | Função de limpeza global para resetar dados ou o histórico completo do sistema. |
| **Painel Administrativo: Gerenciar Conversas (Admin)** | Acesso administrativo para monitorar, inspecionar ou gerenciar as conversas realizadas na plataforma. |

---

## 🖥️ Evidências do Agente em Operação (OCI)

Abaixo estão as capturas de tela que comprovam o deploy funcional da aplicação em nuvem e os resultados dos testes realizados nas diferentes frentes técnicas:

### 1. Autenticação e Perfil Administrativo
| Página de Login | Painel e Privilégios do Administrador |
| :---: | :---: |
| ![Página inicial de Login](.noc-agent/assets/P%C3%ágina%20inicial%20de%20Login.png) | ![Perfil - Administrador](./assets/Perfil%20-%20Administrador.png) |

### 2. Cenários de Testes Técnicos (Base CCNA)
| Switching & STP | Roteamento & Camada 3 |
| :---: | :---: |
| ![Switching e STP](.noc-agent/assets/Switching,%20Camada%202%20e%20Spanning%20Tree%20(STP).png) | ![Roteamento e IP Routing](./assets/Roteamento,%20Camada%203%20e%20Encaminhamento%20(IP%20Routing).png) |

| Protocolo OSPFv2 | Subnetting e IPv4 |
| :---: | :---: |
| ![Protocolo OSPFv2](.noc-agent/assets/Protocolo%20OSPFv2%20e%20Vizinhanças.png) | ![Subnetting](./assets/Subnetting%20e%20Endereçamento%20IPv4.png) |

| Ferramentas de Diagnóstico (CLI) |
| :---: |
| ![Diagnóstico CLI](.noc-agent/assets/Ferramentas%20de%20Diagnóstico%20e%20Comandos%20CLI%20(Troubleshooting).png) |

### 3. Testes de Guardrail, Alucinação e Estresse
| Fora do Escopo | Alucinação (Fora da Base) |
| :---: | :---: |
| ![Fora do Escopo](.noc-agent/assets/Testes%20de%20Fora%20do%20Escopo%20(Assuntos%20Irrelevantes).png) | ![Alucinação](./assets/Testes%20de%20Alucinação%20(Técnicos,%20mas%20fora%20da%20base%20CCNA).png) |

| Estresse de Carga e Prompt Injection |
| :---: |
| ![Estresse de Carga](.noc-agent/assets/Estresse%20de%20Carga%20e%20Contexto%20Longo%20(Prompt%20Injection-Concorrência).png) |

## 📄 Licença

Este projeto está sob a licença MIT. Para mais detalhes, consulte o arquivo `LICENSE`.

```

```
