from bs4 import BeautifulSoup
import re

def get_notas(options_params, session, nome):
    notas = options_params["option"][2]
    onclick_code = notas['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    id_botao_notas = match_botao.group(1)

    # Usa todos os inputs do formMenu como base (igual ao browser via jsfcljs)
    payload_notas = dict(options_params.get("form_inputs", {}))
    payload_notas['formMenu'] = 'formMenu'
    payload_notas[id_botao_notas] = id_botao_notas
    payload_notas['javax.faces.ViewState'] = options_params["view_state"]

    # Copiando exatamente os headers do browser
    headers = {
        'Referer': 'https://sig.cefetmg.br/sigaa/portais/discente/discente.jsf',
        'Origin': 'https://sig.cefetmg.br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # O action do formMenu e sempre /sigaa/ava/index.jsf
    post_url = "https://sig.cefetmg.br/sigaa/ava/index.jsf"
    res_notas = session.post(post_url, data=payload_notas, headers=headers)

    soup_notas = BeautifulSoup(res_notas.text, 'html.parser')

    url_notas = res_notas.url
    form_menu_notas = soup_notas.find('form', id='formMenu')

    # A pagina de relatorio de notas e estatica e abre separadamente, sem formMenu.
    # Fazemos fallback pro view_state original para nao quebrar navegacoes futuras (ex: frequencia)
    view_state_freq = options_params["view_state"] 
    if form_menu_notas:
        input_vs = form_menu_notas.find('input', {'name': 'javax.faces.ViewState'})
        if input_vs:
            view_state_freq = input_vs['value']

    relatorio_notas = soup_notas.find('table', {'class':'tabelaRelatorio'})
    notas_atual = None

    if relatorio_notas:
        nome_limpo = " ".join(nome.split())# Limpa quebras de linha e espacos extras do nome
        
        # Busca pelo nome usando get_text() para evitar problemas com espacos/tags no HTML
        td_nota = relatorio_notas.find(lambda tag: tag.name == 'td' and nome_limpo.lower() in " ".join(tag.get_text().split()).lower())
        
        if td_nota:
            linha_nota = td_nota.find_parent('tr')
            if linha_nota:
                colunas = linha_nota.find_all('td')
                notas_atual = 0.0
                if len(colunas) >= 3:
                    for i in range(2, len(colunas)-3):
                        nota = colunas[i].text.strip().replace(',', '.')
                        if nota:
                            try:
                                notas_atual += float(nota)
                            except ValueError:
                                pass

    # Atualiza o estado para o proximo parser APENAS se continuarmos no AVA (tiver formMenu)
    if form_menu_notas:
        try:
            options_params["view_state"] = view_state_freq
            options_params["url_atual"] = url_notas
        except:
            pass

    return notas_atual