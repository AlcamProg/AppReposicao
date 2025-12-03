import streamlit as st
import json
import os
import base64
import requests
from PIL import Image
from io import BytesIO

# -----------------------------------------------------------
# 1. Proteção por rota
# -----------------------------------------------------------
params = st.query_params

if params.get("admin") != "criar":
    st.error("⛔ Acesso restrito. Esta página é exclusiva para administradores.")
    st.stop()

st.title("📘 Criar Novo Catálogo de Cliente")


# -----------------------------------------------------------
# Configurações GitHub
# -----------------------------------------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]

API_URL = f"https://api.github.com/repos/{REPO}/contents/"


def github_upload(path, content, message):
    """Faz upload de arquivos diretamente para o GitHub."""
    url = API_URL + path

    # Verificar se o arquivo já existe (necessário para atualizar)
    get_file = requests.get(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})

    sha = None
    if get_file.status_code == 200:
        sha = get_file.json().get("sha")

    payload = {
        "message": message,
        "content": content,
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(
        url,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        json=payload
    )

    return response.status_code, response.text


# -----------------------------------------------------------
# 2. Dados do Cliente
# -----------------------------------------------------------
st.subheader("Informações do Cliente")

cliente = st.text_input("Nome do Cliente (ex: Cliente A)")
vendedor = st.text_input("Nome do Vendedor")
contato_vendedor = st.text_input("WhatsApp do Vendedor (ex: 5515999999999)")


# -----------------------------------------------------------
# 3. Cadastro das Peças
# -----------------------------------------------------------

st.subheader("📦 Adicionar Peças")

if "pecas" not in st.session_state:
    st.session_state.pecas = []

with st.form("form_peca"):
    nome = st.text_input("Nome da Peça")
    codigo = st.text_input("Código")
    descricao = st.text_area("Descrição")
    imagem = st.file_uploader("Imagem da Peça", type=["png", "jpg", "jpeg"])

    adicionar = st.form_submit_button("Adicionar Peça")

    if adicionar:
        if nome == "" or codigo == "" or descricao == "":
            st.error("Preencha todos os campos antes de adicionar.")
        else:
            st.session_state.pecas.append({
                "nome": nome,
                "codigo": codigo,
                "descricao": descricao,
                "imagem_file": imagem
            })
            st.success(f"Peça '{nome}' adicionada!")


# -----------------------------------------------------------
# 4. Listar Peças Adicionadas
# -----------------------------------------------------------
st.write("### 📝 Peças já cadastradas:")

for p in st.session_state.pecas:
    st.write(f"**{p['nome']}** ({p['codigo']})")
    st.write(p["descricao"])
    if p["imagem_file"]:
        st.image(p["imagem_file"], width=150)


# -----------------------------------------------------------
# 5. Botão FINAL - Salvar catálogo no GitHub
# -----------------------------------------------------------
if st.button("💾 Salvar Catálogo no GitHub"):
    if cliente == "" or vendedor == "" or contato_vendedor == "":
        st.error("Preencha todos os dados do cliente antes de salvar.")
        st.stop()

    if len(st.session_state.pecas) == 0:
        st.error("Adicione pelo menos uma peça antes de salvar.")
        st.stop()

    cliente_file = cliente.lower().replace(" ", "_")

    pecas_json = []

    # Enviar imagens e montar lista
    for p in st.session_state.pecas:

        # Converter imagem para base64 e enviar ao GitHub
        if p["imagem_file"]:
            img = Image.open(p["imagem_file"])
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)

            img_b64 = base64.b64encode(buffer.read()).decode()
            img_path = f"imagens/{p['codigo']}.jpg"

            status, response = github_upload(
                img_path,
                img_b64,
                f"Add image for {p['codigo']}"
            )

            if status not in [200, 201]:
                st.error(f"Erro ao enviar imagem {p['codigo']}: {response}")
                st.stop()

        else:
            img_path = ""

        pecas_json.append({
            "nome": p["nome"],
            "codigo": p["codigo"],
            "descricao": p["descricao"],
            "imagem": img_path
        })

    # Criar o JSON
    catalogo = {
        "cliente": cliente,
        "vendedor": vendedor,
        "contato_vendedor": contato_vendedor,
        "pecas": pecas_json
    }

    conteudo_json = base64.b64encode(
        json.dumps(catalogo, indent=4, ensure_ascii=False).encode()
    ).decode()

    json_path = f"catalogos/{cliente_file}.json"

    status, response = github_upload(
        json_path,
        conteudo_json,
        f"Add catalog for {cliente}"
    )

    if status in [200, 201]:
        st.success("✅ Catálogo salvo com sucesso!")
        st.info(f"Arquivo criado/atualizado: `{json_path}`")
        st.balloons()
    else:
        st.error("❌ Erro ao salvar no GitHub")
        st.code(response)


