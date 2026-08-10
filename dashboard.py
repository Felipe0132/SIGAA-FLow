import get_data_sigaa as get_sigaa
import requests
import streamlit as st
import math

st.set_page_config(page_title="SIGAA Dashboard", page_icon="📚", layout="wide")


dados_login ={
    "user.login":st.session_state.usuario,
    "user.senha":st.session_state.senha
}

try:
    with st.spinner("Buscando dados do SIGAA..."):
        dados = get_sigaa.datas_sigaa(dados_login)

    st.title(f"Ola {dados["nome"]}!")
    st.caption(f"Saldo de recarga RU: **{dados['saldo']}**")
    st.divider()

   # st.write(dados)
    for materia_nome, materia in dados["data_materias"].items():
        with st.container(border=True):
            st.subheader(materia_nome)

            total_aulas = materia["total_aulas"]
            total_faltas = materia["total_faltas"]
            limite_faltas = math.floor(float(total_aulas * 0.25))
            restantes = limite_faltas - total_faltas
            percentual_usado = total_faltas / limite_faltas if limite_faltas else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("CH total", total_aulas)
            col2.metric("Nota total", materia["notas_atual"])
            col3.metric("Faltas restantes", f"{restantes:.1f}", delta=f"-{total_faltas} usadas", delta_color="inverse")
            st.progress(min(percentual_usado, 1.0), text=f"{total_faltas}/{limite_faltas:.0f} faltas usadas")

except requests.ConnectionError:
    st.error("Erro de conexao! Tente novamente para estabilizar a rede")