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
[ LLM Engine (gemini-3.5-flash-lite/gemini-flash-latest/gemini-pro-latest) ]
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

## 🛠️ Gerenciamento e Povoamento do Banco de Dados

Para facilitar os testes de integração e a homologação do sistema em diferentes ambientes, foi desenvolvido um script utilitário de gerenciamento de usuários. Este script automatiza a inicialização do banco de dados, o cadastro de contas de teste e a remoção de usuários de forma interativa.

### Funcionalidades da Ferramenta de Povoamento
A ferramenta (`seed_users.py`) oferece uma interface de linha de comando (CLI) intuitiva para operações administrativas:

*   **Povoamento Automático:** Cria a estrutura de tabelas, cadastra o perfil administrador (`admin`) e gera uma base de operadores para testes de carga e validação funcional.
*   **Gestão de Exclusão:** Lista todos os usuários cadastrados e permite a remoção seletiva, garantindo a limpeza do ambiente após os testes.
*   **Interface Interativa:** Menu centralizado que reduz o erro operacional na manipulação dos dados.

#### Execução da Ferramenta
Para executar o utilitário, utilize o comando:
```bash
python seed_users.py
```

![Interface de Gerenciamento de Usuários](./noc-agent/assets/Ferramenta_Povoar_DB.png)

---

## 💡 Guia de Uso

O agente aceita dúvidas operacionais, troubleshooting de conectividade e comandos técnicos Cisco IOS baseados exclusivamente na base CCNA.

---

## 💡 Exemplos de Perguntas e Respostas

Abaixo estão exemplos reais de interações com o agente, demonstrando a assertividade técnica com base no guia CCNA, a precisão em cálculos matemáticos de redes e a atuação do filtro de escopo (*Guardrail*):

### 1. Pergunta Técnica (Switching e STP)
* **Usuário:** *"Oi, o switch aqui da rede tá com um loop estranho. Como é que o spanning tree descobre qual é o root bridge da rede?"*
* **NetOps Gleen:** A topologia lógica sem loops do Spanning Tree Protocol começa com a eleição de um único switch central, o Root Bridge. 
  * **Início da Eleição:** Todos os switches ligam-se alegando serem o Root e enviam BPDUs com o seu próprio Bridge ID (BID).
  * **Critério de Vitória:** O switch com o menor Bridge ID (numericamente) vence a eleição. A comparação começa pela prioridade (padrão 32.768) e, em caso de empate, utiliza o menor endereço MAC.
  *(Fonte: `CCNA_200-301_BASE.pdf`)*

### 2. Pergunta Técnica (Protocolo OSPFv2)
* **Usuário:** *"Meu roteador principal perdeu o contato com o vizinho OSPF. Quais parâmetros exatos têm que coincidir para formar essa adjacência?"*
* **NetOps Gleen:** Para que dois roteadores OSPF se tornem vizinhos e troquem LSAs, os seguintes parâmetros nas mensagens Hello devem coincidir exatamente: mesma sub-rede, mesma área, timers compatíveis (Hello e Dead), Router IDs únicos, autenticação (se configurada) e valores de MTU compatíveis.
  *(Fonte: `CCNA_200-301_BASE.pdf`)*

### 3. Pergunta Técnica (Cálculo de Sub-rede / Subnetting)
* **Usuário:** *"Calcule a rede do endereço IP 172.16.32.86/25"*
* **NetOps Gleen:** Para calcular a sub-rede do endereço IP 172.16.32.86 com a máscara /25 (255.255.255.128), analise o quarto octeto, onde a máscara possui bits mistos.
  * O prefixo /25 indica que os primeiros 25 bits são de rede, deixando 7 bits para hosts. No quarto octeto, a representação binária da máscara 128 é 10000000, o que significa que o bloco de incremento (número mágico) é 128.
  * **Subnet ID:** Analisando o quarto octeto (86), o maior múltiplo do número mágico (128) menor ou igual a 86 é 0. Portanto, o Subnet ID é `172.16.32.0`.
  * **Broadcast:** O endereço de broadcast calculado para esta sub-rede é `172.16.32.127`.
  * **Hosts Usáveis:** O intervalo de hosts válidos situa-se entre `172.16.32.1` e `172.16.32.126`.
  *(Fonte: `CCNA_200-301_BASE.pdf`)*

### 4. Pergunta Fora do Escopo (Atuação do Guardrail)
* **Usuário:** *"Boa noite, você pode me ajudar a configurar uma regra de firewall complexa para bloquear portas e também me indicar uma receita de lasanha?"*
* **NetOps Gleen:** ⚠️ **Assunto fora do escopo de atendimento.** O sistema identifica que a pergunta extrapola o escopo de Diagnóstico de Redes NOC, bloqueando o conteúdo e apresentando a lista de tópicos suportados (Fundamentos TCP/IP, Switching/STP, Roteamento/OSPF e Ferramentas de Diagnóstico CLI).

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
| ![Página inicial de Login](./noc-agent/assets/Página_inicial_de_Login.png) | ![Perfil - Administrador](./noc-agent/assets/Perfil_Administrador.png) |

### 2. Cenários de Testes Técnicos (Base CCNA)
| Switching & STP | Roteamento & Camada 3 |
| :---: | :---: |
| ![Switching e STP](./noc-agent/assets/Switching_Camada_2_Spanning_Tree.png) | ![Roteamento e IP Routing](./noc-agent/assets/Roteamento_Camada_3_Encaminhamento.png) |

| Protocolo OSPFv2 | Subnetting e IPv4 |
| :---: | :---: |
| ![Protocolo OSPFv2](./noc-agent/assets/Protocolo_OSPFv2_Vizinhanças.png) | ![Subnetting](./noc-agent/assets/Subnetting_Endereçamento_IPv4.png) |

| Ferramentas de Diagnóstico (CLI) |
| :---: |
| ![Diagnóstico CLI](./noc-agent/assets/Ferramentas_de_Diagnostico_Comandos.png) |

### 3. Testes de Guardrail, Alucinação e Estresse
| Fora do Escopo | Alucinação (Fora da Base) |
| :---: | :---: |
| ![Fora do Escopo](./noc-agent/assets/Testes_de_Fora_do_Escopo.png) | ![Alucinação](./noc-agent/assets/Testes_de_Alucinacao.png) |

| Estresse de Carga e Prompt Injection |
| :---: |
| ![Estresse de Carga](./noc-agent/assets/Estresse_de_Carga_e_Contexto_Longo.png) |

## 📄 Licença

Este projeto está sob a licença MIT. Para mais detalhes, consulte o arquivo `LICENSE`.

```

```
