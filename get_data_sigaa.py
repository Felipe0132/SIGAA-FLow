import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os

load_dotenv()

usuario = os.getenv("SIGAA_USUARIO")
senha = os.getenv("SIGAA_SENHA")

# DADOS LOGIN

dados_login_exemplo = {
    'user.login': usuario,
    'user.senha': senha,
}

def teste_login(dados_login):
    session = requests.Session()
    session.verify = False # Confia ao enviar dados para ignorar erros de certificado de privacidade (SSL)
    requests.packages.urllib3.disable_warnings()
    # URLS
    
    url_login = "https://sig.cefetmg.br/sigaa/verTelaLogin.do"
    
    resposta = session.get(url_login) # Resposta do get da URL

    soup = BeautifulSoup(resposta.text, 'html.parser') # HTML puro

    form_login = soup.find('form', {'name': 'loginForm'}) # Procura o primeiro elemento que eh um form loginForm
    action_url = form_login['action'] # Busca a action, o proximo caminho

    url_login_completa = f"https://sig.cefetmg.br{action_url}" # URL com a acao

    resposta = session.post(url_login_completa, data=dados_login) # Coloca os dados do login

    soup = BeautifulSoup(resposta.text, 'html.parser')

    if soup.find('center', string=re.compile(r'Usuário e/ou senha inválidos')):
        print("Login falho")
        return False
    return soup

def logar(url_login, dados_login, session):
    resposta = session.get(url_login) # Resposta do get da URL

    soup = BeautifulSoup(resposta.text, 'html.parser') # HTML puro

    form_login = soup.find('form', {'name': 'loginForm'}) # Procura o primeiro elemento que eh um form loginForm
    action_url = form_login['action'] # Busca a action, o proximo caminho

    url_login_completa = f"https://sig.cefetmg.br{action_url}" # URL com a acao

    resposta = session.post(url_login_completa, data=dados_login) # Coloca os dados do login

    soup = BeautifulSoup(resposta.text, 'html.parser')

    if soup.find('center', string=re.compile(r'Usuário e/ou senha inválidos')):
        print("Login falho")
        return False
    return soup
    
def get_materias(url_discente, session):
    resposta = session.get(url_discente) 
    
    soup = BeautifulSoup(resposta.text, 'html.parser')
    
    materias = soup.find_all('form', {'id': re.compile(r'^form_acessarTurmaVirtual')})
    if materias:
        return materias
    return False

def get_options_params(materia, url_discente, session):
    nome_form = materia['name'] # "form_acessarTurmaVirtual"
    link_a = materia.find('a') # <a href="#" onclick="var a=function(){return prevenirDuploClique();};var b=function(){if(typeof jsfcljs == 'function'){jsfcljs(document.getElementById('form_acessarTurmaVirtual'),{'form_acessarTurmaVirtual:j_id_jsp_161879646_442':'form_acessarTurmaVirtual:j_id_jsp_161879646_442','frontEndIdTurma':'53B7AE975737A3577CDB50EF0D262AD76053847F'},'');}return false};return (a()==false) ? false : b();">ALGORITMOS E ESTRUTURAS DE DADOS II</a><input id="javax.faces.ViewState" name="javax.faces.ViewState" type="hidden" value="j_id2"/>
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

def get_notas(options_params, session):
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
    
    relatorio_notas = soup_notas.find('div', {'class':'relatorio'})
    notas_atual = 0
    if relatorio_notas:
        linha_par = relatorio_notas.find('tr', {'class':'linhaPar'})

        if linha_par:
            colunas = relatorio_notas.find_all('td')
            if len(colunas) >= 3:
                notas_atual = colunas[-3].text.strip()

    try:
        options_params["view_state"] = view_state_freq
        options_params["url_atual"] = url_notas
    except:
        print("Aq")

    return notas_atual
    
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

    total_aulas = soup_frequencia.find('div', {'class':'botoes-show'})
    if total_aulas:
        match = re.search(r'CH do Componente:\s*(\d+)', total_aulas.text, re.IGNORECASE) # Pega o que vem depois CH do Componentes, somente a parte do numero

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
                    
def get_datas_by_materia(materia, url_discente, session):
    options_params = get_options_params(materia, url_discente, session)
    
    # PAGINAS NOTAS
    
    notas_atual = get_notas(options_params, session)

    # PAGINA FREQUENCIA

    freq = get_freq(options_params, session)
    total_aulas = freq["total_aulas"]
    num_faltas = freq["faltas"]

    return {options_params["nome"]:{"total_aulas":total_aulas, "total_faltas":num_faltas, "notas_atual":notas_atual}}

def get_nome_saldo(url_saldo, session):
    resposta = session.get(url_saldo)

    soup = BeautifulSoup(resposta.text, 'html.parser')

    tabela = soup.find('tbody')

    dados = tabela.find_all('tr')
    nome = dados[0].find('td').text
    saldo = dados[2].find_all('td')
    saldo = re.search(r'\d+', saldo[1].text).group()

    return {"nome":nome, "saldo":saldo}

def datas_sigaa(dados_login):
    session = requests.Session()
    session.verify = False # Confia ao enviar dados para ignorar erros de certificado de privacidade (SSL)
    requests.packages.urllib3.disable_warnings()
    # URLS

    url_login = "https://sig.cefetmg.br/sigaa/verTelaLogin.do"
    url_discente = "https://sig.cefetmg.br/sigaa/portais/discente/discente.jsf"
    url_saldo = "https://sig.cefetmg.br/sigaa/entrarSistema.do?sistema=sipac&vinculoDiscente=true&url=restaurante/vendas/saldo_cartao.jsf?voltar=/sigaa/verPortalDiscente" # URL saldo fica em outro sistema, com o L[ nao A[ como outros do proprio SIGAA


    # RETORNO

    data_materias = dict()

    # TELA LOGIN

    resposta_login = logar(url_login, dados_login, session)

    if not resposta_login:
        print("Falha no login")
        return data_materias

    tabela_materias = get_materias(url_discente, session)

    if not tabela_materias:
        print("Falha no portal")
        return data_materias
    
    for materia in tabela_materias:
        """
        Exemplo
            <form action="/sigaa/portais/discente/discente.jsf" enctype="application/x-www-form-urlencoded" id="form_acessarTurmaVirtual" method="post" name="form_acessarTurmaVirtual">
            <input name="form_acessarTurmaVirtual" type="hidden" value="form_acessarTurmaVirtual"/>
            <a href="#" onclick="var a=function(){return prevenirDuploClique();};var b=function(){if(typeof jsfcljs == 'function'){jsfcljs(document.getElementById('form_acessarTurmaVirtual'),{'form_acessarTurmaVirtual:j_id_jsp_161879646_442':'form_acessarTurmaVirtual:j_id_jsp_161879646_442','frontEndIdTurma':'53B7AE975737A3577CDB50EF0D262AD76053847F'},'');}return false};return (a()==false) ? false : b();">ALGORITMOS E ESTRUTURAS DE DADOS II</a><input id="javax.faces.ViewState" name="javax.faces.ViewState" type="hidden" value="j_id2"/>
            </form>
        """
        data_materias.update(get_datas_by_materia(materia, url_discente, session))

    nome_saldo = get_nome_saldo(url_saldo, session)

    return {
            "nome":nome_saldo["nome"],
            "saldo":nome_saldo["saldo"],
            "data_materias":data_materias
            }

#dados_materia(dados_login)