from bs4 import BeautifulSoup
import re

def get_freq(options_params, session):
    frequencias = options_params["option"][0]

    onclick_code = frequencias['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    id_botao_frequencia = match_botao.group(1)
    
    payload_frequencia = {
        'formMenu': 'formMenu',
        id_botao_frequencia: id_botao_frequencia,
        'javax.faces.ViewState': options_params["view_state"]
    }

    res_frequencia = session.post(options_params["url_atual"], data=payload_frequencia)
    soup_frequencia = BeautifulSoup(res_frequencia.text, 'html.parser')

    total_aulas = 0
    div_botoes = soup_frequencia.find('div', {'class':'botoes-show'})
    if div_botoes:
        match = re.search(r'CH do Componente:\s*(\d+)', div_botoes.text, re.IGNORECASE) # Pega o que vem depois CH do Componentes, somente a parte do numero

        if match:
            total_aulas = int(match.group(1))

    num_faltas = 0
    relacao = soup_frequencia.find('table', {'class':'listing'})
    if relacao:
        linhas = relacao.find_all('tr')
        for linha in linhas:
            colunas = linha.find_all('td')

            if len(colunas) >= 2: # Verifica se existe pelo menos 2 td, data e situacao
                situacao = colunas[1].text.strip()
                if "Falta" in situacao:
                    qtd_faltas = re.search(r'\d+', situacao) # Procura o inteiro na string
                    if qtd_faltas:
                        num_faltas += int(qtd_faltas.group())
                    else: # Quando houver so falta
                        num_faltas += 1

    return {"total_aulas":total_aulas, "faltas":num_faltas}