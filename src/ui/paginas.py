"""Telas do app. Cada função é uma página registrada em streamlit_app.py."""

from pathlib import Path

import requests
import streamlit as st

import src.core.client as client
from src.ui import componentes as ui
from src.ui import dados
from src.ui import formato as fmt

RAIZ = Path(__file__).resolve().parents[2]
IMAGEM_NOTAS = RAIZ / "assets/images/padrao_notas.png"
IMAGEM_FREQUENCIA = RAIZ / "assets/images/padrao_frequencia.png"


def topo(titulo, sobretitulo=None, subtitulo=None):
    esquerda, direita = st.columns([4, 1.4], vertical_alignment="bottom")
    with esquerda:
        ui.cabecalho(titulo, sobretitulo, subtitulo)
    with direita:
        with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center", gap="small"):
            atualizado = st.session_state.get("atualizado_em")
            if atualizado:
                st.caption(f"Atualizado às {fmt.hora(atualizado)}")
            if st.button("Atualizar", icon=":material/refresh:", help="Buscar os dados de novo no SIGAA"):
                dados.recarregar()
    st.write("")


# ---------- guia ----------

def conteudo_guia():
    st.markdown("#### Como os números são calculados")
    st.markdown(
        "- **Faltas:** o limite é 25% do total de aulas registradas, arredondado para baixo. "
        "Com 32 aulas, por exemplo, você pode faltar 8.\n"
        "- **Pontos:** soma das notas que o professor já lançou. O app não sabe quantos pontos "
        "ainda serão distribuídos, então 42 pontos não quer dizer que você está abaixo da média.\n"
        "- **Entregas:** tarefas do SIGAA com prazo ainda aberto. Tarefas vencidas não aparecem."
    )
    st.markdown("#### Páginas que o app precisa ler")
    st.caption("Se o seu SIGAA mostrar estas páginas com outra estrutura, algum dado pode não aparecer.")
    with st.container(border=True):
        st.markdown("**1. Notas da turma**")
        st.caption("Tabela de alunos com seu nome, as colunas de notas e o resultado.")
        st.image(str(IMAGEM_NOTAS), width="stretch")
    with st.container(border=True):
        st.markdown("**2. Frequência**")
        st.caption("Tabela com as colunas Data e Situação, aula por aula.")
        st.image(str(IMAGEM_FREQUENCIA), width="stretch")


@st.dialog("Como o app lê o SIGAA", width="large")
def dialogo_guia():
    conteudo_guia()


def guia():
    topo("Guia", subtitulo="De onde vêm os números e o que o app precisa encontrar no SIGAA.")
    conteudo_guia()


# ---------- login ----------

def login():
    # Sem navegação no login: some com a sidebar que sobra depois de sair.
    st.html('<style>[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],'
            '[data-testid="stExpandSidebarButton"] { display: none; }</style>')
    st.write("")
    esquerda, direita = st.columns([1.1, 1], gap="large", vertical_alignment="center")
    with esquerda:
        ui.render(
            f'<div class="sf-hero">{ui.marca(invertido=True)}'
            "<h1>Seu semestre inteiro, sem abrir o SIGAA.</h1>"
            "<p>Notas, faltas, prazos de tarefas e saldo do RU de todas as disciplinas, numa tela só.</p>"
            '<div class="sf-preview">'
            f'<div class="sf-preview-row">{ui.ico("event_busy")}<span class="lbl">Faltas em Cálculo II</span><b>6 de 8</b></div>'
            f'<div class="sf-preview-row">{ui.ico("assignment")}<span class="lbl">Próxima entrega</span><b>amanhã, 23h59</b></div>'
            f'<div class="sf-preview-row">{ui.ico("restaurant")}<span class="lbl">Saldo do RU</span><b>14 refeições</b></div>'
            "</div>"
            '<div class="sf-hero-foot">Projeto de estudantes, sem vínculo oficial com o SIGAA.</div></div>'
        )
    with direita:
        _, centro, _ = st.columns([0.08, 1, 0.08])
        with centro:
            ui.render(
                '<div class="sf-login-head"><h2>Entrar</h2>'
                "<p>Use o mesmo usuário e senha do SIGAA.</p></div>"
            )
            with st.form("form_login", border=False):
                usuario = st.text_input("Usuário", placeholder="seu usuário do SIGAA", autocomplete="username")
                senha = st.text_input("Senha", type="password", placeholder="••••••••", autocomplete="current-password")
                enviado = st.form_submit_button("Entrar", type="primary", width="stretch")

            if enviado:
                _tentar_login(usuario.strip(), senha)

            ui.render(
                f'<div class="sf-note">{ui.ico("lock")}<span>A senha fica só nesta sessão do navegador, '
                "não é gravada em lugar nenhum e é apagada quando você sai.</span></div>"
            )
            st.write("")
            if st.button("Como o app lê o SIGAA", icon=":material/help:", type="tertiary"):
                dialogo_guia()


def _tentar_login(usuario, senha):
    if not usuario or not senha:
        st.warning("Preencha usuário e senha.", icon=":material/info:")
        return
    with st.spinner("Conferindo com o SIGAA…"):
        try:
            ok = client.teste_login({"user.login": usuario, "user.senha": senha})
        except requests.Timeout:
            st.error("O SIGAA demorou demais para responder. Tente de novo.", icon=":material/cloud_off:")
            return
        except requests.ConnectionError:
            st.error("Não deu para conectar ao SIGAA. Confira sua internet.", icon=":material/cloud_off:")
            return
        except requests.RequestException:
            st.error("O SIGAA respondeu algo inesperado. Tente mais tarde.", icon=":material/cloud_off:")
            return
    if not ok:
        st.error("Usuário ou senha não conferem com o SIGAA.", icon=":material/error:")
        return
    st.session_state.usuario = usuario
    st.session_state.senha = senha
    st.session_state.logged_in = True
    st.rerun()


def sair():
    dados.encerrar_sessao()


# ---------- painel ----------

def painel():
    agora = fmt.agora()
    brutos = dados.carregar()
    disciplinas = dados.disciplinas()
    entregas = [e for e in fmt.todas_entregas(disciplinas) if e.aberta]
    pendentes = [e for e in entregas if e.estado == "pendente"]

    topo(f"Olá, {fmt.primeiro_nome(brutos.get('nome'))}", sobretitulo=fmt.data_extensa(agora),
         subtitulo="Como está o seu período até agora.")

    ui.render(ui.kpis([_kpi_disciplinas(disciplinas), _kpi_frequencia(disciplinas),
                       _kpi_entrega(pendentes, agora), _kpi_ru(brutos.get("saldo"))]))
    st.write("")

    esquerda, direita = st.columns([1.45, 1], gap="medium")
    with esquerda:
        ui.render(ui.cartao("Frequência", ui.lista_frequencia(disciplinas), nota="limite de 25% das aulas"))
    with direita:
        nota = f"{fmt.plural(len(pendentes), 'pendente', 'pendentes')}" if entregas else None
        ui.render(ui.cartao("Próximas entregas", ui.lista_entregas(entregas, agora, limite=6), nota=nota))
        if len(entregas) > 6:
            st.page_link(_PAGINAS["entregas"], label=f"Ver todas as {len(entregas)} entregas abertas", icon=":material/arrow_forward:")

    st.write("")
    ui.render(ui.cartao("Pontos acumulados", ui.grafico_pontos(disciplinas),
                        nota=f"soma das notas lançadas · média {fmt.MEDIA_APROVACAO}"))


def _kpi_disciplinas(disciplinas):
    aulas = sum(d.aulas for d in disciplinas)
    return ui.kpi("Disciplinas", str(len(disciplinas)), f"{fmt.plural(aulas, 'aula registrada', 'aulas registradas')} no período", "school")


def _kpi_frequencia(disciplinas):
    alerta = [d for d in disciplinas if d.situacao.nivel in ("risco", "atencao")]
    if not alerta:
        return ui.kpi("Frequência", "Em dia", "Todas as disciplinas com folga de faltas", "verified", "ok")
    pior = alerta[0]
    tom = "bad" if pior.situacao.nivel == "risco" else "warn"
    valor = f"{len(alerta)}<small>em alerta</small>"
    return ui.kpi("Frequência", valor, f"{pior.nome}: {fmt.texto_folga(pior.situacao)}", "event_busy", tom)


def _kpi_entrega(pendentes, agora):
    futuras = [e for e in pendentes if e.quando]
    if not futuras:
        return ui.kpi("Próxima entrega", "—", "Nenhuma tarefa pendente", "assignment", "ok")
    e = futuras[0]
    dias = (e.quando.date() - agora.date()).days
    valor = "Hoje" if dias <= 0 else "Amanhã" if dias == 1 else f"{dias}<small>dias</small>"
    tom = "bad" if (e.quando - agora).total_seconds() < 24 * 3600 else ""
    return ui.kpi("Próxima entrega", valor, f"{e.titulo} · até {fmt.hora(e.quando)}", "assignment", tom)


def _kpi_ru(saldo):
    valor = fmt.saldo_ru(saldo)
    if valor is None:
        return ui.kpi("Saldo do RU", "—", "O SIGAA não mostrou o saldo agora", "restaurant")
    unidade = "refeição" if valor == 1 else "refeições"
    return ui.kpi("Saldo do RU", f"{valor}<small>{unidade}</small>", "créditos no cartão do restaurante", "restaurant")


# ---------- disciplinas ----------

def disciplinas_tela():
    agora = fmt.agora()
    disciplinas = dados.disciplinas()
    topo("Disciplinas", subtitulo=f"{fmt.plural(len(disciplinas), 'turma', 'turmas')} neste período, "
                                  "as que mais preocupam primeiro. Clique numa para ver notas, aulas e entregas.")

    modo = st.segmented_control("Visualização", ["Cartões", "Tabela"], default="Cartões",
                                label_visibility="collapsed", key="modo_disciplinas") or "Cartões"
    if not disciplinas:
        ui.render(ui.vazio("school", "Nenhuma disciplina", "O SIGAA não retornou turmas para este período."))
    elif modo == "Tabela":
        _tabela_disciplinas(disciplinas)
    else:
        _cartoes_disciplinas(disciplinas, agora)


def _cartoes_disciplinas(disciplinas, agora):
    for inicio in range(0, len(disciplinas), 2):
        colunas = st.columns(2, gap="small")
        for coluna, (i, d) in zip(colunas, enumerate(disciplinas[inicio:inicio + 2], start=inicio)):
            with coluna, st.container(border=True, key=f"disc_{i}"):
                ui.render(ui.corpo_disciplina(d, agora))
                if st.button("Ver detalhes", key=f"ver_{i}", icon=":material/open_in_full:", width="stretch"):
                    abrir_detalhe(d, agora)


def abrir_detalhe(d, agora):
    def conteudo():
        ui.render(ui.resumo_detalhe(d))
        st.write("")
        aba_notas, aba_freq, aba_entregas = st.tabs([
            f"Notas · {sum(1 for a in d.avaliacoes if not a.subtotal and a.valor is not None)}",
            f"Frequência · {fmt.plural(d.faltas, 'falta', 'faltas')}",
            f"Entregas · {len(d.entregas)}",
        ])
        with aba_notas:
            ui.render(ui.notas_detalhe(d))
        with aba_freq:
            ui.render(ui.frequencia_detalhe(d))
        with aba_entregas:
            ui.render(ui.entregas_detalhe(d, agora))

    st.dialog(d.nome, width="large")(conteudo)()


def _tabela_disciplinas(disciplinas):
    linhas = [
        {
            "Disciplina": d.nome,
            "Situação": d.situacao.rotulo,
            "Pontos": d.pontos,
            "Faltas": d.faltas,
            "Limite": d.situacao.limite,
            "Uso do limite": round(d.situacao.uso * 100),
            "Aulas": d.aulas,
            "Entregas pendentes": len(d.pendentes),
        }
        for d in disciplinas
    ]
    st.dataframe(
        linhas,
        hide_index=True,
        width="stretch",
        column_config={
            "Disciplina": st.column_config.TextColumn(width="medium"),
            "Pontos": st.column_config.ProgressColumn(min_value=0, max_value=fmt.NOTA_MAXIMA, format="%g",
                                                      help="Soma das notas lançadas até agora"),
            "Uso do limite": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%",
                                                             help="Faltas usadas em relação ao limite de 25%"),
            "Faltas": st.column_config.NumberColumn(format="%d"),
            "Limite": st.column_config.NumberColumn(format="%d", help="25% das aulas, arredondado para baixo"),
        },
    )


# ---------- entregas ----------

def entregas_tela():
    agora = fmt.agora()
    entregas = fmt.todas_entregas(dados.disciplinas())
    grupos = {
        "Pendentes": [e for e in entregas if e.estado == "pendente"],
        "Enviadas": [e for e in entregas if e.estado == "enviada"],
        "Não enviadas": [e for e in entregas if e.estado == "perdida"],
        "Todas": entregas,
    }
    topo("Entregas", subtitulo=f"{fmt.plural(len(grupos['Pendentes']), 'pendente', 'pendentes')} · "
                               f"{fmt.plural(len(grupos['Enviadas']), 'enviada', 'enviadas')} · "
                               f"{fmt.plural(len(grupos['Não enviadas']), 'não enviada', 'não enviadas')}")

    filtro = st.segmented_control(
        "Filtro", list(grupos), default="Pendentes", label_visibility="collapsed", key="filtro_entregas",
        format_func=lambda nome: f"{nome} · {len(grupos[nome])}",
    ) or "Pendentes"
    st.write("")
    ui.render(ui.entregas_agrupadas(grupos[filtro], agora))


# ---------- navegação ----------

_PAGINAS = {}


def navegacao(logado):
    if not logado:
        # Links antigos (/disciplinas, /sair...) também caem no login, sem aviso de página inexistente.
        entrar = st.Page(login, title="Entrar", icon=":material/login:", url_path="entrar", default=True)
        atalhos = [st.Page(login, title="Entrar", url_path=caminho, visibility="hidden")
                   for caminho in ("painel", "disciplinas", "entregas", "guia", "sair")]
        return st.navigation([entrar, *atalhos], position="hidden")

    _PAGINAS.update(
        painel=st.Page(painel, title="Painel", icon=":material/space_dashboard:", url_path="painel", default=True),
        disciplinas=st.Page(disciplinas_tela, title="Disciplinas", icon=":material/school:", url_path="disciplinas"),
        entregas=st.Page(entregas_tela, title="Entregas", icon=":material/assignment:", url_path="entregas"),
        guia=st.Page(guia, title="Guia", icon=":material/help:", url_path="guia"),
        sair=st.Page(sair, title="Sair", icon=":material/logout:", url_path="sair"),
    )
    p = _PAGINAS
    return st.navigation({"": [p["painel"], p["disciplinas"], p["entregas"]], "Conta": [p["guia"], p["sair"]]})
