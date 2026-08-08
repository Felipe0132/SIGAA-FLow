# 🎓 SIGAA Flow — CEFET-MG

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sigaa-flow.streamlit.app/)

O **SIGAA Flow** é um dashboard em Python + Streamlit que centraliza suas informações acadêmicas em uma única tela: **notas, faltas e saldo de recarga do RU** das matérias do período atual.

---

## 💡 Motivação

No SIGAA, consultar suas notas, faltas e o saldo do Restaurante Universitário (RU) exige repetir manualmente os mesmos passos várias vezes: entrar em cada matéria, abrir a aba de notas, depois a de frequência, anotar os dados, voltar e repetir para as demais disciplinas — além de checar o saldo do RU em uma página separada.

Os dados existem, mas ficam descentralizados e espalhados. A proposta do **SIGAA Flow** é automatizar essa rotina: o script faz o percurso de navegação via requisições de rede em segundo plano e junta tudo em uma interface simples, rápida e organizada.

---

## ⚡ O que ele faz

1. **Autenticação Direta:** Você faz login com suas credenciais do SIGAA (as mesmas do portal oficial).
2. **Raspagem de Dados (Scraping):** O script acessa o portal discente via `requests` e `BeautifulSoup` (sem abrir um navegador pesado) e extrai:
   - 📖 **Carga horária total** de cada matéria
   - 📝 **Nota atual** acumulada
   - ⚠️ **Faltas utilizadas** e faltas restantes até o limite permitido (25%)
   - 💳 **Saldo de recarga** do Restaurante Universitário (RU)
3. **Exibição Centralizada:** Apresenta todas as informações do período organizadas em cartões dinâmicos e expansíveis.

---

## 🛠️ Tecnologias utilizadas

- **[Python](https://www.python.org/)** — linguagem base do projeto
- **[Streamlit](https://streamlit.io/)** — interface web e navegação entre páginas (`st.navigation`)
- **[Requests](https://requests.readthedocs.io/)** — sessão HTTP para autenticar e navegar pelo SIGAA
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** — parsing do HTML retornado pelo SIGAA

---

## ⚠️ Isso vai funcionar para você?

> Este projeto foi desenvolvido e testado especificamente para o **SIGAA do CEFET-MG** (`sig.cefetmg.br`).

O SIGAA é utilizado por diversas instituições de ensino, porém cada uma possui sua própria instância com variações na estrutura HTML — nomes de formulários, seletores de tabelas e IDs de campos.

Se você pertence a outra instituição e quer adaptar o projeto, verifique se:
- A URL de login segue o padrão: `https://sig.SEUDOMINIO/sigaa/verTelaLogin.do`
- As páginas de notas e frequência utilizam tabelas com as classes CSS `relatorio` e `listing`.

*Caso a estrutura da sua instituição seja diferente, será necessário ajustar os seletores HTML no arquivo `get_data_sigaa.py`.*

---

## 🚀 Como usar

### Opção 1: Acessar pelo navegador (mais rápido)

O app já está implantado na nuvem e pronto para uso:

🔗 **[Acessar SIGAA Flow no Streamlit Cloud](https://sigaa-flow.streamlit.app/)**

### Opção 2: Executar localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Felipe0132/SIGAA-FLow.git
   cd SIGAA-FLow
   ```

2. **Instale as dependências** (o projeto já inclui um `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```

3. **Rode o app:**
   ```bash
   streamlit run streamlit_app.py
   ```

### Fazendo login

Use seu usuário e senha do SIGAA na tela inicial (funciona igual nas duas opções acima). Os dados são enviados diretamente ao SIGAA para autenticação — **nada é salvo ou compartilhado**.

---

## 🔒 Sobre privacidade e segurança

- O login usa `requests.Session()` para autenticar como se fosse o navegador acessando o SIGAA normalmente.
- Usuário e senha ficam apenas na sessão do Streamlit (`st.session_state`) durante o uso do app — não são gravados em arquivo, banco de dados ou enviados a terceiros.
- A verificação SSL é desativada nas requisições (`session.verify = False`) para evitar erros de certificado do próprio SIGAA — isso é necessário para o scraping funcionar, mas vale saber que está acontecendo.

---

## 📁 Estrutura do projeto

```
├── streamlit_app.py       # Tela de login e navegação (st.navigation)
├── dashboard.py            # Tela principal com notas, faltas e saldo
├── get_data_sigaa.py       # Lógica de scraping (login, notas, frequência, saldo)
└── requirements.txt        # Dependências do projeto
```

---

## 🧩 Limitações conhecidas

- Depende da estrutura atual das páginas do SIGAA — se a instituição atualizar o sistema, o scraping pode quebrar.
- Não há cache: cada login refaz todas as requisições do zero (pode demorar alguns segundos).
- Pega apenas as notas e faltas que já estão publicadas no SIGAA no momento da consulta.