import sqlite3
from datetime import datetime, timedelta


NOME_BANCO = "portal_postagens.db"


def conectar():
    """Abre conexão com o arquivo do banco de dados SQLite."""
    return sqlite3.connect(NOME_BANCO)


def inicializar_banco():
    """Cria a tabela de postagens usando SQL caso ela ainda não exista."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome_adm TEXT NOT NULL,
            link_post TEXT NOT NULL,
            data_envio TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def registrar_postagem(usuario_id: int, nome_adm: str, link_post: str):
    """Insere um novo registro de postagem no banco de dados (SQL INSERT)."""
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO postagens (usuario_id, nome_adm, link_post, data_envio) VALUES (?, ?, ?, ?)",
        (usuario_id, nome_adm, link_post, agora),
    )

    conn.commit()
    conn.close()


def gerar_relatorio(dias: int):
    """Consulta o total de posts por ADM no período informado (SQL SELECT + COUNT + GROUP BY)."""
    conn = conectar()
    cursor = conn.cursor()

    data_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        SELECT nome_adm, COUNT(*) as total_posts
        FROM postagens
        WHERE data_envio >= ?
        GROUP BY usuario_id, nome_adm
        ORDER BY total_posts DESC
        """,
        (data_limite,),
    )

    resultados = cursor.fetchall()
    conn.close()
    return resultados

def atualizar_nome_adm(usuario_id: int, novo_nome: str):
    """Atualiza o nome do ADM no banco de dados (SQL UPDATE + INSERT/REPLACE)."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfis_adms (
            usuario_id INTEGER PRIMARY KEY,
            nome_oficial TEXT NOT NULL
        )
    """)

    cursor.execute(
        "INSERT OR REPLACE INTO perfis_adms (usuario_id, nome_oficial) VALUES (?, ?)",
        (usuario_id, novo_nome),
    )

    cursor.execute(
        "UPDATE postagens SET nome_adm = ? WHERE usuario_id = ?",
        (novo_nome, usuario_id),
    )

    conn.commit()
    conn.close()


def buscar_nome_oficial(usuario_id: int, nome_padrao: str) -> str:
    """Verifica se o ADM já cadastrou um nome oficial; se não, usa o do Telegram."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfis_adms (
            usuario_id INTEGER PRIMARY KEY,
            nome_oficial TEXT NOT NULL
        )
    """)

    cursor.execute(
        "SELECT nome_oficial FROM perfis_adms WHERE usuario_id = ?",
        (usuario_id,),
    )
    resultado = cursor.fetchone()
    conn.close()

    return resultado[0] if resultado else nome_padrao

def link_ja_existe(link_post: str) -> bool:
    """Verifica no banco SQL se o link já foi registrado anteriormente."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM postagens WHERE link_post = ?", (link_post,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def apagar_ultima_postagem(usuario_id: int) -> bool:
    """Apaga o registro mais recente daquele ADM (SQL DELETE)."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM postagens WHERE usuario_id = ? ORDER BY id DESC LIMIT 1",
        (usuario_id,),
    )
    ultimo = cursor.fetchone()

    if not ultimo:
        conn.close()
        return False

    cursor.execute("DELETE FROM postagens WHERE id = ?", (ultimo[0],))
    conn.commit()
    conn.close()
    return True