from bs4 import BeautifulSoup
import re
import datetime

def get_tarefas(options_params, session):
    data_atual = datetime.datetime.now()
    
    tarefas = options_params["option"][3]
    
    onclick_code = tarefas['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    id_botao_tarefas = match_botao.group(1)
    
    payload_tarefas = {
        'formMenu': 'formMenu',
        id_botao_tarefas: id_botao_tarefas,
        'javax.faces.ViewState': options_params["view_state"]
    }

    res_tarefas = session.post(options_params["url_atual"], data=payload_tarefas)
    soup_tarefas = BeautifulSoup(res_tarefas.text, 'html.parser')

    tarefas = {}

    for tr_tarefas in soup_tarefas.find_all('tr'):
        td_tarefas = tr_tarefas.find_all('td', recursive=False)
        if len(td_tarefas) >= 3:
            td_nome = td_tarefas[1]
            td_data = td_tarefas[2]

            if not td_nome or not td_data:
                continue

            tarefa_nome = " ".join(td_nome.get_text().split())
            tarefa_data_texto = " ".join(td_data.get_text().split())
            match_data = re.search(r'\ba\s+(\d{2}/\d{2}/\d{4}\s+às\s+\d{2}h\d{2})', tarefa_data_texto)
            if not match_data:
                continue
            tarefa_data = match_data.group(1)

            tarefa_enviada = bool(
                tr_tarefas.find('a', {'title': re.compile(r'Visualizar Tarefa Enviada/Corrigida', re.IGNORECASE)})
            )

            data_formatada = datetime.datetime.strptime(tarefa_data, "%d/%m/%Y às %Hh%M")
            if data_atual <= data_formatada:
                chave = tarefa_nome
                contador = 2
                while chave in tarefas:
                    chave = f"{tarefa_nome} ({contador})"
                    contador += 1
                tarefas[chave] = [tarefa_data, tarefa_enviada]

    return tarefas