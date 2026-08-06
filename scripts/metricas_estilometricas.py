#!/usr/bin/env python3
"""Métricas estilométricas interpretáveis para textos acadêmicos em português.

O script NÃO detecta autoria por IA. Ele mede monotonia, repetição, concentração
lexical, nominalizações e desvio em relação a um corpus autoral de referência.

Uso:
  python metricas_estilometricas.py analyze artigo.docx --out-dir saida
  python metricas_estilometricas.py profile texto1.docx texto2.docx --output perfil.json
  python metricas_estilometricas.py compare artigo.docx --profile perfil.json --out-dir saida
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*", re.UNICODE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\"“])")
QUOTE_RE = re.compile(r'[“\"]([^“\"]{1,1000})[”\"]')

PARAGRAPH_CONNECTORS = [
    "além disso", "ademais", "contudo", "no entanto", "todavia", "portanto",
    "por conseguinte", "nesse sentido", "dessa forma", "desse modo", "assim",
    "com efeito", "de resto", "em contrapartida", "por outro lado", "ainda assim",
]

FOCAL_WORDS_PT = {
    "abrangente", "crucial", "essencial", "fundamental", "inovador", "relevante",
    "robusto", "significativo", "transformador", "multifacetado", "panorama",
    "cenário", "paisagem", "mosaico", "jornada", "ecossistema", "sinergia",
    "destacar", "ressaltar", "enfatizar", "evidenciar", "fomentar", "cultivar",
    "aprimorar", "potencializar", "navegar", "transcender", "impulsionar",
    "desempenha", "contribui", "contribuir", "promover", "possibilitar",
}

FUNCTION_WORDS_PT = {
    "a", "à", "ao", "aos", "as", "às", "o", "os", "um", "uma", "uns", "umas",
    "de", "da", "das", "do", "dos", "em", "na", "nas", "no", "nos", "por",
    "para", "com", "sem", "sob", "sobre", "entre", "e", "ou", "mas", "que",
    "se", "como", "quando", "onde", "porque", "embora", "ainda", "já", "não",
    "mais", "menos", "muito", "pouco", "também", "contudo", "portanto", "assim",
    "isso", "isto", "esse", "essa", "esses", "essas", "este", "esta", "estes",
    "estas", "ele", "ela", "eles", "elas", "seu", "sua", "seus", "suas",
}

META_PHRASES = [
    "é importante notar", "vale ressaltar", "cabe destacar", "convém observar",
    "nesse contexto", "no que se refere a", "no que tange a", "tendo em vista que",
    "de forma geral", "em linhas gerais", "em suma", "em síntese",
]

ANTITHESIS_PATTERNS = [
    re.compile(r"\bnão\s+(?:apenas|somente)\b.{0,120}\bmas\s+(?:também\s+)?", re.I),
    re.compile(r"\bnão\s+se\s+trata\s+de\b.{0,120}\b(?:mas|e sim)\b", re.I),
    re.compile(r"\bnão\s+é\b.{0,100}\b(?:mas|é)\b", re.I),
]

@dataclass
class ParagraphMetrics:
    index: int
    words: int
    sentences: int
    mean_sentence_words: float
    nominal_acao_mento_per_1000: float
    nominal_dade_per_1000: float
    focal_words_per_1000: float
    repeated_4gram_ratio: float
    opening: str
    connector_opening: str
    metadiscourse_hits: int
    antithesis_hits: int
    text_preview: str


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize_word(word: str) -> str:
    return strip_accents(word.lower())


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def normalized_words(text: str) -> list[str]:
    return [normalize_word(w) for w in words(text)]


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text)
    return [p.strip() for p in parts if len(words(p)) >= 2]


def load_text(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("python-docx é necessário para ler .docx") from exc
        doc = Document(path)
        return [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    if suffix in {".txt", ".md"}:
        raw = path.read_text(encoding="utf-8")
        return [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
    raise ValueError(f"Formato não suportado: {suffix}")


def remove_references(paragraphs: list[str]) -> list[str]:
    for i, p in enumerate(paragraphs):
        norm = normalize_word(p).strip()
        if norm in {"referencias", "references", "bibliografia"}:
            return paragraphs[:i]
    return paragraphs


def mask_quotes(text: str) -> str:
    return QUOTE_RE.sub(" [CITACAO_DIRETA] ", text)


def is_probable_heading(p: str) -> bool:
    ws = words(p)
    if not ws or len(ws) > 14:
        return False
    if p.endswith(('.', '?', '!', ';', ':')):
        return False
    title_case = sum(1 for w in ws if w[:1].isupper()) / max(1, len(ws))
    return title_case >= 0.6 or p.isupper()


def mean(values: Sequence[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def stdev(values: Sequence[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if total <= 1:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counter.values() if c)


def ngrams(tokens: Sequence[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i+n]) for i in range(max(0, len(tokens)-n+1))]


def repeated_ngram_ratio(tokens: Sequence[str], n: int) -> float:
    grams = ngrams(tokens, n)
    if not grams:
        return 0.0
    counts = Counter(grams)
    repeated_occurrences = sum(c for c in counts.values() if c > 1)
    return repeated_occurrences / len(grams)


def cosine_counter(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[x] * b[x] for x in common)
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    return safe_div(dot, na * nb)


def lag1_autocorrelation(values: Sequence[float]) -> float:
    if len(values) < 3:
        return 0.0
    x = values[:-1]
    y = values[1:]
    mx, my = mean(x), mean(y)
    num = sum((a-mx)*(b-my) for a, b in zip(x, y))
    den = math.sqrt(sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y))
    return safe_div(num, den)


def lexical_metrics(tokens: list[str]) -> dict[str, float]:
    n = len(tokens)
    counts = Counter(tokens)
    v = len(counts)
    hapax = sum(1 for c in counts.values() if c == 1)
    ttr = safe_div(v, n)
    root_ttr = safe_div(v, math.sqrt(n)) if n else 0.0
    herdan_c = safe_div(math.log(v), math.log(n)) if n > 1 and v > 0 else 0.0
    maas = safe_div(math.log(n) - math.log(v), (math.log(n) ** 2)) if n > 1 and v > 0 else 0.0
    return {
        "type_token_ratio": ttr,
        "root_ttr": root_ttr,
        "herdan_c": herdan_c,
        "maas": maas,
        "hapax_ratio": safe_div(hapax, v),
        "vocabulary_size": v,
    }


def detect_connector_opening(text: str) -> str:
    norm = normalize_word(text)
    for c in PARAGRAPH_CONNECTORS:
        if norm.startswith(normalize_word(c)):
            return c
    return ""


def paragraph_opening(text: str, n: int = 4) -> str:
    return " ".join(normalized_words(text)[:n])


def paragraph_metrics(index: int, text: str) -> ParagraphMetrics:
    toks = normalized_words(text)
    sents = split_sentences(text)
    sent_lens = [len(words(s)) for s in sents]
    n = len(toks)
    nominal_am = sum(1 for t in toks if t.endswith("cao") or t.endswith("coes") or t.endswith("mento") or t.endswith("mentos"))
    nominal_d = sum(1 for t in toks if t.endswith("dade") or t.endswith("dades"))
    focal = sum(1 for t in toks if t in {normalize_word(x) for x in FOCAL_WORDS_PT})
    norm_text = normalize_word(text)
    meta_hits = sum(norm_text.count(normalize_word(p)) for p in META_PHRASES)
    anti_hits = sum(len(p.findall(text)) for p in ANTITHESIS_PATTERNS)
    return ParagraphMetrics(
        index=index,
        words=n,
        sentences=len(sents),
        mean_sentence_words=round(mean(sent_lens), 3),
        nominal_acao_mento_per_1000=round(safe_div(nominal_am * 1000, n), 3),
        nominal_dade_per_1000=round(safe_div(nominal_d * 1000, n), 3),
        focal_words_per_1000=round(safe_div(focal * 1000, n), 3),
        repeated_4gram_ratio=round(repeated_ngram_ratio(toks, 4), 4),
        opening=paragraph_opening(text),
        connector_opening=detect_connector_opening(text),
        metadiscourse_hits=meta_hits,
        antithesis_hits=anti_hits,
        text_preview=text[:220],
    )


def analyze_paragraphs(paragraphs: list[str], mask_direct_quotes: bool = True) -> dict:
    prose = [p for p in paragraphs if not is_probable_heading(p)]
    metric_texts = [mask_quotes(p) if mask_direct_quotes else p for p in prose]
    full_text = "\n\n".join(metric_texts)
    toks = normalized_words(full_text)
    sents = [s for p in metric_texts for s in split_sentences(p)]
    sent_lens = [len(words(s)) for s in sents]
    para_lens = [len(words(p)) for p in metric_texts]
    pmetrics = [paragraph_metrics(i+1, p) for i, p in enumerate(metric_texts)]

    openings = [paragraph_opening(p) for p in metric_texts if len(words(p)) >= 4]
    opener_counts = Counter(openings)
    connectors = Counter(pm.connector_opening for pm in pmetrics if pm.connector_opening)
    punctuation = Counter(ch for ch in full_text if ch in ".,;:!?()[]—–-")
    fwords = Counter(t for t in toks if t in FUNCTION_WORDS_PT)

    nominal_am = sum(1 for t in toks if t.endswith("cao") or t.endswith("coes") or t.endswith("mento") or t.endswith("mentos"))
    nominal_d = sum(1 for t in toks if t.endswith("dade") or t.endswith("dades"))
    focal_counts = Counter(t for t in toks if t in {normalize_word(x) for x in FOCAL_WORDS_PT})

    # Variação de coesão local, por similaridade lexical entre sentenças adjacentes.
    sent_counters = [Counter(t for t in normalized_words(s) if t not in FUNCTION_WORDS_PT) for s in sents]
    adjacent_sim = [cosine_counter(a, b) for a, b in zip(sent_counters, sent_counters[1:])]

    lex = lexical_metrics(toks)
    total_words = len(toks)
    metrics = {
        "words": total_words,
        "sentences": len(sents),
        "paragraphs": len(metric_texts),
        "sentence_words_mean": round(mean(sent_lens), 4),
        "sentence_words_median": round(statistics.median(sent_lens), 4) if sent_lens else 0.0,
        "sentence_words_sd": round(stdev(sent_lens), 4),
        "sentence_words_cv": round(safe_div(stdev(sent_lens), mean(sent_lens)), 4),
        "sentence_length_lag1_autocorrelation": round(lag1_autocorrelation(sent_lens), 4),
        "short_sentence_ratio_lt_9": round(safe_div(sum(x < 9 for x in sent_lens), len(sent_lens)), 4),
        "long_sentence_ratio_gt_35": round(safe_div(sum(x > 35 for x in sent_lens), len(sent_lens)), 4),
        "paragraph_words_mean": round(mean(para_lens), 4),
        "paragraph_words_sd": round(stdev(para_lens), 4),
        "paragraph_words_cv": round(safe_div(stdev(para_lens), mean(para_lens)), 4),
        "paragraph_opening_diversity": round(safe_div(len(opener_counts), len(openings)), 4),
        "top_paragraph_opening_share": round(safe_div(opener_counts.most_common(1)[0][1], len(openings)), 4) if openings else 0.0,
        "connector_opening_ratio": round(safe_div(sum(connectors.values()), len(metric_texts)), 4),
        "top_connector_share": round(safe_div(connectors.most_common(1)[0][1], sum(connectors.values())), 4) if connectors else 0.0,
        "nominal_acao_mento_per_1000": round(safe_div(nominal_am * 1000, total_words), 4),
        "nominal_dade_per_1000": round(safe_div(nominal_d * 1000, total_words), 4),
        "focal_words_per_1000": round(safe_div(sum(focal_counts.values()) * 1000, total_words), 4),
        "repeated_bigram_ratio": round(repeated_ngram_ratio(toks, 2), 4),
        "repeated_trigram_ratio": round(repeated_ngram_ratio(toks, 3), 4),
        "repeated_4gram_ratio": round(repeated_ngram_ratio(toks, 4), 4),
        "punctuation_per_1000": round(safe_div(sum(punctuation.values()) * 1000, total_words), 4),
        "punctuation_entropy": round(entropy(punctuation), 4),
        "function_word_entropy": round(entropy(fwords), 4),
        "adjacent_sentence_similarity_mean": round(mean(adjacent_sim), 4),
        "adjacent_sentence_similarity_sd": round(stdev(adjacent_sim), 4),
        "metadiscourse_hits": sum(pm.metadiscourse_hits for pm in pmetrics),
        "antithesis_hits": sum(pm.antithesis_hits for pm in pmetrics),
        **{k: round(v, 4) if isinstance(v, float) else v for k, v in lex.items()},
    }

    top_ngrams = {}
    for n in (2, 3, 4):
        counts = Counter(ngrams(toks, n))
        top_ngrams[str(n)] = [
            {"ngram": " ".join(g), "count": c}
            for g, c in counts.most_common(20) if c > 1
        ][:10]

    return {
        "metrics": metrics,
        "paragraphs": [asdict(pm) for pm in pmetrics],
        "top_openings": [{"opening": k, "count": v} for k, v in opener_counts.most_common(10)],
        "connector_openings": dict(connectors),
        "focal_words": dict(focal_counts.most_common()),
        "punctuation": dict(punctuation),
        "top_repeated_ngrams": top_ngrams,
        "notes": [
            "Estas métricas não estimam probabilidade de autoria por IA.",
            "Valores devem ser comparados, preferencialmente, a um corpus autêntico do mesmo autor e gênero.",
            "Citações diretas são mascaradas por padrão; a lista de referências é excluída por padrão.",
        ],
    }


def robust_profile(reports: list[dict], sources: list[str], genre: str = "") -> dict:
    metric_names = sorted(set.intersection(*(set(r["metrics"].keys()) for r in reports)))
    stats = {}
    for name in metric_names:
        vals = [r["metrics"][name] for r in reports if isinstance(r["metrics"].get(name), (int, float))]
        if not vals:
            continue
        med = statistics.median(vals)
        absdev = [abs(x-med) for x in vals]
        mad = statistics.median(absdev)
        stats[name] = {
            "median": med,
            "mad": mad,
            "min": min(vals),
            "max": max(vals),
            "n": len(vals),
        }
    return {
        "profile_type": "perfil_estilometrico_autoral_robusto",
        "genre": genre,
        "sources": sources,
        "documents": len(reports),
        "total_words": sum(r["metrics"]["words"] for r in reports),
        "metrics": stats,
        "caveat": "Perfil operacional interno; não é modelo biométrico nem prova de autoria.",
    }


def compare_to_profile(report: dict, profile: dict, z_threshold: float = 2.5) -> list[dict]:
    out = []
    for name, ref in profile.get("metrics", {}).items():
        val = report["metrics"].get(name)
        if not isinstance(val, (int, float)):
            continue
        med = ref.get("median", 0.0)
        mad = ref.get("mad", 0.0)
        scale = 1.4826 * mad
        if scale == 0:
            rz = 0.0 if val == med else None
        else:
            rz = (val-med)/scale
        out.append({
            "metric": name,
            "target": val,
            "profile_median": med,
            "profile_mad": mad,
            "robust_z": round(rz, 4) if rz is not None else None,
            "flag": bool(rz is not None and abs(rz) >= z_threshold),
        })
    return sorted(out, key=lambda x: abs(x["robust_z"]) if x["robust_z"] is not None else -1, reverse=True)


def write_report_files(report: dict, out_dir: Path, prefix: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{prefix}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    paragraphs = report.get("paragraphs", [])
    if paragraphs:
        with (out_dir / f"{prefix}_paragrafos.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(paragraphs[0].keys()))
            writer.writeheader()
            writer.writerows(paragraphs)

    m = report["metrics"]
    md = [f"# Relatório estilométrico: {prefix}", "", "## Métricas globais", ""]
    for k, v in m.items():
        md.append(f"- **{k}:** {v}")
    md.extend(["", "## Observações", ""])
    md.extend(f"- {n}" for n in report.get("notes", []))
    if report.get("profile_comparison"):
        md.extend(["", "## Desvios em relação ao perfil autoral", ""])
        for item in report["profile_comparison"]:
            if item["flag"]:
                md.append(f"- **{item['metric']}**: alvo={item['target']}; mediana={item['profile_median']}; z robusto={item['robust_z']}")
    (out_dir / f"{prefix}.md").write_text("\n".join(md), encoding="utf-8")


def prepare(path: Path, include_references: bool, mask_direct_quotes: bool) -> dict:
    paragraphs = load_text(path)
    if not include_references:
        paragraphs = remove_references(paragraphs)
    report = analyze_paragraphs(paragraphs, mask_direct_quotes=mask_direct_quotes)
    report["source_file"] = str(path)
    return report


def command_analyze(args: argparse.Namespace) -> int:
    path = Path(args.input)
    report = prepare(path, args.include_references, not args.keep_quotes)
    prefix = args.prefix or path.stem
    write_report_files(report, Path(args.out_dir), prefix)
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    return 0


def command_profile(args: argparse.Namespace) -> int:
    reports = [prepare(Path(p), args.include_references, not args.keep_quotes) for p in args.inputs]
    profile = robust_profile(reports, args.inputs, genre=args.genre or "")
    Path(args.output).write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Perfil salvo em {args.output}: {profile['documents']} documentos, {profile['total_words']} palavras.")
    return 0


def command_compare(args: argparse.Namespace) -> int:
    path = Path(args.input)
    report = prepare(path, args.include_references, not args.keep_quotes)
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    report["profile_comparison"] = compare_to_profile(report, profile, z_threshold=args.z_threshold)
    report["profile_file"] = args.profile
    prefix = args.prefix or f"{path.stem}_comparado"
    write_report_files(report, Path(args.out_dir), prefix)
    flags = [x for x in report["profile_comparison"] if x["flag"]]
    print(json.dumps(flags, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--include-references", action="store_true", help="Inclui a lista de referências nas métricas.")
    common.add_argument("--keep-quotes", action="store_true", help="Não mascara citações diretas entre aspas.")

    a = sub.add_parser("analyze", parents=[common])
    a.add_argument("input")
    a.add_argument("--out-dir", default="saida_estilometria")
    a.add_argument("--prefix", default="")
    a.set_defaults(func=command_analyze)

    pr = sub.add_parser("profile", parents=[common])
    pr.add_argument("inputs", nargs="+")
    pr.add_argument("--output", required=True)
    pr.add_argument("--genre", default="")
    pr.set_defaults(func=command_profile)

    c = sub.add_parser("compare", parents=[common])
    c.add_argument("input")
    c.add_argument("--profile", required=True)
    c.add_argument("--out-dir", default="saida_estilometria")
    c.add_argument("--prefix", default="")
    c.add_argument("--z-threshold", type=float, default=2.5)
    c.set_defaults(func=command_compare)
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
