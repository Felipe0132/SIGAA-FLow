import requests
from bs4 import BeautifulSoup
import re

def _request(session, method, url, **kwargs):
    """Executa uma requisição e valida a resposta HTTP."""
    resposta = session.request(method, url, **kwargs)
    resposta.raise_for_status()
    return resposta

# DADOS LOGIN
"""
dados_login_exemplo = {
    'user.login': usuario,
    'user.senha': senha,
}
"""

def teste_login(dados_login):
    session = requests.Session()
    session.verify = False # Confia ao enviar dados para ignorar erros de certificado de privacidade (SSL)
    requests.packages.urllib3.disable_warnings()
    # URLS
    
    url_login = "https://sig.cefetmg.br/sigaa/verTelaLogin.do"
    
    resposta = _request(session, "get", url_login) # Resposta do get da URL

    soup = BeautifulSoup(resposta.text, 'html.parser') # HTML puro

    form_login = soup.find('form', {'name': 'loginForm'}) # Procura o primeiro elemento que eh um form loginForm
    if not form_login or not form_login.get('action'):
        return False
    action_url = form_login['action'] # Busca a action, o proximo caminho

    url_login_completa = f"https://sig.cefetmg.br{action_url}" # URL com a acao

    resposta = _request(session, "post", url_login_completa, data=dados_login) # Coloca os dados do login

    soup = BeautifulSoup(resposta.text, 'html.parser')

    if soup.find('center', string=re.compile(r'Usuário e/ou senha inválidos')):
        print("Login falho")
        return False
    return soup

def logar(url_login, dados_login, session):
    resposta = _request(session, "get", url_login)

    soup = BeautifulSoup(resposta.text, 'html.parser')

    form_login = soup.find('form', {'name': 'loginForm'})
    if not form_login:
        return False

    if not form_login.get('action'):
        return False
    action_url = form_login['action']

    url_login_completa = f"https://sig.cefetmg.br{action_url}"

    resposta = _request(session, "post", url_login_completa, data=dados_login)

    soup = BeautifulSoup(resposta.text, 'html.parser')

    if soup.find('center', string=re.compile(r'Usuário e/ou senha inválidos')):
        print("Login falho")
        return False
    return soup

def criar_sessao():
    session = requests.Session()
    session.verify = False # Confia ao enviar dados para ignorar erros de certificado de privacidade (SSL)
    requests.packages.urllib3.disable_warnings()
    
    return session
