# PROTOCOLO_BANCO_ENSAIOS — Diretrizes de Operação, Curadoria e Consulta do Banco de Ensaios

**Documento Guia:** Mantido em conjunto por Prof. Lúcio Fábio Pereira da Silva (ICET/UFAM) e pelos Agentes IAs (Antigravity/Gemini e Claude).  
**Repositório:** `differentiallucio-png/Claude-Chat`  
**Versão:** 3.0.0 (Atualização da Taxonomia E1/E2/E3 e migração para GitHub)

---

## 1. Finalidade e Princípios Centrais

O **PROTOCOLO_BANCO_ENSAIOS** estabelece as regras de curadoria, inserção e consulta do `BANCO_ENSAIOS.md`. Ele orienta tanto os pesquisadores humanos quanto os assistentes de IA (Claude, Gemini, OpenCode) na utilização de exemplares reais de ensaios teóricos e artigos conceituais publicados em periódicos Qualis A (RBEF, CBEF, BOLEMA, REAMEC, Alexandria, REE-ABENGE, etc.).

### Princípios Fundamentais:
1. **Fidelidade Empírica e Integridade Citacional:** NENHUM DADO BIBLIOGRÁFICO OU DOI PODE SER INVENTADO OU ESTIMADO. Todo exemplar registrado deve ter seu DOI e metadados verificados na fonte original.
2. **Dados Proporcionais são Descritivos, NUNCA Normativos:** As informações de porcentagem (% de Introdução, Desenvolvimento e Conclusão) e quantidade de páginas refletem **apenas o que o autor específico fez**. Elas servem para ilustrar a diversidade de arranjos publicados, e JAMAIS devem ser tratadas como meta rígida ou padrão normativo ("o ensaio deve ter X% de introdução").
3. **Taxonomia Vigente de Registros Ensaísticos (E1, E2, E3):** Substituto oficial da antiga classificação (educacional-padrão vs. filosófico-historiográfico).

---

## 2. Detalhamento dos Campos do Schema

Ao cadastrar ou analisar um ensaio para o banco, os seguintes critérios de classificação devem ser rigorosamente aplicados:

### 2.1. Registro Taxonômico (E1 | E2 | E3)
* **E1 (Analítico-Conceitual):** Ensaio com tese explícita enunciada logo nas seções iniciais, contribuição teórica/metodológica claramente demarcada, estrutura argumentativa fortemente ancorada em conceitos delimitados e conclusões assertivas.
* **E2 (Reflexivo-Ensaístico):** Ensaio de tradição hermenêutica/ensaística clássica (linha Meneghetti / Adorno / Benjamin). Caracteriza-se por exploração conceitual aberta, fechamento não-dogmático, estilo fluido e condução reflexiva.
* **E3 (Híbrido Acadêmico):** Ensaio que combina a liberdade de exploração reflexiva do ensaio clássico com o atendimento a exigências estruturais e editoriais rígidas dos periódicos acadêmicos contemporâneos (subdivisões explícitas, notas de rodapé, delimitação de problema).

### 2.2. Explicitação Metodológica (M0 | M1 | M2 | M3)
* **M0 (Incorporada/Dissolvida):** O ensaio não possui seção nem parágrafo dedicado à "metodologia". Os caminhos analíticos são demonstrados diretamente na própria condução da prosa e no exame dos conceitos.
* **M1 (Nota de Percurso):** O autor insere 1 ou 2 parágrafos (geralmente ao final da Introdução) explicando a rota do ensaio, o recorte adotado ou a escolha dos autores interlocutores.
* **M2 (Procedimentos Analíticos):** Há uma subseção dedicada a detalhar a trajetória argumentativa, os critérios de escolha do corpus/autores e a lente teórica empregada.
* **M3 (Metodologia Plena):** O ensaio adota uma seção formal de metodologia (frequentemente presente em periódicos que exigem a estrutura padrão mesmo para artigos teóricos).

---

## 3. Protocolo de Inserção de Novas Entradas

Quando o Gemini, Claude ou o autor identificarem um ensaio teórico/conceitual publicado de alta relevância:

1. **Passo 1 — Validação de Fonte:** Confirmar se a obra foi publicada em periódico com linha editorial consolidada e verificar o DOI diretamente via Crossref ou site da revista.
2. **Passo 2 — Extração dos Dados:** Preencher todos os campos do schema do `BANCO_ENSAIOS.md`.
3. **Passo 3 — Registro no Repositório:** Adicionar o novo bloco ao arquivo `BANCO_ENSAIOS.md` no repositório `differentiallucio-png/Claude-Chat` e realizar o commit/push.

---

## 4. Protocolo de Consulta Durante a Produção (Modo Escrita)

Quando um agente de IA (Claude Chat, Claude Code, Gemini/Antigravity) for acionado para auxiliar na concepção, estruturação ou revisão de um ensaio acadêmico:

1. **Consulta aos Exemplares Comparáveis:** O agente deve consultar o `BANCO_ENSAIOS.md` no repositório GitHub buscando exemplares da mesma área ou com referencial teórico/registro equivalente (E1, E2 ou E3).
2. **Uso de Padrões (Sem Plágio):** O banco fornece **inspiração de arquitetura e estratégias retóricas**, NUNCA conteúdo para reprodução. O agente deve observar como ensaios similares resolveram a transição entre seções, a enunciação da tese ou o fechamento.
3. **Feedback e Evolução de Regras:** Caso o agente ou o pesquisador identifique a necessidade de ajustes no schema, inclusão de novos campos ou novos códigos, essa proposta deve ser repassada ao Prof. Lúcio Fábio para avaliação antes de ser oficializada no TEAA.
