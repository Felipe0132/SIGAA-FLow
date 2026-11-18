from bs4 import BeautifulSoup
import re
import datetime
from urllib.parse import urljoin

def _menu_atual(options_params):
    """Link 'Tarefas', campos do formMenu e URL da última página do AVA (como o navegador faria)."""
    pagina = options_params.get("pagina_menu")
    form = pagina.find('form', id='formMenu') if pagina else None
    if form:
        link = next((a for a in form.find_all('a') if a.get_text(strip=True) == 'Tarefas'), None)
        if link:
            campos = {i.get('name'): i.get('value', '') for i in form.find_all('input') if i.get('name')}
            url = urljoin("https://sig.cefetmg.br", form.get('action') or "/sigaa/ava/index.jsf")
            return link, campos, url
    campos = dict(options_params.get("form_inputs", {}))
    campos['javax.faces.ViewState'] = options_params["view_state"]
    return options_params["option"][3], campos, options_params["url_atual"]


def get_tarefas(options_params, session):
    link, payload_tarefas, url = _menu_atual(options_params)

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", link.get('onclick', ''))
    if not match_botao:
        return {}
    id_botao_tarefas = match_botao.group(1)

    # SIGAA/JSF precisa receber os campos ocultos do formulário, não apenas
    # o botão clicado e o ViewState, para reproduzir o envio feito pelo browser.
    payload_tarefas['formMenu'] = 'formMenu'
    payload_tarefas[id_botao_tarefas] = id_botao_tarefas

    # O menu é um RichFaces PanelBar: o servidor só processa cliques do grupo aberto.
    # Como o navegador, zeramos o painel ativo e enviamos o grupo do link ("Atividades").
    painel = link.find_parent('div', class_='rich-panelbar-interior')
    if painel and painel.get('id'):
        for chave in list(payload_tarefas):
            m = re.match(r'(formMenu:j_id_jsp_\d+)_69$', chave)
            if m:
                payload_tarefas.pop(f"{m.group(1)}_92", None)
                payload_tarefas[chave] = ''
        payload_tarefas[painel['id']] = ''

    headers = {
        'Referer': options_params["url_atual"],
        'Origin': 'https://sig.cefetmg.br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    res_tarefas = session.post(url, data=payload_tarefas, headers=headers)
    res_tarefas.raise_for_status()
    soup_tarefas = BeautifulSoup(res_tarefas.text, 'html.parser')

    return extrair_tarefas(soup_tarefas)


PADRAO_DATA = re.compile(r'(\d{2}/\d{2}/\d{4})\s+às\s+(\d{2})h(\d{2})', re.IGNORECASE)


def _data(match):
    return datetime.datetime.strptime(f"{match.group(1)} {match.group(2)}:{match.group(3)}", "%d/%m/%Y %H:%M")


def extrair_tarefas(soup):
    """Todas as tarefas da turma (abertas e encerradas).

    Retorna {nome: [fim 'dd/mm/aaaa às HHhMM', enviada, inicio 'dd/mm/aaaa às HHhMM' | None]}.
    Uma linha é tarefa quando a 3ª coluna traz o período 'De ... às ... a ... às ...'.
    """
    tarefas = {}
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td', recursive=False)
        if len(tds) < 3:
            continue
        nome = " ".join(tds[1].get_text(" ", strip=True).split())
        periodo = " ".join(tds[2].get_text(" ", strip=True).split())
        if not nome or len(nome) > 300 or len(periodo) > 160:
            continue
        datas = list(PADRAO_DATA.finditer(periodo))
        if not datas:
            continue
        try:
            fim = _data(datas[-1])
            inicio = _data(datas[0]) if len(datas) > 1 else None
        except ValueError:
            continue
        enviada = bool(tr.find('a', {'title': re.compile(r'Visualizar Tarefa Enviada', re.IGNORECASE)}))
        tarefas[nome] = [
            fim.strftime("%d/%m/%Y às %Hh%M"),
            enviada,
            inicio.strftime("%d/%m/%Y às %Hh%M") if inicio else None,
        ]
    return tarefas
