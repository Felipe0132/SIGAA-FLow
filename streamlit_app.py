import src.core.client as client
import streamlit as st

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "usuario" not in st.session_state:
    st.session_state.usuario = " "

if "senha" not in st.session_state:
    st.session_state.senha = " "

def login():
    st.title("Bem-vindo ao simplificador do SIGAA! 📚")
    st.caption("📋 Após o login, você verá suas **notas**, **faltas** (com alerta de risco) e **saldo do RU** de todas as matérias em um só lugar — sem precisar entrar no SIGAA.")

    dados_login = {
        'user.login': st.session_state.usuario,
        'user.senha': st.session_state.senha,
    }

    _, col_centro, _ = st.columns([1, 2, 1])
    with col_centro:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            enviado = st.form_submit_button("Enviar", use_container_width=True)

        if enviado:
            dados_login = {'user.login': usuario, 'user.senha': senha}

            with st.spinner("Verificando login..."):
                st.session_state.usuario = usuario
                st.session_state.senha = senha
                
                if client.teste_login(dados_login):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Login inválido!")

    st.write("")
    if st.button("Guia", help="Ver padrao esperado do SIGAA"):
        exibir_modal_instrucoes()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
)

if st.session_state.logged_in:
    pg = st.navigation([dashboard])
else:
    pg = st.navigation([login_page])

pg.run()