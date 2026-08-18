import gender_guesser.detector as gender
import markdown
import streamlit as st

from database import (
    autenticar_usuario,
    cadastrar_usuario,
    carregar_mensagens_sessao,
    criar_sessao,
    init_db,
    listar_sessoes_usuario,
    salvar_mensagem,
)
from rag import responder_pergunta

# 📌 Inicializa o banco de dados
init_db()

st.set_page_config(page_title="NOC Agent", layout="centered")

# 📌 Avatares
AVATAR_MASCULINO = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
AVATAR_FEMININO = "https://cdn-icons-png.flaticon.com/512/4140/4140047.png"
AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/3662/3662817.png"

# 🎨 CSS Customizado
st.markdown(
    """
<style>
.msg-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 12px;
}

.msg-row.user {
    flex-direction: row-reverse;
}

.avatar-img {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
}

.user-msg {
    background-color: #2563eb;
    color: white;
    padding: 8px 14px;
    border-radius: 12px;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 0.95rem;
    line-height: 1.4;
}

.bot-msg {
    background-color: #1f2937;
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 0.95rem;
    line-height: 1.4;
}

.bot-msg p {
    margin: 0 0 6px 0 !important;
    padding: 0 !important;
}

.bot-msg p:last-child {
    margin-bottom: 0 !important;
}

.bot-msg ul, .bot-msg ol {
    margin: 6px 0 !important;
    padding-left: 20px !important;
}

.bot-msg li {
    margin-bottom: 4px !important;
}

.bot-msg hr {
    margin: 8px 0 !important;
    border-color: #374151;
}

.bot-msg code {
    background-color: #111827;
    color: #38bdf8;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.88rem;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def carregar_detector():
  return gender.Detector()


detector = carregar_detector()


def inferir_genero(nome: str) -> str:
  primeiro_nome = nome.strip().split()[0].capitalize()
  resultado = detector.get_gender(primeiro_nome)
  if resultado in ["female", "mostly_female"]:
    return "Feminino"
  if resultado in ["male", "mostly_male"]:
    return "Masculino"
  if primeiro_nome.lower().endswith(("a", "ia", "ais", "eia", "ina")):
    return "Feminino"
  return "Masculino"


# 🧠 Inicialização das variáveis de sessão
if "usuario_logado" not in st.session_state:
  st.session_state.usuario_logado = None

if "sessao_id_atual" not in st.session_state:
  st.session_state.sessao_id_atual = None

if "messages" not in st.session_state:
  st.session_state.messages = []


# -----------------------------------------------------------------------------
# TELA DE AUTENTICAÇÃO (SOMENTE LOGIN)
# -----------------------------------------------------------------------------
if st.session_state.usuario_logado is None:
    st.title("🔐 NOC Agent - Acesso Restrito")
    
    st.subheader("Login de Operador")
    user_input = st.text_input("Usuário", key="login_user")
    pass_input = st.text_input("Senha", type="password", key="login_pass")

    if st.button("Entrar", type="primary"):
        user = autenticar_usuario(user_input, pass_input)
        if user:
            st.session_state.usuario_logado = user
            st.session_state.messages = []
            st.session_state.sessao_id_atual = None
            st.success(f"Bem-vindo, {user['nome_completo']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.stop()


# -----------------------------------------------------------------------------
# SIDEBAR (PERFIL + ADMIN PANEL + HISTÓRICO)
# -----------------------------------------------------------------------------
user_atual = st.session_state.usuario_logado
avatar_user = AVATAR_MASCULINO if user_atual["genero"] == "Masculino" else AVATAR_FEMININO

with st.sidebar:
    st.image(avatar_user, width=64)
    st.markdown(f"### **{user_atual['nome_completo']}**")
    
    if user_atual.get("is_admin"):
        st.badge("🛡️ Administrador")
    else:
        st.caption(f"Operador @{user_atual['username']}")

    if st.button("➕ Nova Conversa", use_container_width=True, type="primary"):
        st.session_state.sessao_id_atual = None
        st.session_state.messages = []
        st.rerun()

    # 🔑 PAINEL EXCLUSIVO DO ADMINISTRADOR
    if user_atual.get("is_admin"):
        st.divider()
        with st.expander("👤 Cadastrar Novo Operador"):
            novo_nome = st.text_input("Nome Completo", key="adm_nome")
            novo_user = st.text_input("Usuário Login", key="adm_user")
            nova_pass = st.text_input("Senha", type="password", key="adm_pass")
            
            if st.button("Cadastrar Usuário", key="btn_cadastrar_admin"):
                if novo_nome and novo_user and nova_pass:
                    genero_detectado = inferir_genero(novo_nome)
                    sucesso, msg = cadastrar_usuario(novo_user, nova_pass, novo_nome, genero_detectado)
                    if sucesso:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha todos os campos.")

    st.divider()
    st.markdown("📜 **Histórico de Conversas**")

    sessoes = listar_sessoes_usuario(user_atual["id"])
    for s in sessoes:
        label = f"💬 {s['titulo'][:22]}..." if len(s['titulo']) > 22 else f"💬 {s['titulo']}"
        if st.button(label, key=f"sess_{s['id']}", use_container_width=True):
            st.session_state.sessao_id_atual = s["id"]
            msges = carregar_mensagens_sessao(s["id"])
            st.session_state.messages = msges
            st.rerun()

    st.divider()
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sessao_id_atual = None
        st.session_state.messages = []
        st.rerun()


# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL DE CHAT
# -----------------------------------------------------------------------------
st.title("💬 NOC Troubleshooting Agent")

# Mensagem inicial de boas-vindas para nova conversa
if not st.session_state.messages:
    mensagem_inicial = (
        f"👋 Olá, <b>{user_atual['nome_completo']}</b>! Sou o Gleen, seu assistente virtual de NOC. 🤖<br><br>"
        "<i>Aviso: Este sistema é um projeto desenvolvido para fins de estudo e pesquisa.</i><br><br>"
        "Meu escopo de atendimento é focado exclusivamente em <b>Diagnóstico e Troubleshooting de Redes</b>. "
        "Estou pronto para te ajudar com dúvidas e análises sobre:<br>"
        "<ul>"
        "<li><b>Conectividade IP e TCP/IP</b></li>"
        "<li><b>Roteamento (OSPF, Rotas Estáticas)</b></li>"
        "<li><b>Protocolos de Redundância (HSRP)</b></li>"
        "<li><b>Ferramentas de Diagnóstico (Ping, Traceroute, Telnet, Debugs)</b></li>"
        "</ul>"
        "Como posso ajudar na sua operação hoje?"
    )
    st.session_state.messages = [
        {"role": "assistant", "content": mensagem_inicial}
    ]

# Renderização das mensagens do chat
for msg in st.session_state.messages:
  if msg["role"] == "user":
    html_code = f'<div class="msg-row user"><img src="{avatar_user}" class="avatar-img"><div class="user-msg">{msg["content"]}</div></div>'
  else:
    conteudo_convertido = markdown.markdown(msg["content"])
    html_code = f'<div class="msg-row bot"><img src="{AVATAR_BOT}" class="avatar-img"><div class="bot-msg">{conteudo_convertido}</div></div>'

  st.markdown(html_code, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# CAIXA DE ENTRADA E PROCESSAMENTO DE PERGUNTAS
# -----------------------------------------------------------------------------
if prompt_user := st.chat_input("Digite sua pergunta de suporte..."):

  # Cria uma nova sessão no banco de dados na primeira pergunta
  if st.session_state.sessao_id_atual is None:
    novo_id = criar_sessao(user_atual["id"], titulo=prompt_user)
    st.session_state.sessao_id_atual = novo_id
    # Salva a mensagem inicial de boas-vindas do assistente
    salvar_mensagem(
        novo_id, "assistant", st.session_state.messages[0]["content"]
    )

  # Adiciona e salva a pergunta do usuário
  st.session_state.messages.append({"role": "user", "content": prompt_user})
  salvar_mensagem(st.session_state.sessao_id_atual, "user", prompt_user)

  user_html = f'<div class="msg-row user"><img src="{avatar_user}" class="avatar-img"><div class="user-msg">{prompt_user}</div></div>'
  st.markdown(user_html, unsafe_allow_html=True)

  # Gera a resposta do RAG enviando o histórico
  with st.spinner(
      "🤖 Consultando base de conhecimento e gerando resposta..."
  ):
    historico_anterior = st.session_state.messages[:-1]
    resposta = responder_pergunta(prompt_user, historico=historico_anterior)

  # Adiciona e salva a resposta da IA
  st.session_state.messages.append({"role": "assistant", "content": resposta})
  salvar_mensagem(st.session_state.sessao_id_atual, "assistant", resposta)

  st.rerun()