import streamlit as st
import json
import os

CLIENTES_DIR = "clientes"

st.set_page_config(page_title="Clientes Cadastrados", page_icon="📋")
st.title("Lista de Clientes Cadastrados")

os.makedirs(CLIENTES_DIR, exist_ok=True)


arquivos = [f for f in os.listdir(CLIENTES_DIR) if f.endswith(".json")]

if not arquivos:
    st.warning("Nenhum cliente cadastrado ainda.")
    st.stop()

clientes_dados = []

# Carregar dados de cada cliente
for arq in arquivos:
    caminho = os.path.join(CLIENTES_DIR, arq)

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)

        cliente = data.get("cliente", "Sem nome")
        vendedor = data.get("vendedor", "—")
        pecas = data.get("pecas", [])
        qtd_pecas = len(pecas)

        clientes_dados.append({
            "cliente": cliente,
            "vendedor": vendedor,
            "qtd_pecas": qtd_pecas
        })

    except Exception as e:
        st.error(f"Erro ao ler {arq}: {e}")

# ================================================
# TABELA RESUMIDA
# ================================================
st.subheader("📊 Visão Geral")

st.dataframe(clientes_dados, use_container_width=True)

# ================================================
# CARDS DETALHADOS
# ================================================
st.subheader("🗂 Detalhes dos Clientes")

for c in clientes_dados:
    with st.container(border=True):
        st.markdown(f"### 👤 **{c['cliente']}**")
        st.write(f"**Vendedor:** {c['vendedor']}")
        st.write(f"**Itens no catálogo:** {c['qtd_pecas']}")
