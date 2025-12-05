import streamlit as st
import json
import os
from PIL import Image

# ===========================
# CONFIGURAÇÕES
# ===========================
st.set_page_config(page_title="Criar Catálogo", page_icon="📘")

PASSWORD = st.secrect("ADMIN_PASSWORD")

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
# CONTROLE DE LOGIN
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
# INICIALIZAR VARIÁVEIS DE ESTADO SEGURAS
# ===========================
defaults = {
    "cliente": "",
    "vendedor": "",
    "contato": "",
    "codigo_busca": "",
    "nome_novo": "",
    "descricao_novo": "",
    "pecas_cliente": [],
    "reset": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ===========================
# FUNÇÃO PARA LIMPAR FORMULÁRIO
# ===========================
def reset_form():
    for key in defaults:
        if key not in ["pecas_cliente"]:  # lista deve ser resetada separadamente
            st.session_state[key] = ""
    st.session_state.pecas_cliente = []
    st.session_state.reset = False
    st.rerun()

# Quando salvar, ativa reset
if st.session_state.reset:
    reset_form()

# ===========================
# ÁREA PRINCIPAL
# ===========================
st.title("📘 Criar Catálogo")

# FORMULÁRIO CLIENTE
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

# ===========================
# CADASTRAR NOVO PRODUTO
# ===========================
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

        st.success("Produto cadastrado e adicionado ao catálogo!")

# ===========================
# PEÇAS ADICIONADAS
# ===========================
st.markdown("### 📄 Peças adicionadas ao catálogo")

for i, p in enumerate(st.session_state.pecas_cliente):
    st.write(f"**{i+1}. {p['nome']}** — {p['codigo']}")
    st.write(p["descricao"])
    st.write("---")

# ===========================
# SALVAR CATÁLOGO DO CLIENTE
# ===========================
# ===========================
# SALVAR CATÁLOGO DO CLIENTE
# ===========================
if st.button("📁 Salvar Catálogo do Cliente"):
    if not cliente or not vendedor or not contato:
        st.error("Preencha os dados do cliente!")
    elif len(st.session_state.pecas_cliente) == 0:
        st.error("Adicione ao menos uma peça!")
    else:
        # Montar JSON
        data = {
            "cliente": cliente,
            "vendedor": vendedor,
            "contato": contato,
            "pecas": st.session_state.pecas_cliente
        }

        json_name = f"{cliente.replace(' ', '_').lower()}.json"
        json_path_local = f"{CLIENTES_DIR}/{json_name}"

        # Salva localmente (opcional mas útil no dev)
        with open(json_path_local, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        st.success("Catálogo salvo localmente!")

        # =====================================================
        # ENVIA PARA O GITHUB (DEPLOY AUTOMÁTICO)
        # =====================================================
        import base64, requests

        GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
        GITHUB_REPO = st.secrets["GITHUB_REPO"]

        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/clientes/{json_name}"

        # Codifica o JSON em base64
        content_b64 = base64.b64encode(
            json.dumps(data, indent=2, ensure_ascii=False).encode()
        ).decode()

        # Verifica se arquivo existe para pegar o SHA
        get_file = requests.get(url, headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}"
        })

        sha = get_file.json().get("sha") if get_file.status_code == 200 else None

        payload = {
            "message": f"Atualizando catálogo do cliente {cliente}",
            "content": content_b64
        }

        if sha:
            payload["sha"] = sha

        response = requests.put(
            url,
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            json=payload
        )

        if response.status_code in [200, 201]:
            st.success("🎉 Catálogo enviado ao GitHub com sucesso!")
            st.info("O Streamlit Cloud fará o deploy automaticamente em alguns segundos.")
        else:
            st.error("❌ Falha ao enviar ao GitHub!")
            st.code(response.text)

        # Reseta formulário
        st.session_state.reset = True
        st.rerun()

