from bs4 import BeautifulSoup
import re

def get_options_params(materia, url_discente, session):
    nome_form = materia['name'] # "form_acessarTurmaVirtual"
    link_a = materia.find('a') # <a href="#" onclick="var a=function(){return prevenirDuploClique();};var b=function(){if(typeof jsfcljs == 'function'){jsfcljs(document.getElementById('form_acessarTurmaVirt  ual'),{'form_acessarTurmaVirtual:j_id_jsp_161879646_442':'form_acessarTurmaVirtual:j_id_jsp_161879646_442','frontEndIdTurma':'53B7AE975737A3577CDB50EF0D262AD76053847F'},'');}return false};return (a()==false) ? false : b();">ALGORITMOS E ESTRUTURAS DE DADOS II</a><input id="javax.faces.ViewState" name="javax.faces.ViewState" type="hidden" value="j_id2"/>
    nome_materia = link_a.text.strip()
    onclick_code = link_a['onclick'] # "var a=function(){return prevenirDuploClique();};var b=function(){if(typeof jsfcljs == 'function'){jsfcljs(document.getElementById('form_acessarTurmaVirtual'),{'form_acessarTurmaVirtual:j_id_jsp_161879646_442':'form_acessarTurmaVirtual:j_id_jsp_161879646_442','frontEndIdTurma':'53B7AE975737A3577CDB50EF0D262AD76053847F'},'');}return false};return (a()==false) ? false : b();" 
    
    # REGEX
    
    match_botao = re.search(fr"'({nome_form}:j_id_[^']+)'", onclick_code) # Entre '', comece com o form..., e seu id. Regex de 'form_acessarTurmaVirtual:j_id_jsp_161879646_442'
    match_turma = re.search(r"'frontEndIdTurma':'([^']+)'", onclick_code) # Procura a hash. '53B7AE975737A3577CDB50EF0D262AD76053847F'
    
    id_botao = match_botao.group(1) # Aqui pega limpo do Regex
    id_turma = match_turma.group(1)
    
    view_state = materia.find('input', {'name': 'javax.faces.ViewState'})['value'] # "j_id2"
    
    payload_materia = { # Dados que serao enviados pelo form
        nome_form: nome_form,
        id_botao: id_botao,
        'frontEndIdTurma': id_turma,
        'javax.faces.ViewState': view_state
    }
    
    res_materia = session.post(url_discente, data=payload_materia)
    soup = BeautifulSoup(res_materia.text, 'html.parser')
    
    url_ava = res_materia.url
    
    form_menu = soup.find('form', id='formMenu')
    if not form_menu:
        return None

    # O jsfcljs no browser submete o form inteiro, nao so o botao clicado.
    # Por isso, capturamos todos os <input> do formMenu aqui,
    # para que os parsers consigam replicar exatamente o que o browser envia.
    form_inputs = {}
    for inp in form_menu.find_all('input'): # Dos os inputs
        name = inp.get('name')           # nome do campo (ex: 'javax.faces.ViewState')
        value = inp.get('value', '')     # valor do campo (pode ser vazio)
        if name:
            form_inputs[name] = value    # salva {nome: valor} para uso nos payloads

    view_state_notas = form_inputs.get('javax.faces.ViewState', '') # extrai o ViewState do dict

    # O JavaScript do RichFaces altera o form antes de enviar (Python nao roda JS, entao forjamos isso):
    # 1. Ele apaga o valor do _69 (tracker do painel ativo).
    # 2. Ele cria dinamicamente o _92 (vazio), que nem existe no HTML original.
    # O Regex acha a base variavel do ID (ex: 311393315) para replicar essa exata estrutura.
    for key in list(form_inputs.keys()):
        m = re.match(r'(formMenu:j_id_jsp_\d+)_69$', key)
        if m:
            base = m.group(1)
            form_inputs[key] = ''           # 1. Zera o _69 (imita JS apagando valor)
            form_inputs[f'{base}_92'] = ''  # 2. Adiciona _92 vazio (imita JS criando input fantasma)
            break


    options_nota_freq = soup.find_all('td', {'class':'rich-panelbar-content'})[1].find_all('a')
    options3 = soup.find_all('td', {'class':'rich-panelbar-content'})[3].find_all('a')
    options_tarefas = options3[2]

    options = options_nota_freq + [options_tarefas]

    return {"url_atual":url_ava, "view_state":view_state_notas, "form_inputs":form_inputs, "option":options, "nome":nome_materia}
