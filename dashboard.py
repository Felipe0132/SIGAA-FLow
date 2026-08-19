import src.services.sigaa_service as sigaa_service
import requests
import streamlit as st
import math

st.set_page_config(page_title="SIGAA Dashboard", page_icon="📚", layout="wide")

CAMINHO_IMAGEM_NOTAS = "assets/images/padrao_notas.png"
CAMINHO_IMAGEM_FALTAS = "assets/images/padrao_frequencia.png"

@st.dialog("📋 Guia de Padrão do SIGAA")
def exibir_modal_instrucoes():
    st.write(
        "Certifique-se de que a estrutura das páginas no seu SIGAA corresponde ao padrão abaixo para que o sistema extraia os dados corretamente:"
    )

    st.subheader("1. Tela de Notas e Situação")
    st.caption("Deve exibir o nome do aluno e o resultado final da disciplina.")
    st.image(CAMINHO_IMAGEM_NOTAS, use_container_width=True)

    st.divider()

    st.subheader("2. Tela de Diário de Classe / Frequência")
    st.caption("Deve conter a tabela detalhada com as presenças e faltas por data.")
    st.image(CAMINHO_IMAGEM_FALTAS, use_container_width=True)



dados_login ={
    "user.login":st.session_state.usuario,
    "user.senha":st.session_state.senha
}

try:
    if "dados_sigaa" not in st.session_state:
        with st.spinner("Buscando dados do SIGAA..."):
            st.session_state.dados_sigaa = sigaa_service.datas_sigaa(dados_login)

    dados = st.session_state.dados_sigaa

    nome = dados.get('nome', 'Estudante')
    saldo = dados.get('saldo', 'R$ 0,00')
    materias = dados['data_materias']

    col_header, col_botoes = st.columns([3, 1])

    with col_header:
        nome_limpo = " ".join(nome.split())
        st.title(f"Ola {nome_limpo}!")
        
        valor = int(saldo)
        st.write(f"Saldo de recarga RU:  {f':red[**{valor}**]' if valor <= 0 else f'**{valor}**'}")

    with col_botoes:
        st.write("")
        if st.button("Guia", help="Ver padrao esperado do SIGAA"):
            exibir_modal_instrucoes()

    st.divider()

    if not materias:
        st.info("Nenhuma disciplina encontrada para exibir.")

   # st.write(dados)
    for materia_nome, materia in materias.items():
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
            col3.metric(
                "Faltas restantes",
                f"{restantes} aulas",
                delta=f"-{total_faltas} usadas",
                delta_color="inverse",
            )
            st.progress(min(percentual_usado, 1.0), text=f"{total_faltas}/{limite_faltas:.0f} faltas usadas")

except requests.ConnectionError:
    st.error("Erro de conexao! Tente novamente para estabilizar a rede")
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {e}")