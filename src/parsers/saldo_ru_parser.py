from bs4 import BeautifulSoup
import re

def get_saldo(url_saldo, session):
    resposta = session.get(url_saldo)

    soup = BeautifulSoup(resposta.text, 'html.parser')

    tabela = soup.find('tbody')
    if not tabela:
        return '0'

    dados = tabela.find_all('tr')
    if len(dados) < 3:
        return '0'

    colunas = dados[2].find_all('td')
    if len(colunas) < 2:
        return '0'

    match = re.search(r'-?\d+', colunas[1].text)
    return match.group() if match else '0'