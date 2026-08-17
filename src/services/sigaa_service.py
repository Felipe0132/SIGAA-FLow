import src.core.client as client
import src.parsers.turmas_parser as turmas_parser
import src.parsers.saldo_ru_parser as saldo_parser
import src.services.materia_service as materia_service

URL_LOGIN = "https://sig.cefetmg.br/sigaa/verTelaLogin.do"
URL_DISCENTE = "https://sig.cefetmg.br/sigaa/portais/discente/discente.jsf"
URL_SALDO = "https://sig.cefetmg.br/sigaa/entrarSistema.do?sistema=sipac&vinculoDiscente=true&url=restaurante/vendas/saldo_cartao.jsf?voltar=/sigaa/verPortalDiscente" # URL saldo fica em outro sistema, com o L[ nao A[ como outros do proprio SIGAA


def datas_sigaa(dados_login):
    

    session = client.criar_sessao()

    resposta_login = client.logar(URL_LOGIN, dados_login, session)

    if not resposta_login:
        print("Falha no login")
        return {}

    nome = turmas_parser.get_nome(resposta_login)

    tabela_materias = turmas_parser.get_materias(URL_DISCENTE, session)

    if not tabela_materias:
        print("Falha ao carregar turmas")
        return {}

    data_materias = {}
    
    for materia in tabela_materias:
        """
        Exemplo
            <form action="/sigaa/portais/discente/discente.jsf" enctype="application/x-www-form-urlencoded" id="form_acessarTurmaVirtual" method="post" name="form_acessarTurmaVirtual">
            <input name="form_acessarTurmaVirtual" type="hidden" value="form_acessarTurmaVirtual"/>
            <a href="#" onclick="var a=function(){return prevenirDuploClique();};var b=function(){if(typeof jsfcljs == 'function'){jsfcljs(document.getElementById('form_acessarTurmaVirtual'),{'form_acessarTurmaVirtual:j_id_jsp_161879646_442':'form_acessarTurmaVirtual:j_id_jsp_161879646_442','frontEndIdTurma':'53B7AE975737A3577CDB50EF0D262AD76053847F'},'');}return false};return (a()==false) ? false : b();">ALGORITMOS E ESTRUTURAS DE DADOS II</a><input id="javax.faces.ViewState" name="javax.faces.ViewState" type="hidden" value="j_id2"/>
            </form>
        """
        data_materias.update(materia_service.get_datas_by_materia(materia, URL_DISCENTE, session, nome))

    saldo = saldo_parser.get_saldo(URL_SALDO, session)

    return {
            "nome":nome,
            "saldo":saldo,
            "data_materias":data_materias
            }