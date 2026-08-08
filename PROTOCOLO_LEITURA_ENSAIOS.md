# PROTOCOLO_LEITURA_ENSAIOS — Como Ler e Classificar um Exemplar Antes de Registrar

**Documento Guia de Curadoria e Ingestão:** Mantido em conjunto por Prof. Lúcio Fábio Pereira da Silva (ICET/UFAM) e pelos Agentes IAs (Antigravity/Gemini e Claude).  
**Repositório:** `differentiallucio-png/Claude-Chat`  
**Versão:** 1.0.0 (Formalização das Regras de Seleção, Gates de Gênero e Validação de Leituras)

---

## 0. Lição da Correção Anterior

Nenhuma entrada no `BANCO_ENSAIOS.md` pode nascer da memória, de estimativas plausíveis ou da montagem de um exemplo sintético com mimetismo de DOI (como ocorreu no erro da entrada de teste E-001). Todo e qualquer registro deve ser fruto da **leitura integral e minuciosa de um artigo real, publicado e verificado na fonte**.

---

## 1. Seleção de Candidatos

**Entram no banco:**
- Ensaios teóricos, artigos conceituais ou *theory papers* publicados em periódicos com linha editorial consolidada (prioritariamente RBEF, CBEF, BOLEMA, REAMEC, Alexandria e REE-ABENGE, Qualis A no quadriênio vigente).

**NÃO entram no banco:**
- Artigos empíricos de estrutura IMRaD (com coleta e análise de dados de campo/laboratório);
- Revisões sistemáticas ou integrativas da literatura cujo produto principal é o mapeamento bibliométrico/estatístico da própria literatura;
- Relatos de experiência docente ou relatos de extensão.

> *Se houver dúvida sobre o enquadramento de um candidato, aplique o Gate de Gênero (Seção 3) antes de prosseguir.*

---

## 2. Leitura Obrigatória Antes de Qualquer Preenchimento

O agente ou pesquisador deve ler o artigo por inteiro (Introdução, corpo analítico, Conclusão e notas explicatórias/metodológicas). Nenhum campo do schema pode ser preenchido por inferências superficiais a partir apenas do título e do resumo.

---

## 3. Gate de Gênero (Filtros Eliminatórios Pré-Classificação)

Antes de classificar a obra em E1, E2 ou E3, responda rigorosamente à sequência de filtros:

```
GATE 1 — Dados Próprios
O artigo produz conhecimento a partir de dados coletados pelos próprios autores
(entrevista, questionário, observação, experimento, aplicação de teste)?
  ├── SIM ➔ NÃO é candidato a este banco. Descartar.
  └── NÃO ➔ Seguir para o Gate 2.

GATE 2 — Estatuto da Literatura
A literatura é tratada como corpus sistemático de revisão (protocolo de busca,
critérios de inclusão/exclusão, análise bibliométrica/frequencial)?
  ├── SIM ➔ É revisão de literatura, não ensaio teórico. Descartar deste banco.
  └── NÃO ➔ A literatura é mobilizada seletivamente para construir e sustentar a tese/argumento ➔ SEGUIR PARA O REGISTRO.
```

---

## 4. Classificação E1 / E2 / E3

Com o candidato aprovado no Gate de Gênero, determine o registro taxonômico predominante:

* **E1 — Analítico-Conceitual:** Tese explícita enunciada nas seções iniciais, contribuição teórica/metodológica claramente demarcada e conclusão assertiva sobre o que foi estabelecido.
* **E2 — Reflexivo-Ensaístico:** Tradição Meneghetti / Adorno / Benjamin. Exploração conceitual aberta, estilo fluido, fechamento não-dogmático; convida o leitor à reflexão em vez de declarar um resultado definitivo.
* **E3 — Híbrido Acadêmico:** Liberdade ensaística real na condução das ideias, porém sob exigências editoriais explícitas (subseções delimitadas, nota metodológica, seção formal de implicações).

> *Se o artigo apresentar traços de mais de um registro, registre o predominante e indique o secundário no campo de Nota de Padrão. Não force pureza tipológica.*

---

## 5. Explicitação Metodológica (M0 a M3)

Determine o nível de transparência procedural demonstrado na prosa:

* **M0:** Sem seção nem parágrafo dedicado à metodologia; o percurso analítico é totalmente dissolvido na escrita.
* **M1:** 1 a 2 parágrafos de nota de percurso, geralmente ao final da Introdução, justificando o recorte ou a rota.
* **M2:** Subseção com critérios de seleção de autores/corpus e delimitação da lente teórica.
* **M3:** Seção formal e autônoma de metodologia.

> *Classifique pelo que o artigo EFETIVAMENTE FAZ na prática, não pelo rótulo que o autor deu à seção. Se houver incoerência entre o título da seção e sua execução real, registre o nível real e reporte a divergência na Nota de Padrão.*

---

## 6. Verificação de DOI (Passo a Passo Obrigatório)

1. Localizar o DOI no PDF original ou na página oficial do periódico (NUNCA puxar da memória).
2. Confirmar a resolução do DOI em `https://doi.org/[DOI]` ou via Crossref (`https://search.crossref.org`), checando se o título, autores, ano e volume retornados batem 100% com o artigo analisado.
3. Se o DOI não resolver ou os metadados apresentarem divergência, **NÃO registrar a entrada**. Reportar a inconsistência.
4. **JAMAIS construir um DOI por analogia** de prefixo/sufixo com outros artigos do mesmo periódico.

---

## 7. Preenchimento do Schema

Preencher integralmente o schema oficial definido em `PROTOCOLO_BANCO_ENSAIOS.md`. É vedado adicionar ou remover campos sem proposta prévia ao Prof. Lúcio Fábio.

---

## 8. Processo por Lote

- Processar no máximo **3 a 5 artigos por sessão de leitura**, executando os Passos 2 a 7 completos para cada obra antes de iniciar a próxima.
- Ao final de cada lote, apresentar o sumário das entradas adicionadas com seus respectivos DOIs e status de verificação no Crossref antes de realizar o commit final.

---

## 9. Casos de Fronteira e Feedback

Artigos que gerem dúvida no Gate 2 ou que sugiram a necessidade de novos campos devem ser reportados ao Prof. Lúcio como casos de fronteira para deliberação, evitando classificações forçadas.
