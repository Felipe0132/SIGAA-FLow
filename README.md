# 🎓 SIGAA Flow — CEFET-MG

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sigaa-flow.streamlit.app/)

O **SIGAA Flow** é um dashboard em Python e Streamlit que reúne informações acadêmicas do período atual: notas, frequência, tarefas e saldo do Restaurante Universitário (RU), apresentado em quantidade de vezes disponíveis (não em reais).

## O que o app mostra

- Carga horária e nota acumulada de cada disciplina;
- faltas registradas e estimativa de faltas restantes com base no limite de 25%;
- tarefas futuras e seu status de envio;
- saldo do RU em quantidade de vezes disponíveis.

As disciplinas podem ser consultadas em duas visualizações:

- **Cartões:** resumo de carga horária, nota, faltas restantes e tarefas futuras;
- **Tabela:** matéria, CH total, nota e faltas usadas em relação ao limite estimado (por exemplo, `7/8`).

O app acessa o portal do SIGAA por requisições HTTP e interpreta as páginas com BeautifulSoup. Foi desenvolvido para a instância do CEFET-MG (`sig.cefetmg.br`); outras instituições podem usar estruturas HTML diferentes.

## Requisitos e execução

É necessário Python compatível com as dependências listadas em `requirements.txt`.

```bash
git clone https://github.com/Felipe0132/SIGAA-FLow.git
cd SIGAA-FLow
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Também é possível acessar a implantação publicada em [sigaa-flow.streamlit.app](https://sigaa-flow.streamlit.app/).

## Login, sessão e privacidade

Entre com as credenciais do SIGAA. Elas são mantidas na sessão ativa do Streamlit para buscar as informações acadêmicas e não são gravadas em arquivo ou banco de dados pelo projeto. Use **Sair** na navegação para encerrar a sessão e remover as credenciais e os dados carregados da sessão do app.

As requisições aguardam o SIGAA responder, sem um limite de tempo configurado, pois o portal pode estar lento. Erros de conexão e respostas HTTP inesperadas são apresentados com mensagens amigáveis; em caso de falha de conexão, o app oferece a opção de tentar novamente.

> **Atenção:** o cliente HTTP atualmente desativa a validação de certificados SSL (`session.verify = False`) por causa de problemas de certificado reportados pelo portal. Isso reduz a segurança da conexão; evite usar o app em redes não confiáveis e habilite a validação SSL assim que a causa puder ser corrigida.

## Estrutura do projeto

```text
├── streamlit_app.py          # Login e navegação do Streamlit
├── dashboard.py              # Exibição dos dados acadêmicos
├── src/
│   ├── core/                  # Cliente HTTP e modelos
│   ├── parsers/               # Leitura das páginas HTML do SIGAA
│   └── services/              # Orquestração de consultas
├── assets/images/             # Imagens de referência do guia
└── requirements.txt           # Dependências Python
```

## Limitações

- A extração depende da estrutura das páginas do SIGAA e pode precisar de ajustes quando o portal mudar.
- São exibidas apenas informações publicadas e disponíveis para a conta autenticada no momento da consulta.
- O app não mantém cache entre sessões; uma nova sessão consulta novamente o SIGAA.
