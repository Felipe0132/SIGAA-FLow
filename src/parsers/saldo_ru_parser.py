from bs4 import BeautifulSoup
import re

def get_saldo(url_saldo, session):
    resposta = session.get(url_saldo)

    soup = BeautifulSoup(resposta.text, 'html.parser')

    tabela = soup.find('tbody')

    dados = tabela.find_all('tr')
    saldo = dados[2].find_all('td')
    saldo = re.search(r'-?\d+', saldo[1].text).group()

    return saldo