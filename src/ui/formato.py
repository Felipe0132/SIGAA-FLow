"""Regras de apresentação: nomes, datas, números e situação de cada disciplina.

Tudo aqui é puro (sem Streamlit) para facilitar testes e reuso entre telas.
"""

import datetime
import math
import re
from dataclasses import dataclass, field

try:
    from zoneinfo import ZoneInfo

    FUSO = ZoneInfo("America/Sao_Paulo")
except Exception:  # tzdata ausente: cai para o horário do servidor
    FUSO = None

LIMITE_FALTAS = 0.25
MEDIA_APROVACAO = 60
NOTA_MAXIMA = 100

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
DIAS_CURTOS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_CURTOS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

PALAVRAS_MINUSCULAS = {"a", "o", "e", "as", "os", "da", "de", "do", "das", "dos", "em", "na", "no",
                       "nas", "nos", "para", "com", "ao", "aos", "à", "às", "por", "um", "uma"}
ROMANO = re.compile(r"^(?=[IVXL]+$)M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$")


def agora():
    if FUSO:
        return datetime.datetime.now(FUSO).replace(tzinfo=None)
    return datetime.datetime.now()


# ---------- textos ----------

def _capitalizar(palavra):
    return palavra[:1].upper() + palavra[1:].lower()


def primeiro_nome(nome):
    partes = (nome or "").split()
    return _capitalizar(partes[0]) if partes else "Estudante"


def nome_curto(nome):
    partes = (nome or "").split()
    if not partes:
        return "Estudante"
    if len(partes) == 1:
        return _capitalizar(partes[0])
    return f"{_capitalizar(partes[0])} {_capitalizar(partes[-1])}"


def iniciais(nome):
    partes = (nome or "").split()
    if not partes:
        return "?"
    letras = partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")
    return letras.upper()


def titulo_disciplina(nome):
    """'ALGORITMOS E ESTRUTURAS DE DADOS II' -> 'Algoritmos e Estruturas de Dados II'."""
    palavras = (nome or "").split()
    saida = []
    for i, palavra in enumerate(palavras):
        maiuscula = palavra.upper()
        if ROMANO.match(maiuscula) and i > 0:
            saida.append(maiuscula)
        elif i > 0 and palavra.lower() in PALAVRAS_MINUSCULAS:
            saida.append(palavra.lower())
        else:
            saida.append("-".join(_capitalizar(p) for p in palavra.split("-")))
    return " ".join(saida)


def sigla(nome):
    """Sigla curta para eixos de gráfico: 'Algoritmos e Estruturas de Dados II' -> 'AED II'."""
    letras, sufixo = "", ""
    for palavra in (nome or "").split():
        maiuscula = palavra.upper()
        if ROMANO.match(maiuscula):
            sufixo = " " + maiuscula
        elif palavra.lower() not in PALAVRAS_MINUSCULAS:
            letras += palavra[0].upper()
    return (letras[:4] or "?") + sufixo


def numero(valor, casas=2):
    if valor is None:
        return "—"
    texto = f"{float(valor):.{casas}f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def plural(n, singular, plural_):
    return f"{n} {singular if n == 1 else plural_}"


# ---------- datas ----------

def data_extensa(momento):
    return f"{DIAS[momento.weekday()]}, {momento.day} de {MESES[momento.month - 1]}"


def ler_data_sigaa(texto):
    """'21/11/2026 às 23h59' -> datetime. Retorna None se o formato mudar."""
    try:
        return datetime.datetime.strptime(" ".join(str(texto).split()), "%d/%m/%Y às %Hh%M")
    except (TypeError, ValueError):
        return None


def hora(momento):
    return f"{momento.hour:02d}h{momento.minute:02d}"


def prazo_relativo(quando, referencia):
    """Texto curto para quanto falta: 'em 40 min', 'hoje, 23h59', 'amanhã, 18h00', 'em 5 dias'."""
    if quando is None:
        return "sem data"
    restante = quando - referencia
    if restante.total_seconds() < 0:
        atras = (referencia.date() - quando.date()).days
        if atras == 0:
            return f"encerrou hoje, {hora(quando)}"
        if atras == 1:
            return "encerrou ontem"
        return f"encerrou há {atras} dias"
    if restante < datetime.timedelta(hours=1):
        return f"em {max(1, int(restante.total_seconds() // 60))} min"
    dias = (quando.date() - referencia.date()).days
    if dias == 0:
        return f"hoje, {hora(quando)}"
    if dias == 1:
        return f"amanhã, {hora(quando)}"
    if dias < 7:
        return f"{DIAS_CURTOS[quando.weekday()]}, {hora(quando)}"
    return f"em {dias} dias, {hora(quando)}"


def grupo_prazo(quando, referencia):
    if quando is None:
        return "Sem data"
    if quando < referencia:
        return "Encerradas"
    dias = (quando.date() - referencia.date()).days
    if dias <= 0:
        return "Hoje"
    if dias == 1:
        return "Amanhã"
    fim_semana = referencia.date() + datetime.timedelta(days=6 - referencia.weekday())
    if quando.date() <= fim_semana:
        return "Esta semana"
    if quando.date() <= fim_semana + datetime.timedelta(days=7):
        return "Semana que vem"
    return "Mais adiante"


# ---------- situação ----------

@dataclass
class Situacao:
    nivel: str          # ok | atencao | risco | neutro
    rotulo: str
    limite: int
    restantes: int
    uso: float          # 0..1+ (fração do limite usada)


def _inteiro(valor):
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return 0


def situacao_faltas(total_aulas, faltas):
    total_aulas, faltas = _inteiro(total_aulas), _inteiro(faltas)
    limite = math.floor(total_aulas * LIMITE_FALTAS)
    restantes = limite - faltas
    if limite <= 0:
        if faltas > 0:
            return Situacao("risco", "Acima do limite", limite, restantes, 1.0)
        return Situacao("neutro", "Sem frequência", limite, restantes, 0.0)
    uso = faltas / limite
    if restantes < 0:
        return Situacao("risco", "Acima do limite", limite, restantes, uso)
    if restantes == 0:
        return Situacao("risco", "No limite", limite, restantes, uso)
    if uso >= 0.75 or restantes <= 2:
        return Situacao("atencao", "Atenção", limite, restantes, uso)
    return Situacao("ok", "Em dia", limite, restantes, uso)


def texto_folga(situacao):
    if situacao.nivel == "neutro":
        return "nenhuma aula registrada"
    if situacao.restantes < 0:
        return f"{plural(-situacao.restantes, 'falta', 'faltas')} acima do limite"
    if situacao.restantes == 0:
        return "nenhuma falta de folga"
    return f"{plural(situacao.restantes, 'falta', 'faltas')} de folga"


# ---------- modelo de exibição ----------

@dataclass
class Entrega:
    titulo: str
    disciplina: str
    quando: datetime.datetime | None
    texto_data: str
    enviada: bool
    aberta: bool = True

    @property
    def estado(self):
        """enviada | pendente (aberta, sem envio) | perdida (encerrou sem envio)."""
        if self.enviada:
            return "enviada"
        return "pendente" if self.aberta else "perdida"


@dataclass
class Avaliacao:
    unidade: str
    sigla: str
    titulo: str
    valor: float | None
    subtotal: bool
    maximo: float | None = None


@dataclass
class Disciplina:
    nome: str
    nome_original: str
    sigla: str
    aulas: int
    faltas: int
    pontos: float | None
    situacao: Situacao
    entregas: list = field(default_factory=list)
    avaliacoes: list = field(default_factory=list)
    resultado: str = ""
    situacao_sigaa: str = ""
    aulas_registradas: list = field(default_factory=list)

    @property
    def distribuidos(self):
        """Soma do valor máximo das avaliações já corrigidas (None se o SIGAA não informou os valores)."""
        corrigidas = [a for a in self.avaliacoes if not a.subtotal and a.valor is not None]
        if not corrigidas or any(a.maximo is None for a in corrigidas):
            return None
        return round(sum(a.maximo for a in corrigidas), 2)

    @property
    def abertas(self):
        return [e for e in self.entregas if e.aberta]

    @property
    def pendentes(self):
        return [e for e in self.entregas if e.estado == "pendente"]


ORDEM_NIVEL = {"risco": 0, "atencao": 1, "ok": 2, "neutro": 3}


def montar_disciplinas(materias, referencia=None):
    referencia = referencia or agora()
    disciplinas = []
    for nome_original, dados in (materias or {}).items():
        nome = titulo_disciplina(nome_original)
        entregas = []
        for titulo, info in (dados.get("tarefas") or {}).items():
            texto_data = info[0] if len(info) > 0 else ""
            enviada = bool(info[1]) if len(info) > 1 else False
            quando = ler_data_sigaa(texto_data)
            aberta = quando is None or quando >= referencia
            entregas.append(Entrega(str(titulo), nome, quando, str(texto_data), enviada, aberta))
        entregas.sort(key=lambda e: e.quando or datetime.datetime.max)

        notas = dados.get("notas") or {}
        avaliacoes = [
            Avaliacao(a.get("unidade", ""), a.get("sigla", ""), a.get("titulo", ""), a.get("valor"),
                      bool(a.get("subtotal")), a.get("maximo"))
            for a in notas.get("avaliacoes", [])
        ]

        pontos = dados.get("notas_atual")
        pontos = float(pontos) if isinstance(pontos, (int, float)) else None
        disciplinas.append(
            Disciplina(
                nome=nome,
                nome_original=nome_original,
                sigla=sigla(nome),
                aulas=_inteiro(dados.get("total_aulas")),
                faltas=_inteiro(dados.get("total_faltas")),
                pontos=pontos,
                situacao=situacao_faltas(dados.get("total_aulas"), dados.get("total_faltas")),
                entregas=entregas,
                avaliacoes=avaliacoes,
                resultado=notas.get("resultado") or "",
                situacao_sigaa=notas.get("situacao") or "",
                aulas_registradas=list(dados.get("frequencia") or []),
            )
        )
    disciplinas.sort(key=lambda d: (ORDEM_NIVEL[d.situacao.nivel], -d.situacao.uso, d.nome))
    return disciplinas


def todas_entregas(disciplinas):
    """Abertas primeiro (prazo mais próximo no topo), depois encerradas (mais recentes no topo)."""
    itens = [e for d in disciplinas for e in d.entregas]
    abertas = sorted((e for e in itens if e.aberta), key=lambda e: e.quando or datetime.datetime.max)
    encerradas = sorted((e for e in itens if not e.aberta), key=lambda e: e.quando, reverse=True)
    return abertas + encerradas


def saldo_ru(valor):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None
