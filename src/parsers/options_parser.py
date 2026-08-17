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
    view_state_notas = form_menu.find('input', {'name': 'javax.faces.ViewState'})['value']
    
    options = soup.find_all('td', {'class':'rich-panelbar-content'})[1].find_all('a')

    return {"url_atual":url_ava, "view_state":view_state_notas, "option":options, "nome":nome_materia}
