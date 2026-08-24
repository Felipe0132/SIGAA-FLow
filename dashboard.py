import src.services.sigaa_service as sigaa_service
import requests
import streamlit as st
import math

st.set_page_config(page_title="SIGAA Dashboard", page_icon="📚", layout="wide")

CAMINHO_IMAGEM_NOTAS = "assets/images/padrao_notas.png"
CAMINHO_IMAGEM_FALTAS = "assets/images/padrao_frequencia.png"

@st.dialog("Guia de Padrão do SIGAA")
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
        st.title(f"Olá {nome_limpo}!")
        
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
            tarefas_abt = materia["tarefas"]
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

            if tarefas_abt:
                st.divider()
                st.markdown(
                    f"<span style='color:#FFA726; font-size:1rem; font-weight:bold;'>Tarefas em aberto &nbsp;({len(tarefas_abt)})</span>",
                    unsafe_allow_html=True
                )
                for nome_tarefa, info in tarefas_abt.items():
                    data_tarefa, enviada = info[0], info[1]

                    if enviada:
                        cor_borda  = "#4CAF50"
                        cor_fundo  = "#4CAF5022"
                        cor_texto  = "#81C784"
                        status_txt = "Enviada"
                        cor_status = "#4CAF50"
                    else:
                        cor_borda  = "#FFA726"
                        cor_fundo  = "#FFA72622"
                        cor_texto  = "#FFC85C"
                        status_txt = "Não enviada"
                        cor_status = "#FFA726"

                    col_tarefa, col_data, col_status = st.columns([3, 2, 1])
                    with col_tarefa:
                        st.markdown(
                            f"<div style='background-color:{cor_fundo}; border-left: 3px solid {cor_borda}; padding: 6px 10px; border-radius: 4px; color:{cor_texto};'>{nome_tarefa}</div>",
                            unsafe_allow_html=True
                        )
                    with col_data:
                        st.markdown(
                            f"<div style='color:{cor_borda}; font-size:0.82rem; padding-top:8px;'>{data_tarefa}</div>",
                            unsafe_allow_html=True
                        )
                    with col_status:
                        st.markdown(
                            f"<div style='color:{cor_status}; font-size:0.82rem; padding-top:8px; font-weight:bold;'>{status_txt}</div>",
                            unsafe_allow_html=True
                        )
            else:
                st.divider()
                st.caption("Nenhuma tarefa em aberto")

except requests.ConnectionError:
    st.error("Erro de conexao! Tente novamente para estabilizar a rede")
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {e}")