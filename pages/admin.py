import streamlit as st
import json
import os
from PIL import Image
import base64, requests

# ===========================
# CONFIGURAÇÕES
# ===========================
st.set_page_config(page_title="Criar Catálogo", page_icon="📘")

PASSWORD = "SV2024"

PRODUTOS_FILE = "database/database.json"
CLIENTES_DIR = "clientes"
IMAGENS_DIR = "imagens"

os.makedirs(CLIENTES_DIR, exist_ok=True)
os.makedirs(IMAGENS_DIR, exist_ok=True)

# ===========================
# FUNÇÕES AUXILIARES
# ===========================
def carregar_produtos():
    if not os.path.exists(PRODUTOS_FILE):
        return []
    with open(PRODUTOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_produtos(produtos):
    with open(PRODUTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=2, ensure_ascii=False)

def buscar_produto_por_codigo(produtos, codigo):
    for p in produtos:
        if p["codigo"] == codigo:
            return p
    return None

# ===========================
# LOGIN
# ===========================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Área Restrita")
    senha = st.text_input("Digite a senha:", type="password")

    if st.button("Entrar"):
        if senha == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ===========================
# SESSION STATE SEGURO
# ===========================
defaults = {
    "cliente": "",
    "vendedor": "",
    "contato": "",
    "codigo_busca": "",
    "nome_novo": "",
    "descricao_novo": "",
    "pecas_cliente": [],
    "produtos_novos": [],   # << BUFFER DE NOVOS PRODUTOS
    "reset": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Função de reset
def reset_form():
    for key in defaults:
        if key not in ["pecas_cliente", "produtos_novos"]:
            st.session_state[key] = ""
    st.session_state.pecas_cliente = []
    st.session_state.produtos_novos = []
    st.session_state.reset = False
    st.rerun()

if st.session_state.reset:
    reset_form()
st.title("📘 Criar Catálogo")

cliente = st.text_input("Nome do Cliente", key="cliente")
vendedor = st.text_input("Nome do Vendedor", key="vendedor")
contato = st.text_input("Contato do Vendedor", key="contato")

st.subheader("🔧 Adicionar Peças ao Catálogo")

produtos = carregar_produtos()

# Buscar peça existente
codigo_busca = st.text_input("Código da Peça", key="codigo_busca")

if st.button("🔍 Buscar peça por código"):
    if not codigo_busca:
        st.error("Digite um código!")
    else:
        produto = buscar_produto_por_codigo(produtos, codigo_busca)

        if produto:
            st.success(f"Produto encontrado: {produto['nome']}")
            st.session_state.pecas_cliente.append(produto)
        else:
            st.warning("Produto não encontrado. Cadastre abaixo.")
st.markdown("### ➕ Cadastrar Novo Produto")

nome_novo = st.text_input("Nome da Nova Peça", key="nome_novo")
descricao_novo = st.text_area("Descrição da Nova Peça", key="descricao_novo")
upload_novo = st.file_uploader("Imagem da Nova Peça", type=["png", "jpg", "jpeg"])

if st.button("💾 Salvar Novo Produto"):
    if not codigo_busca:
        st.error("Digite o CÓDIGO do novo produto acima.")
    elif not nome_novo or not descricao_novo or upload_novo is None:
        st.error("Preencha todos os campos!")
    else:
        ext = upload_novo.name.split(".")[-1]
        img_filename = f"{codigo_busca}.{ext}"
        img_path = os.path.join(IMAGENS_DIR, img_filename)

        image = Image.open(upload_novo)
        image.save(img_path)

        img_path = img_path.replace("\\", "/")

        novo_produto = {
            "codigo": codigo_busca,
            "nome": nome_novo,
            "descricao": descricao_novo,
            "imagem": img_path
        }

        produtos.append(novo_produto)
        salvar_produtos(produtos)

        st.session_state.pecas_cliente.append(novo_produto)

        # 🟦 GUARDAR PARA UPLOAD NO FINAL
        st.session_state.produtos_novos.append({
            "img_filename": img_filename,
            "img_path": img_path
        })

        st.success("Produto cadastrado e adicionado ao catálogo!")
st.markdown("### 📄 Peças adicionadas ao catálogo")

for i, p in enumerate(st.session_state.pecas_cliente):
    st.write(f"**{i+1}. {p['nome']}** — {p['codigo']}")
    st.write(p["descricao"])
    st.write("---")
if st.button("📁 Salvar Catálogo do Cliente"):

    if not cliente or not vendedor or not contato:
        st.error("Preencha os dados do cliente!")
        st.stop()

    if len(st.session_state.pecas_cliente) == 0:
        st.error("Adicione ao menos uma peça!")
        st.stop()

    data = {
        "cliente": cliente,
        "vendedor": vendedor,
        "contato": contato,
        "pecas": st.session_state.pecas_cliente
    }

    json_name = f"{cliente.replace(' ', '_').lower()}.json"
    json_path_local = f"{CLIENTES_DIR}/{json_name}"

    with open(json_path_local, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    st.success("Catálogo salvo localmente!")

    # GITHUB PARAMS
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
    GITHUB_USER = st.secrets["GITHUB_USER"]

    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    # ------------------------------
    # UPLOAD arquivo JSON do cliente
    # ------------------------------
    url_json = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/clientes/{json_name}"

    content_b64 = base64.b64encode(
        json.dumps(data, indent=2, ensure_ascii=False).encode()
    ).decode()

    get_json = requests.get(url_json, headers=headers)
    sha_json = get_json.json().get("sha") if get_json.status_code == 200 else None

    payload_json = {"message": f"Atualizando catálogo do cliente {cliente}", "content": content_b64}
    if sha_json:
        payload_json["sha"] = sha_json

    resp_json = requests.put(url_json, headers=headers, json=payload_json)

    if resp_json.status_code in [200, 201]:
        st.success("🎉 Catálogo enviado ao GitHub!")
    else:
        st.error("❌ Erro ao enviar catálogo")
        st.code(resp_json.text)

    # ------------------------------
    # UPLOAD database.json
    # ------------------------------
    db_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/database/database.json"

    with open(PRODUTOS_FILE, "r", encoding="utf-8") as f:
        db_content = f.read()

    db_b64 = base64.b64encode(db_content.encode()).decode()

    db_get = requests.get(db_url, headers=headers)
    db_sha = db_get.json().get("sha") if db_get.status_code == 200 else None

    db_payload = {"message": "Atualizando database.json", "content": db_b64}
    if db_sha:
        db_payload["sha"] = db_sha

    db_resp = requests.put(db_url, headers=headers, json=db_payload)

    if db_resp.status_code in [200, 201]:
        st.success("📘 database.json atualizado!")
    else:
        st.error("Erro ao enviar database.json")
        st.code(db_resp.text)

    # ------------------------------
    # UPLOAD das imagens dos PRODUTOS NOVOS
    # ------------------------------
    for item in st.session_state.produtos_novos:
        img_filename = item["img_filename"]
        img_path = item["img_path"]

        img_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/imagens/{img_filename}"

        with open(img_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode()

        img_get = requests.get(img_url, headers=headers)
        img_sha = img_get.json().get("sha") if img_get.status_code == 200 else None

        img_payload = {"message": f"Enviando imagem {img_filename}", "content": img_b64}
        if img_sha:
            img_payload["sha"] = img_sha

        img_resp = requests.put(img_url, headers=headers, json=img_payload)

        if img_resp.status_code in [200, 201]:
            st.success(f"📸 Imagem enviada: {img_filename}")
        else:
            st.error(f"Erro ao enviar {img_filename}")
            st.code(img_resp.text)

    st.success("🎯 Catálogo completo enviado ao GitHub!")

    # RESET
    st.session_state.reset = True
    st.rerun()
