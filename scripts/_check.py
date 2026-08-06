#!/usr/bin/env python3
"""
_check.py - Validacao mecanica do ecossistema TEAA (candidato C4)

Uso:
    python3 /mnt/skills/user/_check.py              # audita todas as skills
    python3 /mnt/skills/user/_check.py nome-skill   # audita uma skill

O que verifica, por skill:
  E1  frontmatter YAML presente e delimitado por --- no inicio do arquivo
  E2  campo 'name' presente e igual ao nome do diretorio
  E3  campo 'description' presente
  E4  description abaixo de 1024 caracteres (contagem normalizada E bruta;
      a zona entre as duas contagens e reportada como AVISO, nao como erro,
      porque nao se sabe qual contagem o painel de upload aplica)
  E5  campo 'version' presente no frontmatter
  E6  coerencia entre a versao do frontmatter e a primeira versao mencionada
      no corpo do arquivo (padrao 'v1.2', 'versao 1.2', 'v2.6')
  E7  cercas de codigo ``` em numero par

Saida: uma linha por achado, prefixada por ERRO ou AVISO, e um sumario.
Codigo de retorno 1 se houver ERRO, 0 caso contrario.

Este script nao altera nenhum arquivo.
"""

import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
LIMITE = 1024
ALERTA_PREVENTIVO = 900

# Componentes que nao sao skills acionaveis: bancos de dados, placeholders,
# contratos e arquivos de referencia consumidos por outra skill. Ficam isentos
# de E3 (description) e E5 (version), porque nunca sao acionados por gatilho.
EXCECOES = {
    "banco-ensaios-placeholder",
    "orquestrador-academico-reference",
    "portao-de-ingestao-textual-contrato",
    "perfil8-ground-truth",
}


def frontmatter(texto):
    m = re.match(r"^---\r?\n(.*?)\r?\n---", texto, re.S)
    return m.group(1) if m else None


def campo(fm, nome):
    """Extrai um campo do frontmatter, incluindo blocos multilinha (> ou |)."""
    padrao = r"^%s:\s*(.*?)(?=^[A-Za-z_][A-Za-z0-9_-]*:\s|\Z)" % re.escape(nome)
    m = re.search(padrao, fm, re.S | re.M)
    if not m:
        return None
    v = m.group(1)
    v = re.sub(r"^[>|][-+]?\s*", "", v.strip())
    return v


def versao_no_corpo(corpo):
    """Heuristica deliberadamente conservadora.

    So considera linhas AUTORREFERENCIAIS: titulo (#) ou linha iniciada por
    'Versao'. Ignora linhas com crase, porque ali a versao costuma ser a de
    OUTRA skill citada ('`template-manifesto` v1.2'), nao a desta.
    Retorna a lista de versoes encontradas na primeira linha candidata.
    """
    for linha in corpo[:4000].splitlines():
        L = linha.strip()
        if "`" in L:
            continue
        rotulo = re.match(r"^\*{0,2}\s*vers[aã]o\b", L, re.I)
        if rotulo:
            # Linha rotulada: '**Versao:** 1.0.0', 'Versao 1.2'. O numero vem
            # solto, sem prefixo 'v', e pode haver ':' e '**' no meio.
            vs = re.findall(r"\b([0-9]+(?:\.[0-9]+)+)", L)
            if vs:
                return vs
            continue
        if L.startswith("#"):
            vs = re.findall(r"\bv(?:ers[aã]o\s*)?([0-9]+(?:\.[0-9]+)+)", L, re.I)
            if vs:
                return vs
    return None


def normalizar_versao(v):
    """1.1 vira (1,1,0); 1.1.7 vira (1,1,7). Sem isso, um startswith ingenuo
    trata 1.1 e 1.1.7 como compativeis e deixa passar divergencia real."""
    try:
        partes = [int(x) for x in v.strip().split(".")]
    except ValueError:
        return None
    return tuple((partes + [0, 0, 0])[:3])


def versao_compativel(frontmatter_ver, versoes_corpo):
    alvo = normalizar_versao(frontmatter_ver)
    if alvo is None:
        return True
    for v in versoes_corpo:
        if normalizar_versao(v) == alvo:
            return True
    return False


def audita(diretorio, nomes_vistos=None):
    achados = []
    caminho = os.path.join(BASE, diretorio, "SKILL.md")
    if not os.path.isfile(caminho):
        return [("ERRO", "SKILL.md ausente")]

    with open(caminho, encoding="utf-8", errors="replace") as f:
        texto = f.read()

    fm = frontmatter(texto)
    if fm is None:
        achados.append(("ERRO", "E1 sem frontmatter YAML delimitado no inicio"))
        return achados
    corpo = texto[texto.index("---", 3) + 3:]

    nome = campo(fm, "name")
    if not nome:
        achados.append(("ERRO", "E2 campo 'name' ausente"))
    else:
        n = nome.strip().strip("\"'")
        if n != diretorio:
            achados.append(("ERRO", "E2 name '%s' difere do diretorio '%s'"
                            % (n, diretorio)))
        if nomes_vistos is not None:
            if n in nomes_vistos:
                achados.append(("ERRO", "E8 name '%s' duplicado (ja usado por "
                                        "'%s')" % (n, nomes_vistos[n])))
            else:
                nomes_vistos[n] = diretorio

    isento = diretorio in EXCECOES
    desc = campo(fm, "description")
    if not desc:
        if not isento:
            achados.append(("ERRO", "E3 campo 'description' ausente"))
        else:
            achados.append(("INFO", "E3 sem description (excecao declarada: "
                                    "componente de dados/referencia)"))
    else:
        bruto = len(desc)
        normal = len(" ".join(desc.split()))
        if normal > LIMITE:
            achados.append(("ERRO", "E4 description %d caracteres normalizados "
                                    "(limite %d)" % (normal, LIMITE)))
        elif bruto > LIMITE:
            achados.append(("AVISO", "E4 description limitrofe: %d bruto / %d "
                                     "normalizado (limite %d)"
                            % (bruto, normal, LIMITE)))
        elif normal > ALERTA_PREVENTIVO:
            achados.append(("INFO", "E4 description em %d caracteres, margem "
                                    "estreita para crescer" % normal))

    ver = campo(fm, "version")
    if not ver:
        if not isento:
            achados.append(("AVISO", "E5 campo 'version' ausente no frontmatter"))
    else:
        ver = ver.strip().strip("\"'")
        vcorpo = versao_no_corpo(corpo)
        if vcorpo and not versao_compativel(ver, vcorpo):
            achados.append(("ERRO", "E6 frontmatter diz version %s, corpo menciona "
                                    "v%s" % (ver, "/v".join(vcorpo))))

    cercas = len(re.findall(r"^```", texto, re.M))
    if cercas % 2:
        achados.append(("ERRO", "E7 cercas de codigo impares (%d)" % cercas))

    # E9: limite estabelecido pelo proprio criador-skills (secao 2.3):
    # menos de 300 linhas idealmente, maximo absoluto 500.
    linhas = texto.count("\n") + 1
    if linhas > 500:
        achados.append(("ERRO", "E9 SKILL.md com %d linhas, acima do maximo "
                                "absoluto de 500; extrair para REFERENCE.md"
                        % linhas))
    elif linhas > 300:
        achados.append(("INFO", "E9 SKILL.md com %d linhas, acima do ideal de "
                                "300" % linhas))

    return achados


def main():
    alvos = sys.argv[1:]
    if not alvos:
        alvos = sorted(d for d in os.listdir(BASE)
                       if os.path.isdir(os.path.join(BASE, d))
                       and not d.startswith(".")
                       and not d.startswith("_"))

    contagem = {"ERRO": 0, "AVISO": 0, "INFO": 0}
    nomes_vistos = {}
    for d in alvos:
        for nivel, msg in audita(d, nomes_vistos):
            print("%-5s %-42s %s" % (nivel, d, msg))
            contagem[nivel] = contagem.get(nivel, 0) + 1

    print("\n%d skills auditadas | %d ERRO | %d AVISO | %d INFO"
          % (len(alvos), contagem["ERRO"], contagem["AVISO"], contagem["INFO"]))
    erros = contagem["ERRO"]
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
