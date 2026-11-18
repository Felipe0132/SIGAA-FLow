from bs4 import BeautifulSoup
import re
import unicodedata

def get_notas(options_params, session, nome):
    notas = options_params["option"][2]
    onclick_code = notas['onclick']

    match_botao = re.search(r"'(formMenu:j_id_[^']+)'", onclick_code)
    id_botao_notas = match_botao.group(1)

    # Usa todos os inputs do formMenu como base (igual ao browser via jsfcljs)
    payload_notas = dict(options_params.get("form_inputs", {}))
    payload_notas['formMenu'] = 'formMenu'
    payload_notas[id_botao_notas] = id_botao_notas
    payload_notas['javax.faces.ViewState'] = options_params["view_state"]

    # Copiando exatamente os headers do browser
    headers = {
        'Referer': 'https://sig.cefetmg.br/sigaa/portais/discente/discente.jsf',
        'Origin': 'https://sig.cefetmg.br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # O action do formMenu e sempre /sigaa/ava/index.jsf
    post_url = "https://sig.cefetmg.br/sigaa/ava/index.jsf"
    res_notas = session.post(post_url, data=payload_notas, headers=headers)
    res_notas.raise_for_status()

    soup_notas = BeautifulSoup(res_notas.text, 'html.parser')

    url_notas = res_notas.url
    form_menu_notas = soup_notas.find('form', id='formMenu')

    # A pagina de relatorio de notas e estatica e abre separadamente, sem formMenu.
    # Fazemos fallback pro view_state original para nao quebrar navegacoes futuras (ex: frequencia)
    view_state_freq = options_params["view_state"] 
    if form_menu_notas:
        input_vs = form_menu_notas.find('input', {'name': 'javax.faces.ViewState'})
        if input_vs:
            view_state_freq = input_vs['value']

    relatorio_notas = soup_notas.find('table', {'class':'tabelaRelatorio'})
    notas = extrair_notas(relatorio_notas, nome) if relatorio_notas else None

    # Atualiza o estado para o proximo parser APENAS se continuarmos no AVA (tiver formMenu)
    if form_menu_notas:
        try:
            options_params["view_state"] = view_state_freq
            options_params["url_atual"] = url_notas
        except:
            pass

    return notas


COLUNAS_FINAIS = 4  # Reposição, Resultado, Faltas, Sit.


def _texto(tag):
    return " ".join(tag.get_text(" ", strip=True).split()) if tag else ""


def _numero(texto):
    try:
        return float(texto.replace(',', '.'))
    except (AttributeError, ValueError):
        return None


def _cabecalho(tabela):
    """Lê as duas linhas de cabeçalho: unidades (com colspan) e siglas das avaliações."""
    linhas = [tr for tr in tabela.find_all('tr') if tr.find('th') and not tr.find('td')]
    if len(linhas) < 2:
        return []

    unidades = []
    for th in linhas[0].find_all('th'):
        rotulo = _texto(th)
        if not rotulo or th.get('rowspan') or rotulo.lower() in ('matrícula', 'nome', 'matrícula nome', 'reposição', 'resultado', 'faltas', 'sit.'):
            continue
        unidades += [rotulo] * int(th.get('colspan', 1) or 1)

    # O SIGAA guarda os detalhes de cada avaliação em inputs ocultos ligados ao id do <th>
    # (th id="aval_123" -> input#denAval_123 = nome, #notaAval_123 = nota máxima, #pesoAval_123 = peso)
    raiz = tabela
    while raiz.parent is not None:
        raiz = raiz.parent

    def oculto(prefixo, id_aval):
        campo = raiz.find('input', id=f"{prefixo}{id_aval}") if id_aval else None
        return (campo.get('value') or "").strip() if campo else ""

    avaliacoes = []
    for i, th in enumerate(th for th in linhas[-1].find_all('th') if _texto(th)):
        id_th = th.get('id') or ""
        id_aval = id_th.split('_', 1)[1] if id_th.startswith('aval_') else ""
        avaliacoes.append({
            "unidade": unidades[i] if i < len(unidades) else "",
            "sigla": _texto(th),
            "titulo": oculto("denAval_", id_aval) or th.get('title') or "",
            "maximo": _numero(oculto("notaAval_", id_aval)),
            "peso": _numero(oculto("pesoAval_", id_aval)),
        })
    return avaliacoes


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", " ".join(str(texto).split()).lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def _linha_do_aluno(tabela, nome):
    """O relatório do discente costuma ter só a linha dele; o nome pode vir com acento ou abreviado."""
    linhas = [tr for tr in tabela.find_all('tr') if tr.find('td')]
    if len(linhas) == 1:
        return linhas[0]
    alvo = _normalizar(nome)
    for tr in linhas:
        if alvo and alvo in _normalizar(tr.get_text(" ")):
            return tr
    partes = alvo.split()
    if len(partes) >= 2:
        for tr in linhas:
            texto = _normalizar(tr.get_text(" "))
            if partes[0] in texto and partes[-1] in texto:
                return tr
    return None


def extrair_notas(tabela, nome):
    """Retorna {'total', 'avaliacoes': [{unidade, sigla, titulo, valor}], 'resultado', 'situacao'}."""
    linha = _linha_do_aluno(tabela, nome)
    if not linha:
        return None

    colunas = linha.find_all('td')
    if len(colunas) < 2 + COLUNAS_FINAIS:
        return None

    celulas = colunas[2:len(colunas) - COLUNAS_FINAIS]
    cabecalho = _cabecalho(tabela)
    reconhecido = len(cabecalho) == len(celulas)
    if not reconhecido:
        cabecalho = [{"unidade": "", "sigla": f"Avaliação {i + 1}", "titulo": "", "maximo": None, "peso": None}
                     for i in range(len(celulas))]

    avaliacoes, total = [], 0.0
    for info, celula in zip(cabecalho, celulas):
        valor = _numero(_texto(celula))
        # 'Nota' é o subtotal da unidade: mostrado à parte e fora da soma
        subtotal = info["sigla"].lower() == "nota"
        avaliacoes.append({**info, "valor": valor, "subtotal": subtotal})
        if valor is not None and not subtotal:
            total += valor

    # Sem cabeçalho reconhecido, mantém a regra antiga (última coluna da unidade é o subtotal)
    if not reconhecido and avaliacoes:
        avaliacoes[-1]["subtotal"] = True
        total = sum(a["valor"] for a in avaliacoes[:-1] if a["valor"] is not None)
    else:
        # Quando o SIGAA já fechou a 'Nota' da unidade, ela é o valor oficial (já arredondado)
        total, itens = 0.0, []
        for a in avaliacoes:
            if not a["subtotal"]:
                itens.append(a["valor"])
                continue
            total += a["valor"] if a["valor"] is not None else sum(v for v in itens if v is not None)
            itens = []
        total += sum(v for v in itens if v is not None)
    total = round(total, 2)

    return {
        "total": total,
        "avaliacoes": avaliacoes,
        "resultado": _texto(colunas[-3]),
        "situacao": _texto(colunas[-1]),
    }
