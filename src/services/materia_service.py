import src.parsers.options_parser as options_parser
import src.parsers.notas_parser as notas_parser
import src.parsers.frequencia_parser as frequencia_parser

def get_datas_by_materia(materia, url_discente, session, nome):
    options_params = options_parser.get_options_params(materia, url_discente, session)
    
    # PAGINAS NOTAS
    
    notas_atual = notas_parser.get_notas(options_params, session, nome)

    # PAGINA FREQUENCIA

    freq = frequencia_parser.get_freq(options_params, session)
    total_aulas = freq["total_aulas"]
    num_faltas = freq["faltas"]

    return {options_params["nome"]:{"total_aulas":total_aulas, "total_faltas":num_faltas, "notas_atual":notas_atual}}
