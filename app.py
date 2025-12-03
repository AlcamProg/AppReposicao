import streamlit as st
import json
import urllib.parse

from utils.images import img_to_base64
from utils.clients import carregar_cliente
from components.header import render_header

# -----------------------------------------------------------
# CONFIG INICIAL
# -----------------------------------------------------------
st.set_page_config(page_title="ALCAM", layout="wide")

logo_base64 = img_to_base64("imagens/Logo.png")
render_header(logo_base64)

ADMIN_PASSWORD = "SV2024"

# -----------------------------------------------------------
# FUNÇÃO: Carregar database.json (base geral dos produtos)
# -----------------------------------------------------------
def carregar_database():
    try:
        with open("database/database.json", "r", encoding="utf-8") as f:
            lista = json.load(f)

        # converter para dict por código
        return {item["codigo"]: item for item in lista}

    except FileNotFoundError:
        st.error("❌ O arquivo 'database.json' não foi encontrado em /database/")
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar database.json: {e}")
        return {}

# -----------------------------------------------------------
# ESTILO DA TELA INICIAL
# -----------------------------------------------------------
st.markdown("""
<style>
.box {
    padding: 25px;
    border-radius: 12px;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    margin-bottom: 25px;
}
.title-center {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# 0. TELA INICIAL — APARECE QUANDO NÃO TEM CLIENTE NA URL
# -----------------------------------------------------------

query_params = st.query_params
cliente_id = query_params.get("cliente", "")

if cliente_id == "":
    st.markdown("<h1 class='title-center'>🔧 Sistema de Catálogo ALCAM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='title-center'>Escolha uma opção para continuar</h3>", unsafe_allow_html=True)
    st.write("")

    # ---------------- LOGIN ADMIN ----------------
    st.subheader("🔐 Área do Administrador")
    if st.button("Entrar como Admin"):
        st.switch_page("pages/admin.py")

    # ---------------- LOGIN CLIENTE ----------------
    st.subheader("👤 Acessar Catálogo do Cliente")
    nome_cliente_digitado = st.text_input("Nome do Cliente:")

    if st.button("Entrar como Cliente"):
        if nome_cliente_digitado.strip() == "":
            st.error("Digite o nome do cliente.")
        else:
            st.query_params["cliente"] = nome_cliente_digitado.lower().replace(" ", "_")
            st.rerun()

    st.stop()

# -----------------------------------------------------------
# 1. PROCESSAR CLIENTE
# -----------------------------------------------------------

dados_cliente = carregar_cliente(cliente_id)

if dados_cliente is None:
    st.error(f"❌ O cliente '{cliente_id}' não foi encontrado.")
    st.stop()

nome_cliente = dados_cliente.get("cliente", cliente_id)
contato_vendedor = dados_cliente.get("contato", "")

# Normalizar lista de peças do cliente
pecas_raw = dados_cliente.get("pecas", [])

codigos_pecas = []

for item in pecas_raw:
    if isinstance(item, dict):
        # caso venha algo como {"codigo": "123"}
        if "codigo" in item:
            codigos_pecas.append(item["codigo"])
        else:
            st.warning(f"Formato inesperado de peça no cliente '{nome_cliente}': {item}")
    else:
        # caso seja apenas o código como string
        codigos_pecas.append(item)


# -----------------------------------------------------------
# 2. CARREGAR BASE DE PRODUTOS DO DATABASE.JSON
# -----------------------------------------------------------
pecas_bd = carregar_database()

pecas = []
for codigo in codigos_pecas:
    if codigo in pecas_bd:
        item = pecas_bd[codigo].copy()
        item["codigo"] = codigo
        pecas.append(item)
    else:
        st.warning(f"⚠ Peça '{codigo}' não encontrada no database.")

# -----------------------------------------------------------
# 3. EXIBIR LISTA DE PEÇAS
# -----------------------------------------------------------
st.header(f"Reposição de Peças — {nome_cliente}")
st.subheader("Selecione as peças desejadas abaixo:")

pecas_selecionadas = []
quantidades = {}

st.subheader("📦 Lista de Peças Disponíveis")

for peca in pecas:
    st.markdown("---")

    col_img, col_info, col_sel = st.columns([1.4, 3, 1.1])

    # Imagem
    with col_img:
        if peca.get("imagem"):
            st.image(peca["imagem"], use_container_width=True)
        else:
            st.write("Sem imagem")

    # Informações
    with col_info:
        st.write(f"### {peca['nome']}")
        st.write(f"**Código:** {peca['codigo']}")
        st.write(f"**Descrição:** {peca.get('descricao', '—')}")

    # Seleção
    with col_sel:
        adicionar = st.checkbox("Selecionar", key=f"chk_{peca['codigo']}")
        if adicionar:
            qtd = st.number_input(
                "Quantidade",
                min_value=1,
                step=1,
                key=f"qtd_{peca['codigo']}"
            )
            pecas_selecionadas.append(peca)
            quantidades[peca['codigo']] = qtd

if not pecas_selecionadas:
    st.warning("Selecione pelo menos uma peça para continuar.")
    st.stop()

# -----------------------------------------------------------
# 4. GERAR MENSAGEM PARA WHATSAPP
# -----------------------------------------------------------
texto_itens = ""
for p in pecas_selecionadas:
    cod = p["codigo"]
    nome = p["nome"]
    qtd = quantidades[cod]
    texto_itens += f"- {nome} (código {cod}) — Quantidade: {qtd}\n"

mensagem = f"""
*Pedido de Reposição de Peças*  
Cliente: {nome_cliente}

*Itens Selecionados:*  
{texto_itens}
"""

mensagem = urllib.parse.quote(mensagem)
link_whatsapp = f"https://wa.me/{contato_vendedor}?text={mensagem}"
mensagem = urllib.parse.quote(mensagem)
link_whatsapp = f"https://wa.me/{contato_vendedor}?text={mensagem}"

mensagem = urllib.parse.quote(mensagem)
link_whatsapp = f"https://wa.me/{contato_vendedor}?text={mensagem}"

st.markdown("""
    <style>
    .wpp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 12px 20px;
        border-radius: 15px;
        text-decoration: none !important;
        font-weight: bold;
        font-size: 20px;
        display: inline-block;
        margin-top: 15px;
    }
    .wpp-btn:hover {
        background-color: #1ebe5d;
        text-decoration: none !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <a href="{link_whatsapp}" target="_blank" class="wpp-btn">
        📲 Enviar Pedido via WhatsApp
    </a>
""", unsafe_allow_html=True)


