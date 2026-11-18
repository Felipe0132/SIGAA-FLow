import streamlit as st

from src.ui import componentes as ui
from src.ui import dados
from src.ui import paginas
from src.ui.tema import aplicar_estilo

st.set_page_config(page_title="SIGAA Flow", page_icon=":material/waves:", layout="wide")
aplicar_estilo()

logado = st.session_state.get("logged_in", False)
navegacao = paginas.navegacao(logado)

if logado and navegacao.url_path != "sair":
    brutos = dados.carregar()
    with st.sidebar:
        st.html(f'<div class="sf">{ui.usuario(brutos.get("nome"))}</div>')

navegacao.run()
