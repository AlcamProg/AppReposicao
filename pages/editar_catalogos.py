import streamlit as st
import json
import os
from PIL import Image

st.set_page_config(page_title="Editar Catálogo", page_icon="📘")

CATALOGOS_DIR = "clientes"
IMAGENS_DIR = "imagens"
PRODUTOS_FILE = "database/database.json"

# --------------------------------------------------
# Função para carregar produtos
# --------------------------------------------------
def carregar_produtos():
    if not os.path.exists(PRODUTOS_FILE):
        return []
    with open(PRODUTOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------
# Função para carregar catálogo existente
# --------------------------------------------------
def carregar_catalogo(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------
# Função para salvar catálogo atualizado
# --------------------------------------------------
def salvar_catalogo(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --------------------------------------------------
# ABA: EDITAR CATÁLOGOS JÁ CRIADOS
# --------------------------------------------------
st.header("🛠 Editar Catálogos Existentes")

# --------------------------------------------------
# LISTAR CATÁLOGOS EXISTENTES
# --------------------------------------------------
if not os.path.exists(CATALOGOS_DIR):
    st.warning("A pasta 'catalogos' não existe.")
    st.stop()

arquivos = [f for f in os.listdir(CATALOGOS_DIR) if f.endswith(".json")]

if len(arquivos) == 0:
    st.warning("Nenhum catálogo encontrado na pasta.")
    st.stop()

nome_catalogo = st.selectbox("Selecione um catálogo:", arquivos)

caminho_catalogo = os.path.join(CATALOGOS_DIR, nome_catalogo)

# Carregar catálogo selecionado
catalogo = carregar_catalogo(caminho_catalogo)

if "pecas" not in catalogo:
    st.error("Esse catálogo não possui o formato esperado (sem 'pecas').")
    st.stop()

if "cliente" not in catalogo:
    catalogo["cliente"] = ""

cliente_edit = st.text_input("Nome do cliente:", value=catalogo["cliente"])

st.markdown("---")
st.subheader("Peças do catálogo")

# --------------------------------------------------
# LISTAR E EDITAR CADA PEÇA
# --------------------------------------------------
remover_indices = []

for i, p in enumerate(catalogo["pecas"]):

    with st.container():
        st.write(f"### {p['nome']} ({p['codigo']})")

        # Editar textos
        novo_nome = st.text_input("Nome:", value=p["nome"], key=f"nome_{i}")
        nova_desc = st.text_area("Descrição:", value=p["descricao"], key=f"desc_{i}")

        p["nome"] = novo_nome
        p["descricao"] = nova_desc

        # Editar imagem
        st.write("Imagem atual:")
        st.image(p["imagem"], width=200)

        nova_img = st.file_uploader("Nova imagem (opcional)", key=f"img_{i}")

        if nova_img:
            ext = nova_img.name.split(".")[-1].lower()
            if ext == "jpeg": ext = "jpg"

            img_filename = f"{p['codigo']}.{ext}"
            img_path = os.path.join(IMAGENS_DIR, img_filename)

            image = Image.open(nova_img)
            image.save(img_path)

            p["imagem"] = f"{IMAGENS_DIR}/{img_filename}"

        # Botão de remoção
        if st.button("🗑 Remover peça", key=f"remove_{i}"):
            remover_indices.append(i)

# Remover peças selecionadas
for idx in sorted(remover_indices, reverse=True):
    catalogo["pecas"].pop(idx)

st.markdown("---")

# --------------------------------------------------
# ADICIONAR NOVA PEÇA AO CATÁLOGO
# --------------------------------------------------
st.subheader("Adicionar nova peça ao catálogo")

codigo_novo = st.text_input("Código da peça:")
nome_novo = st.text_input("Nome da peça:")
desc_novo = st.text_area("Descrição:")
img_nova = st.file_uploader("Imagem:", type=["png", "jpg", "jpeg"])

if st.button("Adicionar peça"):
    if not codigo_novo or not nome_novo or not img_nova:
        st.error("Preencha todos os campos e envie uma imagem.")
    else:
        ext = img_nova.name.split(".")[-1].lower()
        if ext == "jpeg": ext = "jpg"

        img_filename = f"{codigo_novo}.{ext}"
        img_path = os.path.join(IMAGENS_DIR, img_filename)

        image = Image.open(img_nova)
        image.save(img_path)

        nova_peca = {
            "codigo": codigo_novo,
            "nome": nome_novo,
            "descricao": desc_novo,
            "imagem": f"{IMAGENS_DIR}/{img_filename}"
        }

        catalogo["pecas"].append(nova_peca)
        st.success("Peça adicionada com sucesso!")
        st.rerun()

# --------------------------------------------------
# SALVAR ALTERAÇÕES
# --------------------------------------------------
if st.button("💾 Salvar catálogo"):
    catalogo["cliente"] = cliente_edit
    salvar_catalogo(caminho_catalogo, catalogo)
    st.success("Catálogo atualizado com sucesso!")
