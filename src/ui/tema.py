"""Tokens visuais e CSS global do app.

As cores base dos widgets nativos ficam em .streamlit/config.toml; aqui ficam os
tokens dos componentes em HTML, escolhidos conforme o tema ativo (claro/escuro).
"""

import streamlit as st

TOKENS = {
    "light": {
        "bg": "#F4F6FA",
        "surface": "#FFFFFF",
        "surface-2": "#F8F9FC",
        "line": "#E3E7EE",
        "line-strong": "#D3D9E3",
        "ink": "#0E1626",
        "ink-2": "#475266",
        "ink-3": "#7C869A",
        "track": "#EBEEF4",
        "brand": "#1F5EDB",
        "brand-soft": "#E9F0FD",
        "brand-2": "#A8C1F3",
        "brand-ink": "#1A4FB8",
        "ok": "#1F8A55",
        "ok-soft": "#E4F3EB",
        "warn": "#B26A00",
        "warn-soft": "#FCF0DC",
        "bad": "#C7352B",
        "bad-soft": "#FBE7E5",
        "neutral": "#7C869A",
        "neutral-soft": "#EEF1F5",
        "shadow": "0 1px 2px rgba(16,24,40,.04)",
    },
    "dark": {
        "bg": "#0B0F17",
        "surface": "#121926",
        "surface-2": "#161E2C",
        "line": "#222C3D",
        "line-strong": "#2E3A4F",
        "ink": "#E7ECF4",
        "ink-2": "#A9B3C4",
        "ink-3": "#7A8599",
        "track": "#212A3A",
        "brand": "#6E9BFF",
        "brand-soft": "rgba(110,155,255,.14)",
        "brand-2": "#3F5A96",
        "brand-ink": "#9DBCFF",
        "ok": "#45C384",
        "ok-soft": "rgba(69,195,132,.14)",
        "warn": "#E7A43C",
        "warn-soft": "rgba(231,164,60,.15)",
        "bad": "#F2695E",
        "bad-soft": "rgba(242,105,94,.15)",
        "neutral": "#7A8599",
        "neutral-soft": "rgba(122,133,153,.16)",
        "shadow": "none",
    },
}


def tipo_tema():
    try:
        return "dark" if st.context.theme.type == "dark" else "light"
    except Exception:
        return "light"


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..24,400..600,0..1,0&display=block');

:root { %(vars)s }

/* ---------- moldura do Streamlit ---------- */
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 1240px; padding-top: 2.25rem; padding-bottom: 4rem;
}
[data-testid="stSidebarContent"] { display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] { order: -1; padding-bottom: .25rem; }
[data-testid="stSidebarHeader"] { order: -2; height: 3rem; min-height: 0; padding-top: .75rem; padding-bottom: 0; }
[data-testid="stSidebarNav"] { order: 0; }
[data-testid="stSidebarNavLink"] { border-radius: 10px; padding: .45rem .7rem; margin: 1px 0; }
[data-testid="stSidebarNavLink"] span { font-weight: 500; }
[data-testid="stSidebarNavSeparator"] { display: none; }
[data-testid="stNavSectionHeader"] {
  font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-3);
  margin-top: 1rem;
}
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
.stButton button, .stFormSubmitButton button { font-weight: 600; }
[data-testid="stForm"] { border: none; padding: 0; }
.stTextInput input { height: 2.75rem; }

/* ---------- componentes ---------- */
.sf { color: var(--ink); font-variant-numeric: tabular-nums; }
.sf * { box-sizing: border-box; }
.sf-ico { font-family: 'Material Symbols Rounded'; font-weight: 500; font-style: normal;
  font-size: 20px; line-height: 1; letter-spacing: normal; text-transform: none;
  display: inline-block; white-space: nowrap; direction: ltr; -webkit-font-smoothing: antialiased;
  font-feature-settings: 'liga'; font-variation-settings: 'FILL' 0, 'opsz' 20; }
.sf-ico.fill { font-variation-settings: 'FILL' 1, 'opsz' 20; }

.sf-page-head { display: flex; flex-direction: column; gap: 4px; margin-bottom: 4px; }
.sf-eyebrow { font-size: .85rem; color: var(--ink-3); text-transform: lowercase; }
.sf-eyebrow::first-letter { text-transform: uppercase; }
.sf-h1 { font-size: 1.9rem; font-weight: 700; letter-spacing: -.02em; line-height: 1.15; margin: 0; color: var(--ink); }
.sf-sub { color: var(--ink-2); font-size: .95rem; margin: 0; }

.sf-card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
  padding: 20px 22px; box-shadow: var(--shadow); }
.sf-card-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.sf-card-title { font-size: 1.02rem; font-weight: 600; margin: 0; color: var(--ink); }
.sf-card-note { font-size: .8rem; color: var(--ink-3); }

/* KPIs */
.sf-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.sf-kpi { display: flex; justify-content: space-between; gap: 12px; padding: 18px 20px; }
.sf-kpi-label { font-size: .84rem; color: var(--ink-2); margin-bottom: 8px; }
.sf-kpi-value { font-size: 1.75rem; font-weight: 600; letter-spacing: -.02em; line-height: 1.1; color: var(--ink); }
.sf-kpi-value small { font-size: .95rem; font-weight: 500; color: var(--ink-2); letter-spacing: 0; margin-left: 4px; }
.sf-kpi-hint { font-size: .8rem; color: var(--ink-3); margin-top: 8px; line-height: 1.35;
  overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.sf-tile { flex: none; width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center;
  background: var(--brand-soft); color: var(--brand); }
.sf-tile.warn { background: var(--warn-soft); color: var(--warn); }
.sf-tile.bad { background: var(--bad-soft); color: var(--bad); }
.sf-tile.ok { background: var(--ok-soft); color: var(--ok); }

/* chips de status: sempre ícone + texto */
.sf-chip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px 3px 6px; border-radius: 999px;
  font-size: .75rem; font-weight: 600; white-space: nowrap; line-height: 1.2; }
.sf-chip .sf-ico { font-size: 15px; }
.sf-chip.ok { background: var(--ok-soft); color: var(--ok); }
.sf-chip.atencao { background: var(--warn-soft); color: var(--warn); }
.sf-chip.risco { background: var(--bad-soft); color: var(--bad); }
.sf-chip.neutro { background: var(--neutral-soft); color: var(--ink-2); }
.sf-chip.enviada { background: var(--ok-soft); color: var(--ok); }
.sf-chip.pendente { background: var(--neutral-soft); color: var(--ink-2); }
.sf-chip.perdida { background: var(--bad-soft); color: var(--bad); }

/* barras de uso */
.sf-meter { position: relative; height: 8px; border-radius: 4px; background: var(--track); }
.sf-meter > i { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 4px; background: var(--brand); }
.sf-meter > i.dist { background: var(--brand-2); }
.sf-meter > i + i { box-shadow: 2px 0 0 var(--surface); }
.sf-legend { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: .75rem; color: var(--ink-3); margin-top: 2px; }
.sf-legend span { display: inline-flex; align-items: center; gap: 5px; }
.sf-legend b { color: var(--ink-2); font-weight: 600; }
.sf-legend i { width: 10px; height: 10px; border-radius: 3px; background: var(--brand); }
.sf-legend i.dist { background: var(--brand-2); }
.sf-legend i.resto { background: var(--track); }
.sf-meter > i.ok { background: var(--ok); }
.sf-meter > i.atencao { background: var(--warn); }
.sf-meter > i.risco { background: var(--bad); }
.sf-meter > i.neutro { background: var(--neutral); }
.sf-meter > b { position: absolute; top: -4px; bottom: -4px; width: 2px; border-radius: 1px;
  background: var(--ink-2); box-shadow: 0 0 0 2px var(--surface); }

/* lista de frequência */
.sf-freq { display: flex; flex-direction: column; gap: 16px; }
.sf-freq-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 14px; align-items: center; }
.sf-freq-name { font-size: .92rem; font-weight: 500; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sf-freq-meta { display: flex; align-items: center; gap: 10px; font-size: .82rem; color: var(--ink-2); white-space: nowrap; }
.sf-freq-row .sf-meter { grid-column: 1 / -1; }
.sf-freq-foot { font-size: .78rem; color: var(--ink-3); grid-column: 1 / -1; margin-top: -2px; }

/* entregas */
.sf-list { display: flex; flex-direction: column; }
.sf-task { display: grid; grid-template-columns: 46px minmax(0, 1fr) auto; gap: 14px; align-items: center;
  padding: 12px 0; border-top: 1px solid var(--line); }
.sf-list > .sf-task:first-child { border-top: none; padding-top: 2px; }
.sf-date { width: 46px; height: 50px; border-radius: 10px; border: 1px solid var(--line); background: var(--surface-2);
  display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1; }
.sf-date b { font-size: 1.15rem; font-weight: 600; color: var(--ink); }
.sf-date span { font-size: .68rem; color: var(--ink-3); text-transform: uppercase; letter-spacing: .05em; margin-top: 4px; }
.sf-date.urgente { border-color: transparent; background: var(--bad-soft); }
.sf-date.urgente b, .sf-date.urgente span { color: var(--bad); }
.sf-date.encerrada { background: transparent; border-style: dashed; }
.sf-date.encerrada b { color: var(--ink-3); }
.sf-task-title { font-size: .93rem; font-weight: 500; color: var(--ink); overflow: hidden; text-overflow: ellipsis;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.3; }
.sf-task-sub { font-size: .8rem; color: var(--ink-3); margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sf-task-side { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.sf-task-when { font-size: .8rem; color: var(--ink-2); white-space: nowrap; }
.sf-task-when.urgente { color: var(--bad); font-weight: 600; }

.sf-groups { max-width: 880px; }
.sf-group { margin-top: 26px; }
.sf-group:first-child { margin-top: 0; }
.sf-group-title { display: flex; align-items: center; gap: 8px; font-size: .78rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase; color: var(--ink-3); margin: 0 0 8px; }
.sf-group-title em { font-style: normal; font-weight: 500; color: var(--ink-3); letter-spacing: 0; }

/* gráfico de pontos */
.sf-cols { position: relative; height: 220px; margin: 8px 0 0 34px; border-bottom: 1px solid var(--line-strong); }
.sf-cols-grid { position: absolute; left: -34px; right: 0; border-top: 1px dashed var(--line); font-size: .7rem; color: var(--ink-3); }
.sf-cols-grid span { position: absolute; top: -7px; left: 0; width: 26px; text-align: right; }
.sf-cols-goal { position: absolute; left: 0; right: 0; border-top: 2px dashed var(--ink-3); z-index: 0; }
.sf-cols-goal span { position: absolute; right: 0; top: -20px; font-size: .72rem; color: var(--ink-2); background: var(--surface);
  padding: 0 4px; }
.sf-cols-bars { position: absolute; inset: 0; display: flex; align-items: flex-end; justify-content: space-around; gap: 2px; z-index: 1; }
.sf-col { position: relative; flex: 1; max-width: 150px; height: 100%%; display: flex; align-items: flex-end; justify-content: center; }
.sf-col > i { width: 60%%; max-width: 36px; min-height: 2px; border-radius: 4px 4px 0 0; background: var(--brand); transition: opacity .15s; }
.sf-col > i.dist { position: absolute; bottom: 0; left: 50%%; transform: translateX(-50%%); background: var(--brand-2); }
.sf-col.vazio > i { background: transparent; border: 1px dashed var(--line-strong); border-bottom: none; height: 12px; }
.sf-col > em { position: absolute; font-style: normal; font-size: .78rem; font-weight: 600; color: var(--ink); transform: translateY(-4px);
  background: var(--surface); padding: 0 4px 2px; border-radius: 4px; }
.sf-col > i:not(.dist) { position: relative; z-index: 1; }
.sf-cols-bars:hover .sf-col > i { opacity: .45; }
.sf-cols-bars .sf-col:hover > i { opacity: 1; }
.sf-tip { position: absolute; bottom: calc(100%% + 8px); left: 50%%; transform: translateX(-50%%); z-index: 5;
  background: var(--ink); color: var(--surface); font-size: .76rem; line-height: 1.35; padding: 6px 9px; border-radius: 8px;
  white-space: nowrap; pointer-events: none; opacity: 0; transition: opacity .12s; }
.sf-col:hover .sf-tip { opacity: 1; }
.sf-cols-x { display: flex; justify-content: space-around; gap: 2px; margin: 8px 0 0 34px; }
.sf-cols-x .curto { display: none; }
.sf-cols-x span { flex: 1; max-width: 150px; text-align: center; font-size: .75rem; line-height: 1.3; color: var(--ink-2);
  padding: 0 4px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

/* cartões de disciplina */
.sf-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 14px; }
.sf-subj { display: flex; flex-direction: column; gap: 18px; }
.sf-subj-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.sf-subj-tag { font-size: .72rem; font-weight: 600; color: var(--brand-ink); letter-spacing: .04em; margin-bottom: 4px; }
.sf-subj-name { font-size: 1rem; font-weight: 600; line-height: 1.3; color: var(--ink); margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.sf-stat-row { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--line); border-radius: 10px; }
.sf-stat { padding: 10px 12px; border-left: 1px solid var(--line); }
.sf-stat:first-child { border-left: none; }
.sf-stat-label { font-size: .72rem; color: var(--ink-3); }
.sf-stat-value { font-size: 1.15rem; font-weight: 600; color: var(--ink); margin-top: 2px; }
.sf-stat-value small { font-size: .78rem; color: var(--ink-3); font-weight: 500; }
.sf-stat-value.risco { color: var(--bad); }
.sf-bar-block { display: flex; flex-direction: column; gap: 7px; }
.sf-bar-label { display: flex; justify-content: space-between; font-size: .8rem; color: var(--ink-2); }
.sf-bar-label b { color: var(--ink); font-weight: 600; }
.sf-subj-foot { display: flex; align-items: center; gap: 8px; padding-top: 14px; border-top: 1px solid var(--line);
  font-size: .82rem; color: var(--ink-2); min-height: 1.2em; }
.sf-subj-foot .sf-ico { font-size: 18px; color: var(--ink-3); }
.sf-subj-foot strong { color: var(--ink); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* contêiner nativo como cartão de disciplina */
[class*="st-key-disc_"] { background: var(--surface); border-radius: 14px; box-shadow: var(--shadow); }
[class*="st-key-disc_"] .stButton button { margin-top: -2px; }

/* detalhe */
.sf-detail-head { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.sf-grade-groups .sf-group-title { margin-top: 18px; }
.sf-grade-groups .sf-group-title:first-child { margin-top: 0; }
.sf-grades { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.sf-grade { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 14px;
  border-top: 1px solid var(--line); font-size: .9rem; color: var(--ink); }
.sf-grade:first-child { border-top: none; }
.sf-grade b { font-weight: 600; }
.sf-grade.total { background: var(--surface-2); color: var(--ink-2); }
.sf-grade.total b { color: var(--ink); }
.sf-grade.final { margin-top: 14px; border: 1px solid var(--line); border-radius: 10px; }
.sf-grade-code { display: inline-block; min-width: 52px; margin-right: 8px; font-size: .75rem; font-weight: 600;
  color: var(--brand-ink); letter-spacing: .03em; }
.sf-muted { color: var(--ink-3); font-weight: 400; font-size: .85rem; }
.sf-grade-val { display: inline-flex; align-items: baseline; gap: 6px; white-space: nowrap; }
.sf-grade-max { font-size: .8rem; color: var(--ink-3); min-width: 3.2em; text-align: right; }
.sf-attendance { margin-top: 16px; }

/* vazio */
.sf-empty { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 6px; padding: 34px 12px; color: var(--ink-2); }
.sf-empty .sf-ico { font-size: 30px; color: var(--ink-3); margin-bottom: 4px; }
.sf-empty b { color: var(--ink); font-weight: 600; }
.sf-empty span { font-size: .85rem; }

/* sidebar */
.sf-brand { display: flex; align-items: center; gap: 10px; padding: 2px 4px 14px; }
.sf-brand img { flex: none; display: block; }
.sf-brand b { font-size: 1.1rem; font-weight: 700; letter-spacing: -.01em; color: var(--ink); }
.sf-brand b span { color: var(--brand); }
.sf-user { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 12px;
  background: var(--surface-2); border: 1px solid var(--line); }
.sf-avatar { flex: none; width: 36px; height: 36px; border-radius: 50%%; display: grid; place-items: center;
  background: var(--brand); color: #fff; font-weight: 600; font-size: .85rem; letter-spacing: .02em; }
.sf-user-name { font-size: .88rem; font-weight: 600; color: var(--ink); line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sf-user-role { font-size: .75rem; color: var(--ink-3); margin-top: 2px; }

/* login */
.sf-hero { position: relative; overflow: hidden; background: #1F5EDB; color: #fff; border-radius: 20px;
  padding: 36px 36px 30px; min-height: 560px; display: flex; flex-direction: column; }
.sf-hero::after { content: ""; position: absolute; right: -120px; bottom: -160px; width: 420px; height: 420px;
  border-radius: 50%%; border: 70px solid rgba(255,255,255,.06); }
.sf-hero .sf-brand b, .sf-hero .sf-brand b span { color: #fff; }
.sf-hero h1 { font-size: 2.35rem; line-height: 1.1; letter-spacing: -.03em; font-weight: 700; margin: 40px 0 14px; color: #fff; max-width: 13ch; }
.sf-hero p { font-size: 1rem; line-height: 1.5; color: rgba(255,255,255,.82); margin: 0; max-width: 36ch; }
.sf-preview { position: relative; z-index: 1; margin-top: auto; display: flex; flex-direction: column; gap: 8px; max-width: 360px; padding-top: 32px; }
.sf-preview-row { display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 12px;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.14); font-size: .88rem; }
.sf-preview-row .sf-ico { font-size: 19px; color: rgba(255,255,255,.9); }
.sf-preview-row .lbl { flex: 1; color: rgba(255,255,255,.85); }
.sf-preview-row b { font-weight: 600; color: #fff; }
.sf-hero-foot { position: relative; z-index: 1; margin-top: 22px; font-size: .75rem; color: rgba(255,255,255,.6); }
.sf-login-head { margin-bottom: 18px; }
.sf-login-head h2 { font-size: 1.6rem; font-weight: 700; letter-spacing: -.02em; margin: 0 0 6px; color: var(--ink); }
.sf-login-head p { margin: 0; color: var(--ink-2); font-size: .95rem; }
.sf-note { display: flex; gap: 8px; align-items: flex-start; font-size: .8rem; color: var(--ink-3); line-height: 1.45; margin-top: 6px; }
.sf-note .sf-ico { font-size: 17px; margin-top: 1px; }

@media (max-width: 720px) {
  .sf-hero { min-height: 0; padding: 26px 24px; }
  .sf-hero h1 { font-size: 1.8rem; margin-top: 22px; }
  .sf-preview, .sf-hero-foot { display: none; }
  .sf-h1 { font-size: 1.55rem; }
  .sf-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .sf-kpi { padding: 14px; }
  .sf-kpi .sf-tile { display: none; }
  .sf-kpi-value { font-size: 1.4rem; }
  .sf-cols-x .longo { display: none; }
  .sf-cols-x .curto { display: -webkit-box; }
  .sf-grid { grid-template-columns: 1fr; }
  .sf-task { grid-template-columns: 42px minmax(0, 1fr); }
  .sf-task-side { grid-column: 2; flex-direction: row; align-items: center; justify-content: flex-start; }
}
"""


def aplicar_estilo():
    tokens = TOKENS[tipo_tema()]
    variaveis = " ".join(f"--{nome}: {valor};" for nome, valor in tokens.items())
    st.html(f"<style>{CSS % {'vars': variaveis}}</style>")
