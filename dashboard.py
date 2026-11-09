import html
import math

import requests
import streamlit as st

import src.services.sigaa_service as sigaa_service


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


def formatar_nota(nota):
    if isinstance(nota, (int, float)):
        return f"{nota:.2f}"
    return str(nota) if nota is not None else "—"


def limite_de_faltas(total_aulas):
    return math.floor(float(total_aulas) * 0.25)


def exibir_cartao(materia_nome, materia):
    total_aulas = materia["total_aulas"]
    total_faltas = materia["total_faltas"]
    limite = limite_de_faltas(total_aulas)
    restantes = limite - total_faltas
    percentual_usado = total_faltas / limite if limite else 0
    percentual_usado = max(0, min(percentual_usado, 1.0))
    tarefas = materia.get("tarefas", {})

    with st.container(border=True):
        st.subheader(materia_nome)
        col1, col2, col3 = st.columns(3)
        col1.metric("CH total", total_aulas)
        col2.metric("Nota total", formatar_nota(materia.get("notas_atual")))
        col3.metric(
            "Faltas restantes",
            f"{restantes} aulas",
            delta=f"{total_faltas} usadas de {limite}",
            delta_color="inverse",
        )
        st.progress(percentual_usado, text=f"{total_faltas}/{limite} faltas usadas")

        if not tarefas:
            st.divider()
            st.caption("Nenhuma tarefa futura")
            return

        st.divider()
        st.markdown(f"**Tarefas futuras · {len(tarefas)}**")
        for nome_tarefa, info in tarefas.items():
            data_tarefa, enviada = info[0], info[1]
            cor = "#39765d" if enviada else "#a56816"
            status = "Enviada" if enviada else "Não enviada"
            col_tarefa, col_data, col_status = st.columns([3, 2, 1])
            with col_tarefa:
                st.markdown(
                    f"<div style='border-left:3px solid {cor};padding:6px 10px;"
                    f"border-radius:4px;background:rgba(90,130,125,.08)'>"
                    f"{html.escape(str(nome_tarefa))}</div>",
                    unsafe_allow_html=True,
                )
            with col_data:
                st.caption(data_tarefa)
            with col_status:
                st.markdown(f"<span style='color:{cor}'><b>{status}</b></span>", unsafe_allow_html=True)


try:
    dados_login = {
        "user.login": st.session_state.usuario,
        "user.senha": st.session_state.senha,
    }
    if "dados_sigaa" not in st.session_state:
        with st.spinner("Buscando dados do SIGAA..."):
            st.session_state.dados_sigaa = sigaa_service.datas_sigaa(dados_login)

    dados = st.session_state.dados_sigaa
    nome = " ".join(dados.get("nome", "Estudante").split())
    saldo = dados.get("saldo")
    materias = dados.get("data_materias", {})
    try:
        valor_saldo = int(str(saldo).strip()) if saldo is not None else None
    except (TypeError, ValueError):
        valor_saldo = None
    saldo_display = f"{valor_saldo} vezes" if valor_saldo is not None else "Indisponível"

    st.markdown(
        """
        <style>
        .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
        [data-testid="stMetric"] {
            background: rgba(90, 130, 125, 0.08);
            padding: 0.8rem 1rem;
            border-radius: 12px;
        }
        [data-testid="stMetricLabel"] { color: #60716e; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_header, col_guia = st.columns([4, 1])
    with col_header:
        st.title(f"Olá, {nome} 👋")
        st.caption("Seu período acadêmico em um só lugar")
    with col_guia:
        st.write("")
        if st.button("Guia", help="Ver o padrão esperado do SIGAA"):
            exibir_modal_instrucoes()

    st.divider()
    total_tarefas = sum(len(materia.get("tarefas", {})) for materia in materias.values())
    resumo1, resumo2, resumo3 = st.columns(3)
    resumo1.metric("Disciplinas", len(materias))
    resumo2.metric("Tarefas futuras", total_tarefas)
    resumo3.metric("Saldo RU", saldo_display)
    if valor_saldo is None:
        st.caption("Não foi possível localizar o saldo do RU no SIGAA.")

    st.subheader("Acompanhamento das disciplinas")
    modo = st.radio(
        "Visualização",
        ["Cartões", "Tabela"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if not materias:
        st.info("Nenhuma disciplina encontrada para exibir.")
    elif modo == "Tabela":
        linhas = []
        for materia_nome, materia in materias.items():
            limite = limite_de_faltas(materia["total_aulas"])
            linhas.append(
                {
                    "Matéria": materia_nome,
                    "CH total": materia["total_aulas"],
                    "Nota": formatar_nota(materia.get("notas_atual")),
                    "Faltas (usadas/limite)": f"{materia['total_faltas']}/{limite}",
                }
            )
        st.caption("Faltas exibidas como quantidade usada / limite estimado (por exemplo, 7/8).")
        st.dataframe(linhas, hide_index=True, use_container_width=True)
    else:
        for materia_nome, materia in materias.items():
            exibir_cartao(materia_nome, materia)

except requests.Timeout:
    st.error("O SIGAA demorou para responder. Tente carregar os dados novamente.")
    if st.button("Tentar novamente"):
        st.session_state.pop("dados_sigaa", None)
        st.rerun()
except requests.ConnectionError:
    st.error("Não foi possível conectar ao SIGAA. Verifique sua internet e tente novamente.")
    if st.button("Tentar novamente"):
        st.session_state.pop("dados_sigaa", None)
        st.rerun()
except requests.HTTPError:
    st.error("O SIGAA retornou um erro ao carregar os dados. Tente novamente mais tarde.")
except requests.RequestException:
    st.error("Ocorreu um problema de comunicação com o SIGAA. Tente novamente mais tarde.")
except Exception:
    st.error("Não foi possível interpretar os dados retornados pelo SIGAA. A estrutura do portal pode ter mudado.")
