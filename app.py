import streamlit as st
import json
import urllib.parse

from utils.images import img_to_base64
from utils.clients import carregar_cliente
from components.header import render_header

st.set_page_config(page_title="ALCAM", layout="wide")

# Renderizar o cabeçalho
logo_base64 = img_to_base64("imagens/Logo.png")
render_header(logo_base64)

# -----------------------------------------------------------
# 1. Ler parâmetros da URL
# -----------------------------------------------------------
query_params = st.query_params

# Página ADMIN
if query_params.get("admin") == "criar":
    import pages.admin_criar_catalogo
    st.stop()

cliente_id = query_params.get("cliente", "")

if cliente_id == "":
    st.error("❌ Cliente não especificado. Use ?cliente=nome_do_cliente na URL.")
    st.stop()

# -----------------------------------------------------------
# 2. Carregar dados do cliente
# -----------------------------------------------------------
dados_cliente = carregar_cliente(cliente_id)
if dados_cliente is None:
    st.error(f"❌ O cliente '{cliente_id}' não foi encontrado.")
    st.stop()

nome_cliente = dados_cliente.get("nome", cliente_id)
contato_vendedor = dados_cliente.get("contato_vendedor", "")
pecas = dados_cliente.get("pecas", [])

# -----------------------------------------------------------
# 3. Exibir lista de peças
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

# Nenhuma peça?
if not pecas_selecionadas:
    st.warning("Selecione pelo menos uma peça para continuar.")
    st.stop()

# -----------------------------------------------------------
# 4. Criar mensagem e link do WhatsApp
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
