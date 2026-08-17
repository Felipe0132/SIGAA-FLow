from bs4 import BeautifulSoup
import re

def get_notas(options_params, session, nome):
    notas = options_params["option"][2]
    onclick_code = notas['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    id_botao_notas = match_botao.group(1) # Qual seria o caminho

    payload_notas = {
        'formMenu': 'formMenu',
        'formMenu:j_id_jsp': 'formMenu:j_id_jsp',
        id_botao_notas: id_botao_notas,
        'javax.faces.ViewState': options_params["view_state"]
    }

    res_notas = session.post(options_params["url_atual"], data=payload_notas)
    soup_notas = BeautifulSoup(res_notas.text, 'html.parser')

    form_menu_notas = soup_notas.find('form', id='formMenu')
    view_state_freq = form_menu_notas.find('input', {'name': 'javax.faces.ViewState'})['value']
    url_notas = res_notas.url
    
    relatorio_notas = soup_notas.find('div', {'class':'tabelaRelatorio'})
    notas_atual = 0
    if relatorio_notas:
        td_nota = relatorio_notas.find('td', string=re.compile(re.escape(nome), re.IGNORECASE))
        if td_nota:
            linha_nota = td_nota.find_parent('tr')

            if linha_nota:
                colunas = linha_nota.find_all('td')
                if len(colunas) >= 3:
                    notas_atual = colunas[-3].text.strip()

    try:
        options_params["view_state"] = view_state_freq
        options_params["url_atual"] = url_notas
    except:
        print("Aq")

    return notas_atual