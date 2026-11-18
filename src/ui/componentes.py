"""Blocos de interface em HTML. Todo texto vindo do SIGAA passa por `esc`."""

import base64
import html

import streamlit as st

from src.ui import formato as fmt

ICONE_NIVEL = {"ok": "check_circle", "atencao": "warning", "risco": "report", "neutro": "remove"}


def esc(valor):
    return html.escape(str(valor), quote=True)


def ico(nome, fill=False):
    return f'<span class="sf-ico{" fill" if fill else ""}" aria-hidden="true">{nome}</span>'


def render(conteudo):
    st.html(f'<div class="sf">{conteudo}</div>')


def logo_svg(tamanho=30, invertido=False):
    """Marca do app como <img> com data URI (o sanitizador do st.html remove <svg> inline)."""
    fundo, traco = ("#FFFFFF", "#1F5EDB") if invertido else ("#1F5EDB", "#FFFFFF")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        f'<rect width="32" height="32" rx="9" fill="{fundo}"/>'
        f'<path d="M8 19.5c2.6 0 3.4-7 6-7s3.4 7 6 7 3.4-7 6-7" fill="none" stroke="{traco}" '
        'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="8" cy="19.5" r="1.9" fill="{traco}"/></svg>'
    )
    dados = base64.b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{dados}" width="{tamanho}" height="{tamanho}" alt="">'


def marca(invertido=False):
    return f'<div class="sf-brand">{logo_svg(30, invertido)}<b>SIGAA <span>Flow</span></b></div>'


def chip(nivel, rotulo):
    return f'<span class="sf-chip {nivel}">{ico(ICONE_NIVEL.get(nivel, "remove"), fill=nivel != "neutro")}{esc(rotulo)}</span>'


def chip_entrega(entrega):
    estado = entrega.estado
    if estado == "enviada":
        return f'<span class="sf-chip enviada">{ico("check")}Enviada</span>'
    if estado == "perdida":
        return f'<span class="sf-chip perdida">{ico("close")}Não enviada</span>'
    return f'<span class="sf-chip pendente">{ico("schedule")}Pendente</span>'


def cabecalho(titulo, sobretitulo=None, subtitulo=None):
    partes = []
    if sobretitulo:
        partes.append(f'<div class="sf-eyebrow">{esc(sobretitulo)}</div>')
    partes.append(f'<h1 class="sf-h1">{esc(titulo)}</h1>')
    if subtitulo:
        partes.append(f'<p class="sf-sub">{esc(subtitulo)}</p>')
    render(f'<div class="sf-page-head">{"".join(partes)}</div>')


def vazio(icone, titulo, texto):
    return f'<div class="sf-empty">{ico(icone)}<b>{esc(titulo)}</b><span>{esc(texto)}</span></div>'


def cartao(titulo, corpo, nota=None):
    nota_html = f'<span class="sf-card-note">{esc(nota)}</span>' if nota else ""
    return (
        f'<section class="sf-card"><div class="sf-card-head"><h3 class="sf-card-title">{esc(titulo)}</h3>'
        f"{nota_html}</div>{corpo}</section>"
    )


# ---------- sidebar ----------

def usuario(nome):
    return (
        f'{marca()}<div class="sf-user"><div class="sf-avatar">{esc(fmt.iniciais(nome))}</div>'
        f'<div style="min-width:0"><div class="sf-user-name">{esc(fmt.nome_curto(nome))}</div>'
        '<div class="sf-user-role">Discente · CEFET-MG</div></div></div>'
    )


# ---------- KPIs ----------

def kpi(rotulo, valor, dica, icone, tom=""):
    return (
        f'<div class="sf-card sf-kpi"><div style="min-width:0"><div class="sf-kpi-label">{esc(rotulo)}</div>'
        f'<div class="sf-kpi-value">{valor}</div><div class="sf-kpi-hint">{esc(dica)}</div></div>'
        f'<div class="sf-tile {tom}">{ico(icone)}</div></div>'
    )


def kpis(itens):
    return f'<div class="sf-kpis">{"".join(itens)}</div>'


# ---------- barras ----------

def barra(fracao, nivel="", marcador=None, titulo=""):
    largura = max(0.0, min(fracao, 1.0)) * 100
    marca_html = f'<b style="left:calc({marcador * 100:.1f}% - 1px)"></b>' if marcador is not None else ""
    return (
        f'<div class="sf-meter" title="{esc(titulo)}" role="img" aria-label="{esc(titulo)}">'
        f'<i class="{nivel}" style="width:{largura:.1f}%"></i>{marca_html}</div>'
    )


def barra_pontos(d):
    """Uma barra só: seus pontos, o que já foi distribuído e o que ainda falta distribuir (0–100)."""
    meta = fmt.MEDIA_APROVACAO / fmt.NOTA_MAXIMA
    pontos = d.pontos or 0
    if not d.distribuidos:
        return barra(pontos / fmt.NOTA_MAXIMA, "", meta, f"{fmt.numero(pontos)} pontos, média {fmt.MEDIA_APROVACAO}")
    seus = max(0.0, min(pontos / fmt.NOTA_MAXIMA, 1.0)) * 100
    dist = max(seus, min(d.distribuidos / fmt.NOTA_MAXIMA, 1.0) * 100)
    titulo = f"{fmt.numero(pontos)} de {fmt.numero(d.distribuidos)} pontos distribuídos"
    return (
        f'<div class="sf-meter" title="{esc(titulo)}" role="img" aria-label="{esc(titulo)}">'
        f'<i class="dist" style="width:{dist:.1f}%"></i><i style="width:{seus:.1f}%"></i>'
        f'<b style="left:calc({meta * 100:.1f}% - 1px)"></b></div>'
        f'<div class="sf-legend"><span><i></i>seus pontos <b>{fmt.numero(pontos)}</b></span>'
        f'<span><i class="dist"></i>distribuídos <b>{fmt.numero(d.distribuidos)}</b></span>'
        f'<span><i class="resto"></i>a distribuir <b>{fmt.numero(max(0, fmt.NOTA_MAXIMA - d.distribuidos))}</b></span></div>'
    )


def lista_frequencia(disciplinas):
    if not disciplinas:
        return vazio("event_busy", "Sem disciplinas", "Nenhuma turma encontrada neste período.")
    linhas = []
    for d in disciplinas:
        s = d.situacao
        resumo = f"{d.faltas} de {s.limite}" if s.limite else f"{d.faltas} faltas"
        titulo = f"{d.nome}: {d.faltas} faltas, limite {s.limite}"
        linhas.append(
            f'<div class="sf-freq-row"><div class="sf-freq-name" title="{esc(d.nome)}">{esc(d.nome)}</div>'
            f'<div class="sf-freq-meta"><span>{esc(resumo)}</span>{chip(s.nivel, s.rotulo)}</div>'
            f"{barra(s.uso, s.nivel, titulo=titulo)}"
            f'<div class="sf-freq-foot">{esc(fmt.texto_folga(s))} · {fmt.plural(d.aulas, "aula", "aulas")} no total</div></div>'
        )
    return f'<div class="sf-freq">{"".join(linhas)}</div>'


# ---------- entregas ----------

def _urgente(entrega, agora):
    return (entrega.estado == "pendente" and entrega.quando is not None
            and (entrega.quando - agora).total_seconds() < 24 * 3600)


def item_entrega(entrega, agora, mostrar_disciplina=True):
    q = entrega.quando
    urgente = _urgente(entrega, agora)
    tom = " urgente" if urgente else "" if entrega.aberta else " encerrada"
    dia = f"{q.day:02d}" if q else "—"
    mes = fmt.MESES_CURTOS[q.month - 1] if q else ""
    sub = esc(entrega.disciplina) if mostrar_disciplina else ""
    quando = fmt.prazo_relativo(q, agora) if q else esc(entrega.texto_data)
    return (
        f'<div class="sf-task"><div class="sf-date{tom}"><b>{dia}</b><span>{mes}</span></div>'
        f'<div style="min-width:0"><div class="sf-task-title" title="{esc(entrega.titulo)}">{esc(entrega.titulo)}</div>'
        f'<div class="sf-task-sub">{sub}</div></div>'
        f'<div class="sf-task-side"><span class="sf-task-when{" urgente" if urgente else ""}">{esc(quando)}</span>'
        f"{chip_entrega(entrega)}</div></div>"
    )


def lista_entregas(entregas, agora, limite=None):
    if not entregas:
        return vazio("task_alt", "Nada para entregar", "Nenhuma tarefa aberta no SIGAA agora.")
    itens = entregas[:limite] if limite else entregas
    return f'<div class="sf-list">{"".join(item_entrega(e, agora) for e in itens)}</div>'


def entregas_agrupadas(entregas, agora):
    if not entregas:
        return vazio("task_alt", "Nada por aqui", "Nenhuma tarefa neste filtro.")
    grupos = {}
    for e in entregas:
        grupos.setdefault(fmt.grupo_prazo(e.quando, agora), []).append(e)
    blocos = []
    for nome, itens in grupos.items():
        blocos.append(
            f'<div class="sf-group"><div class="sf-group-title">{esc(nome)}<em>· {len(itens)}</em></div>'
            f'<div class="sf-card" style="padding:8px 22px"><div class="sf-list">'
            f'{"".join(item_entrega(e, agora) for e in itens)}</div></div></div>'
        )
    return f'<div class="sf-groups">{"".join(blocos)}</div>'


# ---------- pontos ----------

def grafico_pontos(disciplinas):
    if not disciplinas:
        return vazio("bar_chart", "Sem dados", "Nenhuma disciplina para mostrar.")
    grade = "".join(
        f'<div class="sf-cols-grid" style="bottom:{v}%"><span>{v}</span></div>' for v in (0, 25, 50, 75, 100)
    )
    meta = fmt.MEDIA_APROVACAO
    barras, eixo = [], []
    for d in disciplinas:
        if d.pontos is None:
            barras.append(
                f'<div class="sf-col vazio"><i></i><span class="sf-tip">{esc(d.nome)}<br>Nenhuma nota lançada</span></div>'
            )
        else:
            altura = max(0.0, min(d.pontos / fmt.NOTA_MAXIMA, 1.0)) * 100
            falta = max(0.0, meta - d.pontos)
            detalhe = f"faltam {fmt.numero(falta)} para {meta}" if falta else f"já passou de {meta}"
            dist = f'<i class="dist" style="height:{min(d.distribuidos / fmt.NOTA_MAXIMA, 1) * 100:.1f}%"></i>' if d.distribuidos else ""
            if d.distribuidos:
                detalhe += f" · {fmt.numero(d.distribuidos)} distribuídos"
            barras.append(
                f'<div class="sf-col">{dist}<i style="height:{altura:.1f}%"></i>'
                f'<em style="bottom:{altura:.1f}%">{fmt.numero(d.pontos)}</em>'
                f'<span class="sf-tip" style="bottom:calc({altura:.1f}% + 28px)"><b>{esc(d.nome)}</b><br>'
                f"{fmt.numero(d.pontos)} pontos · {esc(detalhe)}</span></div>"
            )
        eixo.append(f'<span class="longo" title="{esc(d.nome)}">{esc(d.nome)}</span>'
                    f'<span class="curto" title="{esc(d.nome)}">{esc(d.sigla)}</span>')
    legenda = ('<div class="sf-legend" style="margin:14px 0 0 34px"><span><i></i>seus pontos</span>'
               '<span><i class="dist"></i>já distribuídos</span></div>') if any(d.distribuidos for d in disciplinas) else ""
    return (
        f'<div class="sf-cols">{grade}<div class="sf-cols-goal" style="bottom:{meta}%"><span>média {meta}</span></div>'
        f'<div class="sf-cols-bars">{"".join(barras)}</div></div><div class="sf-cols-x">{"".join(eixo)}</div>{legenda}'
    )


# ---------- cartões de disciplina ----------

def corpo_disciplina(d, agora):
    s = d.situacao
    pontos = fmt.numero(d.pontos) if d.pontos is not None else "—"
    restam = str(s.restantes).replace("-", "−") if s.limite else "—"
    pendentes = d.pendentes
    if pendentes:
        prox = pendentes[0]
        quando = fmt.prazo_relativo(prox.quando, agora) if prox.quando else prox.texto_data
        rodape = f'{ico("assignment")}<span>Próxima:</span><strong title="{esc(prox.titulo)}">{esc(prox.titulo)}</strong><span>· {esc(quando)}</span>'
    elif d.abertas:
        rodape = f'{ico("task_alt")}<span>Todas as entregas abertas já foram enviadas</span>'
    else:
        rodape = f'{ico("event_available")}<span>Sem entregas abertas</span>'

    if d.pontos is None:
        texto_pontos = "nenhuma nota lançada"
    elif d.pontos < fmt.MEDIA_APROVACAO:
        texto_pontos = f"faltam <b>{fmt.numero(fmt.MEDIA_APROVACAO - d.pontos)}</b> para {fmt.MEDIA_APROVACAO}"
    else:
        texto_pontos = f"<b>passou</b> dos {fmt.MEDIA_APROVACAO}"
    texto_faltas = esc(fmt.texto_folga(s)) if s.limite else "sem aulas registradas"
    classe_folga = " risco" if s.limite and s.restantes < 0 else ""
    return (
        f'<div class="sf-subj"><div class="sf-subj-head"><div style="min-width:0">'
        f'<h3 class="sf-subj-name" title="{esc(d.nome)}">{esc(d.nome)}</h3></div>'
        f"{chip(s.nivel, s.rotulo)}</div>"
        f'<div class="sf-stat-row">'
        f'<div class="sf-stat"><div class="sf-stat-label">Pontos</div><div class="sf-stat-value">{pontos}</div></div>'
        f'<div class="sf-stat"><div class="sf-stat-label">Faltas</div><div class="sf-stat-value">{d.faltas}<small> / {s.limite}</small></div></div>'
        f'<div class="sf-stat"><div class="sf-stat-label">Folga</div><div class="sf-stat-value{classe_folga}">{restam}</div></div></div>'
        f'<div class="sf-bar-block"><div class="sf-bar-label"><span>Pontos até agora</span><span>{texto_pontos}</span></div>'
        f'{barra_pontos(d)}</div>'
        f'<div class="sf-bar-block"><div class="sf-bar-label"><span>Limite de faltas</span><span>{texto_faltas}</span></div>'
        f'{barra(s.uso, s.nivel, titulo=f"{d.faltas} faltas de {s.limite} permitidas")}</div>'
        f'<div class="sf-subj-foot">{rodape}</div></div>'
    )


# ---------- detalhe da disciplina ----------

def resumo_detalhe(d):
    s = d.situacao
    pontos = fmt.numero(d.pontos) if d.pontos is not None else "—"
    situacao = f'<span class="sf-chip neutro">{ico("description")}SIGAA: {esc(d.situacao_sigaa)}</span>' if d.situacao_sigaa else ""
    return (
        f'<div class="sf-detail-head">{chip(s.nivel, s.rotulo)}{situacao}</div>'
        f'<div class="sf-stat-row">'
        f'<div class="sf-stat"><div class="sf-stat-label">Pontos</div><div class="sf-stat-value">{pontos}<small> / {fmt.NOTA_MAXIMA}</small></div></div>'
        f'<div class="sf-stat"><div class="sf-stat-label">Faltas</div><div class="sf-stat-value">{d.faltas}<small> / {s.limite}</small></div></div>'
        f'<div class="sf-stat"><div class="sf-stat-label">Entregas pendentes</div><div class="sf-stat-value">{len(d.pendentes)}</div></div></div>'
    )


def notas_detalhe(d):
    if not d.avaliacoes:
        texto = "O professor ainda não lançou notas." if d.pontos is None else "O SIGAA só mostrou o total desta turma."
        return vazio("grading", "Sem notas por avaliação", texto)
    grupos = {}
    for a in d.avaliacoes:
        grupos.setdefault(a.unidade or "Avaliações", []).append(a)
    def celula_valor(valor, maximo):
        nota = fmt.numero(valor) if valor is not None else '<span class="sf-muted">não lançada</span>'
        vale = f'<span class="sf-grade-max">{"de " if valor is not None else "vale "}{fmt.numero(maximo)}</span>' if maximo else ""
        return f'<span class="sf-grade-val"><b>{nota}</b>{vale}</span>'

    blocos = []
    for unidade, itens in grupos.items():
        linhas = []
        avaliacoes = [a for a in itens if not a.subtotal]
        maximo_unidade = sum(a.maximo for a in avaliacoes if a.maximo) or None
        for a in itens:
            classe = " total" if a.subtotal else ""
            if a.subtotal:
                valor = a.valor if a.valor is not None else (
                    sum(x.valor for x in avaliacoes if x.valor is not None) if any(x.valor is not None for x in avaliacoes) else None)
                rotulo, celula = "Total da unidade", celula_valor(valor, maximo_unidade)
            else:
                rotulo = f'<span class="sf-grade-code">{esc(a.sigla)}</span>{esc(a.titulo)}'
                celula = celula_valor(a.valor, a.maximo)
            linhas.append(f'<div class="sf-grade{classe}"><span>{rotulo}</span>{celula}</div>')
        blocos.append(f'<div class="sf-group-title">{esc(unidade)}</div><div class="sf-grades">{"".join(linhas)}</div>')

    lancadas = [a for a in d.avaliacoes if not a.subtotal and a.valor is not None]
    distribuidos = sum(a.maximo for a in lancadas if a.maximo)
    if distribuidos:
        obtidos = sum(a.valor for a in lancadas if a.maximo)
        aproveitamento = round(obtidos / distribuidos * 100)
        blocos.insert(0, f'<div class="sf-bar-block" style="margin-bottom:18px"><div class="sf-bar-label">'
                         f'<span>Você fez <b>{fmt.numero(obtidos)}</b> dos <b>{fmt.numero(distribuidos)}</b> pontos já corrigidos</span>'
                         f'<span><b>{aproveitamento}%</b> de aproveitamento</span></div>'
                         f'{barra(obtidos / distribuidos, "", fmt.MEDIA_APROVACAO / 100, "aproveitamento nas avaliações corrigidas")}</div>')
    resultado = (f'<div class="sf-grade total final"><span>Resultado no SIGAA</span><b>{esc(d.resultado)}</b></div>'
                 if d.resultado else "")
    return f'<div class="sf-grade-groups">{"".join(blocos)}{resultado}</div>'


def frequencia_detalhe(d):
    s = d.situacao
    topo = (f'<div class="sf-bar-block"><div class="sf-bar-label"><span>{d.faltas} de {s.limite} faltas permitidas</span>'
            f'<span>{esc(fmt.texto_folga(s))}</span></div>{barra(s.uso, s.nivel, titulo="uso do limite de faltas")}</div>')
    if not d.aulas_registradas:
        return topo + vazio("event_note", "Sem registro aula a aula",
                            "O professor ainda não lançou o diário de frequência.")
    linhas = []
    for r in d.aulas_registradas:
        faltas = int(r.get("faltas") or 0)
        situacao = r.get("situacao", "")
        if faltas:
            marca = f'<span class="sf-chip risco">{ico("close")}{fmt.plural(faltas, "falta", "faltas")}</span>'
        elif "presente" in situacao.lower():
            marca = f'<span class="sf-chip ok">{ico("check")}Presente</span>'
        else:
            marca = f'<span class="sf-chip neutro">{ico("remove")}{esc(situacao)}</span>'
        linhas.append(f'<div class="sf-grade"><span>{esc(r.get("data", ""))}</span>{marca}</div>')
    return f'{topo}<div class="sf-grades sf-attendance">{"".join(linhas)}</div>'


def entregas_detalhe(d, agora):
    if not d.entregas:
        return vazio("assignment", "Nenhuma tarefa", "Esta turma não tem tarefas no SIGAA.")
    itens = sorted(d.abertas, key=lambda e: e.quando or agora) + sorted(
        (e for e in d.entregas if not e.aberta), key=lambda e: e.quando, reverse=True)
    return f'<div class="sf-list">{"".join(item_entrega(e, agora, mostrar_disciplina=False) for e in itens)}</div>'
