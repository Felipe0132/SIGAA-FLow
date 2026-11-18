"""Carrega os dados do SIGAA uma vez por sessão e trata as falhas de forma amigável."""

import requests
import streamlit as st

import src.services.sigaa_service as sigaa_service
from src.ui import formato as fmt


def _credenciais():
    return {
        "user.login": st.session_state.get("usuario", ""),
        "user.senha": st.session_state.get("senha", ""),
    }


def _falha(mensagem, pode_tentar=True):
    st.error(mensagem, icon=":material/cloud_off:")
    with st.container(horizontal=True):
        if pode_tentar and st.button("Tentar novamente", icon=":material/refresh:", type="primary"):
            recarregar()
        if st.button("Sair", icon=":material/logout:"):
            encerrar_sessao()
    st.stop()


def recarregar():
    st.session_state.pop("dados_sigaa", None)
    st.rerun()


def carregar():
    """Retorna o dicionário bruto do SIGAA, buscando-o se ainda não estiver na sessão."""
    if "dados_sigaa" not in st.session_state:
        try:
            with st.spinner("Buscando suas disciplinas no SIGAA. O portal costuma levar alguns segundos…", show_time=True):
                dados = sigaa_service.datas_sigaa(_credenciais())
        except requests.Timeout:
            _falha("O SIGAA demorou demais para responder.")
        except requests.ConnectionError:
            _falha("Não deu para conectar ao SIGAA. Confira sua internet.")
        except requests.HTTPError:
            _falha("O SIGAA respondeu com erro. Tente de novo em alguns minutos.")
        except requests.RequestException:
            _falha("Algo falhou na comunicação com o SIGAA.")
        except Exception:
            _falha("O SIGAA respondeu num formato que o app não reconhece. A estrutura do portal pode ter mudado.", False)
        if not dados:
            _falha("O SIGAA não devolveu dados para esta conta. Tente entrar de novo.")
        st.session_state.dados_sigaa = dados
        st.session_state.atualizado_em = fmt.agora()
    return st.session_state.dados_sigaa


def disciplinas():
    return fmt.montar_disciplinas(carregar().get("data_materias", {}))


def encerrar_sessao():
    for chave in ("logged_in", "usuario", "senha", "dados_sigaa", "atualizado_em"):
        st.session_state.pop(chave, None)
    st.rerun()
