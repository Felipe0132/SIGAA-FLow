from bs4 import BeautifulSoup
import re

def get_freq(options_params, session):
    frequencias = options_params["option"][0]

    onclick_code = frequencias['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    id_botao_frequencia = match_botao.group(1)
    
    # Usa todos os inputs do formMenu como base e headers do browser para garantir que o SIGAA responda
    payload_frequencia = dict(options_params.get("form_inputs", {}))
    payload_frequencia['formMenu'] = 'formMenu'
    payload_frequencia[id_botao_frequencia] = id_botao_frequencia
    payload_frequencia['javax.faces.ViewState'] = options_params["view_state"]

    headers = {
        'Referer': 'https://sig.cefetmg.br/sigaa/portais/discente/discente.jsf',
        'Origin': 'https://sig.cefetmg.br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    res_frequencia = session.post(options_params["url_atual"], data=payload_frequencia, headers=headers)
    soup_frequencia = BeautifulSoup(res_frequencia.text, 'html.parser')

    total_aulas = 0
    div_botoes = soup_frequencia.find('div', {'class':'botoes-show'})
    if div_botoes:
        match = re.search(r'CH do Componente:\s*(\d+)', div_botoes.text, re.IGNORECASE)

        if match:
            total_aulas = int(match.group(1))

    num_faltas = 0
    relacao = soup_frequencia.find('table', {'class':'listing'})
    if relacao:
        linhas = relacao.find_all('tr')
        for linha in linhas:
            colunas = linha.find_all('td')

            if len(colunas) >= 2: # colunas[0]=Data/Aula, colunas[1]=Situação
                situacao = colunas[1].text.strip().capitalize()
                if "falta" in situacao.lower():
                    qtd_faltas = re.search(r'\d+', situacao) # Pega o primeiro inteiro na string (ex: '2 Falta(s)' -> 2)
                    if qtd_faltas:
                        num_faltas += int(qtd_faltas.group())
                    else: # Quando houver apenas 'Falta'
                        num_faltas += 1

    return {"total_aulas":total_aulas, "faltas":num_faltas}