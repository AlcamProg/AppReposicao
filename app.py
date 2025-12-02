import streamlit as st
import json
import urllib.parse

# -----------------------------------------------------------
# 1. Ler parâmetro ?cliente= na URL
# -----------------------------------------------------------
query_params = st.query_params
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

st.title(f"Reposição de Peças — {nome_cliente}")
st.write("Selecione as peças desejadas abaixo:")

pecas_selecionadas = []
quantidades = {}

st.subheader("📦 Lista de Peças Disponíveis")

for peca in pecas:
    st.markdown("---")

    col_img, col_info, col_sel = st.columns([1.4, 3, 1])

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
                "Qtd",
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
