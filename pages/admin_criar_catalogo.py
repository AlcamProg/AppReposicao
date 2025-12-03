import streamlit as st
import json
import os
from PIL import Image

# ===========================
# CONFIGURAÇÕES
# ===========================
st.set_page_config(page_title="Criar Catálogo", page_icon="📘")

PASSWORD = "SV2024"

# Caminhos dos arquivos
PRODUTOS_FILE = "clientes/database.json"
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
# AUTENTICAÇÃO
# ===========================
st.title("🔐 Área Restrita")
senha = st.text_input("Digite a senha:", type="password")

if senha != PASSWORD:
    st.warning("Informe a senha correta.")
    st.stop()

# ===========================
# FORMULÁRIO CLIENTE
# ===========================
st.title("📘 Criar Catálogo")

cliente = st.text_input("Nome do Cliente")
vendedor = st.text_input("Nome do Vendedor")
contato = st.text_input("Contato do Vendedor")

st.subheader("🔧 Adicionar Peças ao Catálogo")

# Sessão de peças do cliente
if "pecas_cliente" not in st.session_state:
    st.session_state.pecas_cliente = []

# Carregar base de produtos
produtos = carregar_produtos()

# Formulário para buscar/cadastrar produto
codigo_busca = st.text_input("Código da Peça")

if st.button("🔍 Buscar peça por código"):
    if not codigo_busca:
        st.error("Digite um código!")
    else:
        produto = buscar_produto_por_codigo(produtos, codigo_busca)

        if produto:
            st.success(f"Produto encontrado: {produto['nome']}")
            #st.image(produto["imagem"], width=150)
            st.session_state.pecas_cliente.append(produto)
        else:
            st.warning("Produto não encontrado. Cadastre abaixo.")

# ===========================
# FORMULÁRIO DE NOVO PRODUTO (SE NÃO EXISTIR)
# ===========================
st.markdown("### ➕ Cadastrar Novo Produto")

nome_novo = st.text_input("Nome da Nova Peça")
descricao_novo = st.text_area("Descrição da Nova Peça")
upload_novo = st.file_uploader("Imagem da Nova Peça", type=["png", "jpg", "jpeg"])

if st.button("💾 Salvar Novo Produto"):
    if not codigo_busca:
        st.error("Digite o CÓDIGO do novo produto acima.")
    elif not nome_novo or not descricao_novo or upload_novo is None:
        st.error("Preencha todos os campos e envie uma imagem!")
    else:
        # Salvar imagem
       # ext = upload_novo.name.split(".")[-1]
        #nome_img = f"{codigo_busca}.{ext}"
        #caminho_img = os.path.join(IMAGENS_DIR, nome_img)

        #img = Image.open(upload_novo)
        #img.save(caminho_img)

        novo_produto = {
            "codigo": codigo_busca,
            "nome": nome_novo,
            "descricao": descricao_novo,
            #"imagem": caminho_img.replace("\\", "/")
        }

        produtos.append(novo_produto)
        salvar_produtos(produtos)

        st.session_state.pecas_cliente.append(novo_produto)

        st.success("Produto cadastrado e adicionado ao catálogo!")
        #st.image(novo_produto["imagem"], width=150)

# ===========================
# EXIBIR PEÇAS DO CLIENTE
# ===========================
st.markdown("### 📄 Peças adicionadas ao catálogo do cliente")

for i, p in enumerate(st.session_state.pecas_cliente):
    st.write(f"**{i+1}. {p['nome']}** — {p['codigo']}")
    st.write(p["descricao"])
    #st.image(p["imagem"], width=120)
    st.write("---")

# ===========================
# SALVAR CATÁLOGO DO CLIENTE
# ===========================
if st.button("📁 Salvar Catálogo do Cliente"):
    if not cliente or not vendedor or not contato:
        st.error("Preencha os dados do cliente!")
    elif len(st.session_state.pecas_cliente) == 0:
        st.error("Adicione ao menos uma peça!")
    else:
        data = {
            "cliente": cliente,
            "vendedor": vendedor,
            "contato": contato,
            "pecas": st.session_state.pecas_cliente
        }

        filename = f"{CLIENTES_DIR}/{cliente.replace(' ', '_').lower()}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        st.success(f"Catálogo salvo: {filename}")
