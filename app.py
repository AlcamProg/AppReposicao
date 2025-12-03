import streamlit as st
import json
import urllib.parse

from utils.images import img_to_base64
from utils.clients import carregar_cliente
from utils.pecas import carregar_base_pecas
from components.header import render_header

# -----------------------------------------------------------
# CONFIG INICIAL
# -----------------------------------------------------------
st.set_page_config(page_title="ALCAM", layout="wide")

logo_base64 = img_to_base64("imagens/Logo.png")
render_header(logo_base64)

ADMIN_PASSWORD = "SV2024"

# -----------------------------------------------------------
# ESTILO PARA A TELA INICIAL
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
# 0. TELA INICIAL DE ENTRADA — SEM COLUNAS, MAIS BONITA
# -----------------------------------------------------------

# Se ainda não houve escolha de cliente
query_params = st.query_params
cliente_id = query_params.get("cliente", "")

# Exibe a tela inicial APENAS se não houver cliente na URL
if cliente_id == "":

    st.markdown("<h1 class='title-center'>🔧 Sistema de Catálogo ALCAM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='title-center'>Escolha uma opção para continuar</h3>", unsafe_allow_html=True)
    st.write("")

    # -------------------- LOGIN ADMIN --------------------
    st.subheader("🔐 Área do Administrador")
    if st.button("Entrar como Admin"):
        st.switch_page("pages/admin.py")

    # -------------------- ACESSO CLIENTE --------------------
    st.subheader("👤 Acessar Catálogo do Cliente")
    nome_cliente_digitado = st.text_input("Nome do Cliente:")

    if st.button("Entrar como Cliente"):
        if nome_cliente_digitado.strip() == "":
            st.error("Digite o nome do cliente.")
        else:
            st.query_params["cliente"] = nome_cliente_digitado.lower().replace(" ", "_")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()  # Impede que o restante da página carregue enquanto não escolher cliente


# -----------------------------------------------------------
# 1. PROCESSAMENTO NORMAL DA PÁGINA DO CLIENTE
# -----------------------------------------------------------

dados_cliente = carregar_cliente(cliente_id)

if dados_cliente is None:
    st.error(f"❌ O cliente '{cliente_id}' não foi encontrado.")
    st.stop()

nome_cliente = dados_cliente.get("cliente", cliente_id)
contato_vendedor = dados_cliente.get("contato_vendedor", "")
codigos_pecas = dados_cliente.get("pecas", [])

# -----------------------------------------------------------
# 3. Carregar BASE GERAL DE PEÇAS
# -----------------------------------------------------------
pecas_bd = carregar_base_pecas()

pecas = []
for codigo in codigos_pecas:
    if codigo in pecas_bd:
        item = pecas_bd[codigo].copy()
        item["codigo"] = codigo
        pecas.append(item)
    else:
        st.warning(f"⚠ Peça '{codigo}' não encontrada na base geral.")

# -----------------------------------------------------------
# 4. Exibir lista de peças
# -----------------------------------------------------------
st.header(f"Reposição de Peças — {nome_cliente}")
st.subheader("Selecione as peças desejadas abaixo:")

pecas_selecionadas = []
quantidades = {}

st.subheader("📦 Lista de Peças Disponíveis")

for peca in pecas:
    st.markdown("---")

    col_img, col_info, col_sel = st.columns([1.4, 3, 1.1])

    with col_img:
        if peca.get("imagem"):
            st.image(peca["imagem"], use_container_width=True)
        else:
            st.write("Sem imagem")

    with col_info:
        st.write(f"### {peca['nome']}")
        st.write(f"**Código:** {peca['codigo']}")
        st.write(f"**Descrição:** {peca.get('descricao', '—')}")

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
# 5. Criar mensagem e link do WhatsApp
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

st.markdown("### 📲 Enviar pedido")
st.markdown(f"[Clique aqui para enviar no WhatsApp]({link_whatsapp})")
