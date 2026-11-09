from bs4 import BeautifulSoup
import re
import datetime

def get_tarefas(options_params, session):
    data_atual = datetime.datetime.now()

    tarefas = options_params["option"][3]
    onclick_code = tarefas['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    if not match_botao:
        return {}
    id_botao_tarefas = match_botao.group(1)

    # SIGAA/JSF precisa receber os campos ocultos do formulário, não apenas
    # o botão clicado e o ViewState, para reproduzir o envio feito pelo browser.
    payload_tarefas = dict(options_params.get("form_inputs", {}))
    payload_tarefas['formMenu'] = 'formMenu'
    payload_tarefas[id_botao_tarefas] = id_botao_tarefas
    payload_tarefas['javax.faces.ViewState'] = options_params["view_state"]

    headers = {
        'Referer': options_params["url_atual"],
        'Origin': 'https://sig.cefetmg.br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    res_tarefas = session.post(
        options_params["url_atual"],
        data=payload_tarefas,
        headers=headers,
    )
    res_tarefas.raise_for_status()
    soup_tarefas = BeautifulSoup(res_tarefas.text, 'html.parser')

    tarefas_disp_childs = soup_tarefas.find_all(
        'a', {'title': re.compile(r'^Enviar tarefa$', re.IGNORECASE)}
    )

    tarefas = {}

    for tarefas_disp_child in tarefas_disp_childs:
        tr_tarefas = tarefas_disp_child.find_parent('tr')
        if not tr_tarefas:
            continue

        td_tarefas = tr_tarefas.find_all('td', recursive=False)
        if len(td_tarefas) >= 3:
            td_nome = td_tarefas[1]
            td_data = td_tarefas[2]

            if not td_nome or not td_data:
                continue

            tarefa_nome = " ".join(td_nome.get_text(" ", strip=True).split())
            texto_periodo = " ".join(td_data.get_text(" ", strip=True).split())
            match_data = re.search(
                r'\ba\s+(\d{2}/\d{2}/\d{4}\s+às\s+\d{2}h\d{2})',
                texto_periodo,
                re.IGNORECASE,
            )
            if not match_data:
                continue
            tarefa_data = " ".join(match_data.group(1).split())

            tarefa_enviada = bool(tr_tarefas.find('a', {'title':'Visualizar Tarefa Enviada/Corrigida'}))

            try:
                data_formatada = datetime.datetime.strptime(tarefa_data, "%d/%m/%Y às %Hh%M")
            except ValueError:
                continue
            if data_atual < data_formatada:
                tarefas[tarefa_nome] = [tarefa_data, tarefa_enviada]

    return tarefas
