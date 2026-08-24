from bs4 import BeautifulSoup
import re

def get_tarefas(options_params, session):
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

    tarefas_disp_childs = soup_tarefas.find_all('a', {'title':'Enviar tarefa'})

    tarefas = {}

    for tarefas_disp_child in tarefas_disp_childs:
        tr_tarefas = tarefas_disp_child.find_parent('tr')
        td_tarefas = tr_tarefas.find_all('td')
        if len(td_tarefas) >= 3:
            tarefa_nome = td_tarefas[1].text.strip()
            tarefa_data = td_tarefas[2].text.strip()
            tarefa_data = re.search(r'de\s+(.+)', tarefa_data).group(1)

            tarefa_enviada = bool(tr_tarefas.find('a', {'title':'Visualizar Tarefa Enviada/Corrigida'}))

            tarefas[tarefa_nome] = [tarefa_data, tarefa_enviada]

    return tarefas