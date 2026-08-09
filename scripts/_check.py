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
  E8  campo 'name' duplicado entre skills (mesmo nome usado por dois
      diretorios diferentes)
  E9  SKILL.md acima do limite absoluto de 500 linhas (ideal: 300)
  E10 integridade de proveniencia de regras normativas marcadas com
      [RULE: ID]. So se aplica a skills que optaram por marcar regras;
      skill sem nenhuma marcacao [RULE: ...] passa sem erro (regra antiga
      intocada = legacy, sem reprovacao retroativa). Verifica: (a) toda
      tag [RULE: ID] no corpo tem entrada correspondente em
      RULES_PROVENANCE.yml no mesmo diretorio; (b) toda entrada em
      RULES_PROVENANCE.yml tem campo 'provenance' com valor A, B, C, D ou
      legacy; (c) entrada tipo A ou B tem campo 'source' ou 'basis'
      preenchido; (d) entrada tipo C nunca tem 'strength: hard-rule' nem
      equivalente; (e) entrada tipo D nunca tem 'strength: literature-backed'.

Saida: uma linha por achado, prefixada por ERRO, AVISO ou INFO, e um sumario.
Codigo de retorno 1 se houver ERRO, 0 caso contrario.

Este script nao altera nenhum arquivo.

Restaurado em 07/08/2026 a partir da copia recuperavel em
auditor-estilometrico-academico-reference/SKILL.md. Docstring corrigido
nesta restauracao: documentava apenas E1-E7 embora o corpo ja implementasse
E8 e E9 desde a versao anterior. Numeracao de E8/E9 preservada, nao
renumerada. E10 acrescentado nesta mesma sessao, apos validacao da
restauracao contra o oraculo de 30/07/2026.
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

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


def valida_provenance(diretorio, corpo):
    """E10 - integridade de proveniencia de regras marcadas com [RULE: ID].

    Politica de transicao: skill sem nenhuma tag [RULE: ...] no corpo passa
    sem erro (legacy, sem reprovacao retroativa). So entra em avaliacao
    quando ha pelo menos uma tag marcada.
    """
    achados = []
    tags = re.findall(r"\[RULE:\s*([A-Za-z0-9_-]+)\]", corpo)
    if not tags:
        return achados

    caminho_yml = os.path.join(BASE, diretorio, "RULES_PROVENANCE.yml")
    if not os.path.isfile(caminho_yml):
        achados.append(("ERRO", "E10 %d tag(s) [RULE: ID] no corpo, mas "
                                 "RULES_PROVENANCE.yml ausente" % len(tags)))
        return achados

    if yaml is None:
        achados.append(("AVISO", "E10 RULES_PROVENANCE.yml presente, mas "
                                  "PyYAML indisponivel neste ambiente para "
                                  "validar o conteudo"))
        return achados

    try:
        with open(caminho_yml, encoding="utf-8") as f:
            dados = yaml.safe_load(f) or {}
    except Exception as e:
        achados.append(("ERRO", "E10 RULES_PROVENANCE.yml malformado: %s" % e))
        return achados

    regras = dados.get("rules", dados)
    if not isinstance(regras, dict):
        achados.append(("ERRO", "E10 RULES_PROVENANCE.yml sem mapa de regras "
                                 "legivel"))
        return achados

    tipos_validos = {"A", "B", "C", "D", "legacy"}
    for tag in tags:
        entrada = regras.get(tag)
        if entrada is None:
            achados.append(("ERRO", "E10 tag [RULE: %s] no corpo sem entrada "
                                     "em RULES_PROVENANCE.yml" % tag))
            continue
        prov = str(entrada.get("provenance", "")).strip()
        if prov not in tipos_validos:
            achados.append(("ERRO", "E10 regra %s com provenance invalido "
                                     "'%s' (esperado A/B/C/D/legacy)"
                            % (tag, prov)))
            continue
        strength = str(entrada.get("strength", "")).strip().lower()
        strength_norm = re.sub(r"[_\s]+", "-", strength)
        if prov in ("A", "B") and not (entrada.get("source") or entrada.get("basis")):
            achados.append(("ERRO", "E10 regra %s tipo %s sem campo 'source' "
                                     "ou 'basis'" % (tag, prov)))
        if prov == "C" and strength_norm == "hard-rule":
            achados.append(("ERRO", "E10 regra %s tipo C marcada como "
                                     "hard-rule (pista nao verificada nao "
                                     "pode sustentar regra dura sozinha)" % tag))
        if prov == "D" and strength_norm == "literature-backed":
            achados.append(("ERRO", "E10 regra %s tipo D apresentada como "
                                     "literature-backed (heuristica interna "
                                     "nao e conclusao da literatura)" % tag))

    return achados


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

    linhas = texto.count("\n") + 1
    # E9: limite estabelecido pelo proprio criador-skills (secao 2.3):
    # menos de 300 linhas idealmente, maximo absoluto 500.
    if linhas > 500:
        achados.append(("ERRO", "E9 SKILL.md com %d linhas, acima do maximo "
                                "absoluto de 500; extrair para REFERENCE.md"
                        % linhas))
    elif linhas > 300:
        achados.append(("INFO", "E9 SKILL.md com %d linhas, acima do ideal de "
                                "300" % linhas))

    achados.extend(valida_provenance(diretorio, corpo))

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