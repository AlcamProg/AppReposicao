import streamlit as st
import json
import os
from PIL import Image

st.set_page_config(page_title="Editar Catálogo", page_icon="📘")

CATALOGOS_DIR = "clientes"
IMAGENS_DIR = "imagens"
PRODUTOS_FILE = "database/database.json"

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
# Página
# --------------------------------------------------
st.header("🛠 Editar Catálogos Existentes")

# Verifica existência da pasta
if not os.path.exists(CATALOGOS_DIR):
    st.warning(f"A pasta '{CATALOGOS_DIR}' não existe.")
    st.stop()

arquivos = [f for f in os.listdir(CATALOGOS_DIR) if f.endswith(".json")]
if len(arquivos) == 0:
    st.warning("Nenhum catálogo encontrado na pasta.")
    st.stop()

nome_catalogo = st.selectbox("Selecione um catálogo:", arquivos)
caminho_catalogo = os.path.join(CATALOGOS_DIR, nome_catalogo)

# Carregar catálogo
catalogo = carregar_catalogo(caminho_catalogo)

if "pecas" not in catalogo:
    st.error("Esse catálogo não possui o formato esperado (sem 'pecas').")
    st.stop()

catalogo.setdefault("cliente", "")

# Campo de edição do nome do cliente (precisa salvar explicitamente)
cliente_edit = st.text_input("Nome do cliente:", value=catalogo["cliente"])

st.markdown("---")
st.subheader("Peças do catálogo")

# Lista para armazenar índices a remover
remover_indices = []

# Itera pelas peças e cria um form por peça
for i, p in enumerate(catalogo["pecas"]):
    # Expander para organizar visualmente
    with st.expander(f"{p.get('nome', 'Sem nome')} — {p.get('codigo', '')}", expanded=False):
        # Form para confirmar alterações ou remover
        form_key = f"form_peca_{i}"
        with st.form(key=form_key):
            nome_input = st.text_input("Nome:", value=p.get("nome", ""), key=f"nome_{i}")
            desc_input = st.text_area("Descrição:", value=p.get("descricao", ""), key=f"desc_{i}")

            st.write("Imagem atual:")
            imagem_atual = p.get("imagem", None)
            if imagem_atual and os.path.exists(imagem_atual):
                st.image(imagem_atual, width=200)
            else:
                st.info("Nenhuma imagem cadastrada para esta peça.")

            nova_img = st.file_uploader("Nova imagem (opcional)", type=["png", "jpg", "jpeg"], key=f"img_{i}")

            # Dois botões de submit no mesmo form — apenas o pressionado volta True
            confirmar = st.form_submit_button("Confirmar alterações")
            remover = st.form_submit_button("Remover peça")

            # Ação de remoção (marcar para remover depois)
            if remover:
                # marca índice para remoção (remoção após o loop)
                remover_indices.append(i)
                st.success("Peça marcada para remoção. Clique em 'Salvar catálogo' para confirmar.")
                # força rerun para mostrar que operação foi registrada
                st.experimental_rerun()

            # Ação de confirmar alterações
            if confirmar:
                # atualiza nome e descrição no objeto do catálogo
                catalogo["pecas"][i]["nome"] = nome_input
                catalogo["pecas"][i]["descricao"] = desc_input

                # se houver nova imagem, salva e atualiza o path
                if nova_img is not None:
                    ext = nova_img.name.split(".")[-1].lower()
                    if ext == "jpeg":
                        ext = "jpg"
                    img_filename = f"{p.get('codigo', i)}.{ext}"
                    img_path = os.path.join(IMAGENS_DIR, img_filename)

                    # garante diretório
                    os.makedirs(IMAGENS_DIR, exist_ok=True)

                    image = Image.open(nova_img)
                    image.save(img_path)

                    catalogo["pecas"][i]["imagem"] = f"{IMAGENS_DIR}/{img_filename}"

                st.success("Alterações aplicadas localmente. Clique em 'Salvar catálogo' para gravar no arquivo.")
                # rerun para atualizar visual com novas informações
                st.experimental_rerun()

# Após iterar, remover índices (se houver)
if remover_indices:
    # remove em ordem decrescente para manter índices corretos
    for idx in sorted(remover_indices, reverse=True):
        # antes de remover, tenta também remover a imagem associada (opcional)
        p_to_remove = catalogo["pecas"][idx]
        img_path = p_to_remove.get("imagem")
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception:
                # se falhar, apenas continue — não bloqueia
                pass
        catalogo["pecas"].pop(idx)
    st.success("Peças removidas localmente. Clique em 'Salvar catálogo' para gravar no arquivo.")
    st.experimental_rerun()

st.markdown("---")
st.subheader("Adicionar nova peça ao catálogo")

# Inputs para nova peça (usar keys únicas)
codigo_novo = st.text_input("Código da peça (nova):", key="codigo_novo")
nome_novo = st.text_input("Nome da peça (nova):", key="nome_novo")
desc_novo = st.text_area("Descrição (nova):", key="desc_novo")
img_nova = st.file_uploader("Imagem (nova):", type=["png", "jpg", "jpeg"], key="img_nova")

if st.button("Adicionar peça"):
    if not codigo_novo or not nome_novo or not img_nova:
        st.error("Preencha todos os campos e envie uma imagem.")
    else:
        ext = img_nova.name.split(".")[-1].lower()
        if ext == "jpeg":
            ext = "jpg"

        img_filename = f"{codigo_novo}.{ext}"
        img_path = os.path.join(IMAGENS_DIR, img_filename)

        os.makedirs(IMAGENS_DIR, exist_ok=True)

        image = Image.open(img_nova)
        image.save(img_path)

        nova_peca = {
            "codigo": codigo_novo,
            "nome": nome_novo,
            "descricao": desc_novo,
            "imagem": f"{IMAGENS_DIR}/{img_filename}"
        }

        catalogo["pecas"].append(nova_peca)
        st.success("Peça adicionada com sucesso! Clique em 'Salvar catálogo' para gravar no arquivo.")
        st.experimental_rerun()

st.markdown("---")

# Botão final para salvar todas as alterações no arquivo JSON
if st.button("💾 Salvar catálogo"):
    catalogo["cliente"] = cliente_edit
    salvar_catalogo(caminho_catalogo, catalogo)
    st.success("Catálogo atualizado com sucesso!")
    st.experimental_rerun()
