from bs4 import BeautifulSoup
import re

def get_saldo(url_saldo, session):
    resposta = session.get(url_saldo)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, 'html.parser')

    tabela = soup.find('tbody')
    if not tabela:
        return None

    dados = tabela.find_all('tr')
    if len(dados) < 3:
        return None

    colunas = dados[2].find_all('td')
    if len(colunas) < 2:
        return None

    match = re.search(r'-?\d+', colunas[1].text)
    return match.group() if match else None
