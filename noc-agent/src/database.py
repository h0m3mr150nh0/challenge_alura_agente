import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def init_db():
    """Cria as tabelas caso ainda não existam e aplica migrações."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL,
                genero TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Garante a criação da coluna is_admin em bancos de dados já existentes
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Coluna já existe

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessoes_chat (id)
            )
        """)
        conn.commit()

def cadastrar_usuario(username: str, senha_bruta: str, nome: str, genero: str, is_admin: bool = False) -> tuple[bool, str]:
    username = username.strip().lower()
    if not username or not senha_bruta or not nome:
        return False, "Preencha todos os campos obrigatórios."
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash, nome_completo, genero, is_admin) VALUES (?, ?, ?, ?, ?)",
                (username, hash_senha(senha_bruta), nome.strip(), genero, 1 if is_admin else 0)
            )
            conn.commit()
            return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Este nome de usuário já está em uso."

def autenticar_usuario(username: str, senha_bruta: str):
    username = username.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, nome_completo, genero, is_admin FROM usuarios WHERE username = ? AND password_hash = ?",
            (username, hash_senha(senha_bruta))
        )
        row = cursor.fetchone()
        return dict(row) if row else None

# --- GERENCIAMENTO DE CHATS E HISTÓRICO ---

def criar_sessao(user_id: int, titulo: str = "Nova Conversa") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessoes_chat (user_id, titulo) VALUES (?, ?)",
            (user_id, titulo)
        )
        conn.commit()
        return cursor.lastrowid

def salvar_mensagem(session_id: int, role: str, content: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensagens (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()

def listar_sessoes_usuario(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, titulo, created_at FROM sessoes_chat WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def carregar_mensagens_sessao(session_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM mensagens WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        return [dict(row) for row in cursor.fetchall()]