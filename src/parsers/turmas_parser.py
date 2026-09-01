from bs4 import BeautifulSoup
import re

def get_materias(url_discente, session):
    resposta = session.get(url_discente) 
    
    soup = BeautifulSoup(resposta.text, 'html.parser')
    
    materias = soup.find_all('form', {'id': re.compile(r'^form_acessarTurmaVirtual')})
    if materias:
        return materias
    return False

def get_nome(resposta_login):
    p = resposta_login.find('p', {'class':'usuario'})
    if not p or not p.span:
        return 'Estudante'
    return p.span.text