---
name: ingestor-banco-ensaios
version: 1.0.0
description: >
  Curador e ingestor oficial de ensaios teóricos para o BANCO_ENSAIOS.md no repositório GitHub (differentiallucio-png/Claude-Chat).
  Realiza triagem por Gates de Gênero, leitura analítica (E1/E2/E3, M0-M3), verificação obrigatória de DOI via Crossref/DOI.org, e faz a ingestão via commit direto no repositório.
  Use SEMPRE que o usuário pedir para "ler este ensaio para o banco", "adicionar este artigo ao banco de padrões", "ingerir este ensaio", "processar lote de ensaios", "classifique e registre este ensaio", ou "atualizar o BANCO_ENSAIOS".
---

# Ingestor e Curador do Banco de Ensaios (`ingestor-banco-ensaios`)

## Visão Geral

Esta skill rege a rotina completa de **triagem, leitura, extração e registro de ensaios teóricos reais** no repositório oficial `differentiallucio-png/Claude-Chat`. Ela garante a aplicação rigorosa do `PROTOCOLO_BANCO_ENSAIOS.md` e do `PROTOCOLO_LEITURA_ENSAIOS.md`, impedindo a inserção de dados alucinados ou DOIs não-verificados.

---

## Fluxo Operacional de Ingestão (Passo a Passo)

### Passo 1 — Triagem e Gates de Gênero
Antes de iniciar a leitura detalhada, submeter a obra aos dois gates eliminatórios:

```
GATE 1 — Dados Próprios
O artigo produz conhecimento a partir de dados coletados pelos próprios autores (entrevistas, questionários, testes, experimentos)?
  ├── SIM ➔ REJEITAR (não é ensaio teórico).
  └── NÃO ➔ Avançar para o Gate 2.

GATE 2 — Estatuto da Literatura
A literatura é tratada como corpus de revisão sistemática (análise estatística, busca bibliométrica)?
  ├── SIM ➔ REJEITAR (é revisão de literatura).
  └── NÃO ➔ Literatura mobilizada seletivamente para sustentar argumento ➔ CANDIDATO APROVADO.
```

---

### Passo 2 — Leitura Analítica e Classificação
Ler a obra integralmente e extrair os 17 campos do schema:

1. **Registro Taxonômico:**
   - **E1 (Analítico-Conceitual):** Tese explícita enunciada no início, contribuição teórica demarcada, conclusões assertivas.
   - **E2 (Reflexivo-Ensaístico):** Linha Meneghetti/Adorno/Benjamin; exploração reflexiva aberta, fechamento não-dogmático.
   - **E3 (Híbrido Acadêmico):** Liberdade ensaística real combinada com subdivisões editoriais rígidas.
2. **Explicitação Metodológica:**
   - **M0:** Percurso totalmente dissolvido na prosa.
   - **M1:** 1 a 2 parágrafos de nota de percurso ao final da Introdução.
   - **M2:** Subseção dedicada aos critérios de seleção e lente teórica.
   - **M3:** Seção formal de metodologia.
3. **Proporção da Estrutura:**
   - Registrar as proporções reais observadas no exemplar (% Introdução / % Desenvolvimento / % Conclusão).  
   - *Nota obrigatória: Dado estritamente descritivo deste artigo, nunca norma.*

---

### Passo 3 — Verificação Obrigatória de DOI (Anti-Alucinação)
1. Extrair o DOI do PDF ou do site oficial da revista.
2. Fazer requisição de confirmação no Crossref (`https://search.crossref.org`) ou `https://doi.org/[DOI]`.
3. Validar se o título, autores e periódico retornados correspondem 100% à obra analisada.
4. **Se o DOI não resolver ou não bater exato, NUNCA registrar a entrada.**

---

### Passo 4 — Formatação da Entrada no Schema

Gerar a entrada no formato exato:

```markdown
### [ID] - [Título do Ensaio Publicado]

- **ID / Título:** [ID] - [Título Completo]
- **DOI:** [DOI Verificado no Crossref]
- **Periódico, Qualis e Ano:** [Nome do Periódico | Qualis A... | Ano]
- **Área / Subtema:** [Área / Subtema]
- **Referencial Teórico Central:** [Autores/Teorias centrais]
- **Registro Taxonômico:** [E1 | E2 | E3]
- **Operação Intelectual Dominante:** [definir | comparar | criticar | etc.]
- **Tipo de Contribuição:** [teórica | prática | metodológica | didática]
- **Papel da Literatura:** [interlocução seletiva vs. objeto de revisão]
- **Explicitação Metodológica:** [M0 | M1 | M2 | M3]
- **Arquitetura do Desenvolvimento:** [Descrição em prosa livre da estrutura]
- **Modo de Fechamento Predominante:** [Síntese integradora / Abertura de agenda / Provocação]
- **Extensão Total (páginas):** [Nº páginas]
- **Proporção da Estrutura (Descritivo do exemplar):** [% Intr | % Dev | % Conc] *(Descritivo do exemplar, nunca norma)*
- **Limitações Declaradas:** [sim | não | retóricas]
- **Nota de Padrão (1-3 frases):** [O que este exemplar faz bem que orienta novos ensaios]
```

---

### Passo 5 — Apresentação e Ingestão via GitHub

1. Apresentar o lote de entradas analisadas ao usuário com a confirmação da verificação de DOI no Crossref.
2. Adicionar as novas entradas ao arquivo `BANCO_ENSAIOS.md` na pasta clonada.
3. Executar o commit e push para o repositório `differentiallucio-png/Claude-Chat`:
   ```bash
   git add BANCO_ENSAIOS.md
   git commit -m "feat(banco-ensaios): adicionar [N] novos exemplares verificados"
   git push origin main
   ```
4. Fornecer os links de confirmação atualizados.

---

## O Que Esta Skill NÃO Faz

- Não inventa nem estima DOIs ou metadados bibliográficos.
- Não cadastra artigos empíricos (IMRaD) nem revisões sistemáticas da literatura.
- Não força pureza tipológica quando um artigo possui traços híbridos.
