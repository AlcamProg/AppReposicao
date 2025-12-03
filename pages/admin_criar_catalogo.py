import streamlit as st
import json
import os
from PIL import Image

# ===========================
# AUTENTICAÇÃO POR SENHA
# ===========================
st.set_page_config(page_title="Criar Catálogo", page_icon="🔐")

PASSWORD = "SV2024"  # Troque se quiser

st.title("🔐 Área Restrita")

senha = st.text_input("Digite a senha para continuar:", type="password")

if senha != PASSWORD:
    st.warning("Área restrita. Informe a senha correta.")
    st.stop()

# ===========================
# FORMULÁRIO DO CATÁLOGO
# ===========================

st.title("📘 Criar Catálogo")

# Dados gerais
st.subheader("📌 Dados do Cliente")

cliente = st.text_input("Nome do Cliente")
vendedor = st.text_input("Nome do Vendedor")
contato = st.text_input("Contato do Vendedor (ex: 5515999999999)")

# Lista de peças
st.subheader("🔧 Peças do Catálogo")

if "pecas" not in st.session_state:
    st.session_state.pecas = []

# Adicionar nova peça
st.markdown("### ➕ Adicionar nova peça")

nome_peca = st.text_input("Nome da Peça")
codigo_peca = st.text_input("Código da Peça")
descricao_peca = st.text_area("Descrição da Peça")

# UPLOAD DA IMAGEM
uploaded_image = st.file_uploader("Enviar imagem da peça", type=["png", "jpg", "jpeg"])



if st.button("Adicionar Peça"):
    if not nome_peca or not codigo_peca:
        st.error("Nome e código da peça são obrigatórios!")

    elif uploaded_image is None:
        st.error("Envie uma imagem para a peça!")

    else:
        # Criar diretório imagens se não existir
        os.makedirs("imagens", exist_ok=True)

        # Definir nome do arquivo final
        img_extension = uploaded_image.name.split(".")[-1]
        img_save_name = f"{nome_peca}.{img_extension}"
        img_path = os.path.join("imagens", img_save_name)

        # Salvar a imagem enviada
        image = Image.open(uploaded_image)
        image.save(img_path)

        # Registrar no catálogo
        nova_peca = {
            "nome": nome_peca,
            "codigo": codigo_peca,
            "descricao": descricao_peca,
            "imagem": img_path.replace("\\", "/")   # Normaliza caminho
        }

        st.session_state.pecas.append(nova_peca)
        st.success(f"Peça '{nome_peca}' adicionada com sucesso!")

# Exibir lista de peças adicionadas
st.markdown("### 📄 Peças já adicionadas")

if len(st.session_state.pecas) == 0:
    st.info("Nenhuma peça adicionada ainda.")
else:
    for i, p in enumerate(st.session_state.pecas):
        st.write(f"**{i+1}. {p['nome']}** — {p['codigo']}")
        st.write(f"Descrição: {p['descricao']}")
        st.write(f"Imagem salva em: `{p['imagem']}`")
        st.image(p["imagem"], width=150)
        st.write("---")

# ===========================
# SALVAR JSON
# ===========================

OUTPUT_DIR = "clientes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

if st.button("💾 Salvar Catálogo"):
    if not cliente or not vendedor or not contato:
        st.error("Cliente, vendedor e contato são obrigatórios!")
    elif len(st.session_state.pecas) == 0:
        st.error("Você precisa adicionar pelo menos uma peça!")
    else:
        data = {
            "cliente": cliente,
            "vendedor": vendedor,
            "contato_vendedor": contato,
            "pecas": st.session_state.pecas
        }

        filename = f"{OUTPUT_DIR}/{cliente.replace(' ', '_').lower()}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        st.success(f"Catálogo salvo com sucesso! Arquivo: {filename}")
