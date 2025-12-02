import streamlit as st
import json
import os
from PIL import Image

# -----------------------------------------------------------
# 1. Proteção por rota secreta
# -----------------------------------------------------------
params = st.query_params

if params.get("admin") != "criar":
    st.error("Acesso restrito. Esta página é exclusiva para administradores.")
    st.stop()

st.title("📘 Criar novo catálogo de cliente")


# -----------------------------------------------------------
# 2. Formulário básico do catálogo
# -----------------------------------------------------------

st.subheader("Informações do Cliente")

cliente = st.text_input("Nome do Cliente (ex: Cliente A)")
vendedor = st.text_input("Nome do Vendedor")
contato_vendedor = st.text_input("Número do WhatsApp do vendedor (ex: 5515999999999)")


# -----------------------------------------------------------
# 3. Cadastro das Peças
# -----------------------------------------------------------

st.subheader("📦 Peças do Catálogo")

# Guarda lista de peças
if "pecas_temp" not in st.session_state:
    st.session_state.pecas_temp = []

with st.form("form_peca"):
    st.write("### Adicionar nova peça")

    nome_peca = st.text_input("Nome da peça")
    codigo_peca = st.text_input("Código da peça")
    descricao_peca = st.text_area("Descrição da peça")

    imagem_peca = st.file_uploader("Imagem da peça", type=["png", "jpg", "jpeg"])

    adicionar = st.form_submit_button("Adicionar peça")

    if adicionar:
        if nome_peca == "" or codigo_peca == "" or descricao_peca == "":
            st.error("Preencha todos os campos da peça antes de adicionar.")
        else:
            st.session_state.pecas_temp.append({
                "nome": nome_peca,
                "codigo": codigo_peca,
                "descricao": descricao_peca,
                "imagem_file": imagem_peca  # guardamos o arquivo para salvar depois
            })
            st.success(f"Peça '{nome_peca}' adicionada!")


# -----------------------------------------------------------
# 4. Mostrar peças adicionadas
# -----------------------------------------------------------

st.write("### 📝 Peças cadastradas até agora:")

for p in st.session_state.pecas_temp:
    st.write(f"**{p['nome']}** — {p['codigo']}")
    st.write(p["descricao"])
    if p["imagem_file"] is not None:
        st.image(p["imagem_file"], width=150)


# -----------------------------------------------------------
# 5. Salvar o catálogo final
# -----------------------------------------------------------

if st.button("💾 Salvar Catálogo"):

    if cliente == "" or vendedor == "" or contato_vendedor == "":
        st.error("Preencha todas as informações do cliente antes de salvar.")
        st.stop()

    if len(st.session_state.pecas_temp) == 0:
        st.error("Adicione pelo menos uma peça.")
        st.stop()

    # Criar pastas se não existirem
    os.makedirs("catalogos", exist_ok=True)
    os.makedirs("imagens", exist_ok=True)

    lista_pecas_json = []

    # Salvar imagens e montar JSON
    for p in st.session_state.pecas_temp:
        nome_img = f"{p['codigo']}.jpg"
        caminho_img = os.path.join("imagens", nome_img)

        if p["imagem_file"] is not None:
            img = Image.open(p["imagem_file"])
            img.save(caminho_img)

        lista_pecas_json.append({
            "nome": p["nome"],
            "codigo": p["codigo"],
            "descricao": p["descricao"],
            "imagem": caminho_img.replace("\\", "/")
        })

    # Montar JSON final
    catalogo = {
        "cliente": cliente,
        "vendedor": vendedor,
        "contato_vendedor": contato_vendedor,
        "pecas": lista_pecas_json
    }

    # Salvar arquivo JSON
    nome_arquivo = f"catalogos/{cliente.lower().replace(' ', '_')}.json"

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)

    st.success(f"Catálogo do cliente '{cliente}' salvo com sucesso!")
    st.info(f"Arquivo criado: {nome_arquivo}")
