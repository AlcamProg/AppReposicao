import streamlit as st
import json
import urllib.parse
import base64

st.set_page_config(page_title="ALCAM", layout="wide")

# carregar a imagem e converter para base64
def img_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = img_to_base64("imagens/Logo.png")

st.markdown(f"""
<style>
.header {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    border-bottom: 2px solid #ddd;
    background-color: #fafafa;
}}
.header img {{
    height: 70px;
    margin-right: 15px;
}}
.header h1 {{
    font-size: 32px;
    font-weight: 700;
    margin: 0;
}}
</style>

<div class="header">
    <img src="data:image/png;base64,{logo_base64}">
    <h1>ALCAM — Reposição de Peças</h1>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# 1. Ler parâmetro ?cliente= na URL
# -----------------------------------------------------------
query_params = st.query_params

# Se a rota for admin, pula totalmente a lógica de clientes
if query_params.get("admin") == "criar":
    # Importa ou chama sua página de administração
    import admin_criar_catalogo
    st.stop()

# --- PROCESSO NORMAL DOS CLIENTES ---
cliente_id = query_params.get("cliente", "")

if cliente_id == "":
    st.error("❌ Cliente não especificado. Use ?cliente=nome_do_cliente na URL.")
    st.stop()

# -----------------------------------------------------------
# 2. Carregar arquivo JSON do cliente
# -----------------------------------------------------------
arquivo_cliente = f"clientes/{cliente_id}.json"

try:
    with open(arquivo_cliente, "r", encoding="utf-8") as f:
        dados_cliente = json.load(f)
except FileNotFoundError:
    st.error(f"❌ O cliente '{cliente_id}' não foi encontrado.")
    st.stop()

# Extrair dados
nome_cliente = dados_cliente.get("nome", cliente_id)
contato_vendedor = dados_cliente.get("contato_vendedor", "")
pecas = dados_cliente.get("pecas", [])


# -----------------------------------------------------------
# 3. Layout do Streamlit — todas as peças exibidas com IMAGENS
# -----------------------------------------------------------

st.header(f"Reposição de Peças — {nome_cliente}")
st.subheader("Selecione as peças desejadas abaixo:")

pecas_selecionadas = []
quantidades = {}

st.subheader("📦 Lista de Peças Disponíveis")

for peca in pecas:
    st.markdown("---")

    col_img, col_info, col_sel = st.columns([1.4, 3, 1.1])

    # -------------------- IMAGEM --------------------
    with col_img:
        if "imagem" in peca and peca["imagem"]:
            st.image(
                peca["imagem"],
                use_container_width=True
            )
        else:
            st.write("Sem imagem")

    # -------------------- INFORMAÇÕES --------------------
    with col_info:
        st.write(f"### {peca['nome']}")
        st.write(f"**Código:** {peca['codigo']}")
        st.write(f"**Descrição:** {peca.get('descricao', '—')}")

    # -------------------- SELEÇÃO E QUANTIDADE --------------------
    with col_sel:
        adicionar = st.checkbox(
            "Selecionar",
            key=f"chk_{peca['codigo']}"
        )

        if adicionar:
            qtd = st.number_input(
                "Quantidade",
                min_value=1,
                step=1,
                key=f"qtd_{peca['codigo']}"
            )
            pecas_selecionadas.append(peca)
            quantidades[peca['codigo']] = qtd

# Caso nenhuma peça selecionada
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
