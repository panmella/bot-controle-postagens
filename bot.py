import os
import re
import telebot
from dotenv import load_dotenv
from banco import (
    inicializar_banco,
    registrar_postagem,
    gerar_relatorio,
    atualizar_nome_adm,
    buscar_nome_oficial,
    link_ja_existe,
    apagar_ultima_postagem,
)
from graficos import gerar_grafico_pizza

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
inicializar_banco()

META_SEMANAL = 8


@bot.message_handler(commands=["start", "ajuda"])
def boas_vindas(mensagem):
    texto = (
        "🖤🩷 *Oi, ADMs! Bem-vindos ao contador de posts do Portal BLACKPINK!*\n\n"
         "          *\n\n"

        "• Compartilhe qualquer link do X/Twitter aqui no grupo que eu registro automaticamente.\n"
        "• Digite `/nome SeuNome` para definir como você aparece no ranking.\n"
        "• Digite `/desfazer` se mandou um link errado e quer apagar seu último registro.\n"
        "• Digite `/relatorio` para ver o ranking dos últimos 7 dias e quem bateu a meta semanal."
    )
    bot.reply_to(mensagem, texto, parse_mode="Markdown")


@bot.message_handler(commands=["nome"])
def definir_nome(mensagem):
    partes = mensagem.text.split(maxsplit=1)
    if len(partes) < 2 or not partes[1].strip():
        bot.reply_to(
            mensagem,
            "⚠️ Digite seu nome após o comando. Exemplo: `/nome Pami`",
            parse_mode="Markdown",
        )
        return

    novo_nome = partes[1].strip()
    atualizar_nome_adm(mensagem.from_user.id, novo_nome)
    bot.reply_to(
        mensagem,
        f"✅ Nome atualizado para *{novo_nome}* no relatório!",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["desfazer"])
def desfazer_ultimo_post(mensagem):
    apagou = apagar_ultima_postagem(mensagem.from_user.id)
    if apagou:
        bot.reply_to(mensagem, "🗑️ Sua última postagem registrada foi removida!")
    else:
        bot.reply_to(mensagem, "⚠️ Você ainda não tem postagens registradas para apagar.")


def montar_e_enviar_relatorio(mensagem, dias: int, titulo: str, mostrar_meta=False, enviar_grafico=False):
    dados = gerar_relatorio(dias)

    if not dados:
        bot.reply_to(mensagem, f"📭 Nenhuma postagem registrada para: *{titulo}*.", parse_mode="Markdown")
        return

    linhas = [f"📊 *{titulo}*\n"]
    for nome_adm, total in dados:
        if mostrar_meta:
            status = "✅ Meta batida!" if total >= META_SEMANAL else f"⏳ Faltam {META_SEMANAL - total}"
            linhas.append(f"• *{nome_adm}*: {total} post(s) — {status}")
        else:
            linhas.append(f"• *{nome_adm}*: {total} post(s)")

    texto_final = "\n".join(linhas)

    if enviar_grafico:
        caminho_img = gerar_grafico_pizza(dados, titulo)
        with open(caminho_img, "rb") as foto:
            bot.send_photo(mensagem.chat.id, foto, caption=texto_final, parse_mode="Markdown")
        os.remove(caminho_img)  # Apaga a imagem temporária depois de enviar
    else:
        bot.reply_to(mensagem, texto_final, parse_mode="Markdown")


@bot.message_handler(commands=["relatorio", "semanal"])
def relatorio_semanal(mensagem):
    montar_e_enviar_relatorio(
        mensagem,
        dias=7,
        titulo="Relatório Semanal (Últimos 7 dias)",
        mostrar_meta=True,
        enviar_grafico=False,
    )


@bot.message_handler(commands=["mensal"])
def relatorio_mensal(mensagem):
    montar_e_enviar_relatorio(
        mensagem,
        dias=30,
        titulo="Ranking Mensal (Últimos 30 dias)",
        mostrar_meta=False,
        enviar_grafico=True,
    )


@bot.message_handler(commands=["anual"])
def relatorio_anual(mensagem):
    montar_e_enviar_relatorio(
        mensagem,
        dias=365,
        titulo="Ranking Anual (Últimos 365 dias)",
        mostrar_meta=False,
        enviar_grafico=True,
    )


@bot.message_handler(func=lambda msg: msg.text is not None)
def capturar_link(mensagem):
    match = re.search(r"(https?://(?:www\.)?(?:x\.com|twitter\.com)/\S+)", mensagem.text)

    if match:
        # Limpa parâmetros extras do botão de compartilhar (?s=20, ?t=..., etc.)
        link = match.group(1).split("?")[0]

        if link_ja_existe(link):
            bot.reply_to(mensagem, "⚠️ Esse link já foi registrado anteriormente!")
            return

        usuario_id = mensagem.from_user.id
        nome_telegram = mensagem.from_user.first_name or mensagem.from_user.username or "ADM"
        nome_adm = buscar_nome_oficial(usuario_id, nome_telegram)

        registrar_postagem(usuario_id, nome_adm, link)
        try:
            bot.set_message_reaction(
                mensagem.chat.id,
                mensagem.id,
                [telebot.types.ReactionTypeEmoji("✅")],
            )
        except Exception:
            bot.reply_to(mensagem, "✅")


print("🤖 Bot rodando! Pressione Ctrl + C no terminal para parar.")
bot.infinity_polling()