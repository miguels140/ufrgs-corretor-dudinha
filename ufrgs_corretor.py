
import re
from collections import Counter
from typing import List, Dict, Tuple

CONNECTIVES = [
    "além disso","contudo","portanto","assim","dessa forma","desse modo","no entanto",
    "todavia","entretanto","logo","porém","por conseguinte","em suma","por fim",
    "primeiramente","em primeiro lugar","em segundo lugar","por outro lado","ou seja",
    "nesse sentido","nesse contexto","diante disso","dessa maneira","além do mais"
]

THESIS_MARKERS = [
    "defende-se","sustenta-se","argumenta-se","este texto","neste texto","é necessário",
    "é preciso","portanto","logo","propõe-se","propomos","defendo","sustento","sou de opinião",
]

EXAMPLE_MARKERS = [
    "por exemplo","como exemplo","segundo","de acordo com","dados","pesquisa","ibge","onu",
    "unesco","fundo monetário","banco mundial","constituição","lei","estatuto","artigo",
    "em 20","em 19"
]

ORTHO_TARGETS = {
    "á": "à",
    "a internet": "à internet",
    "a educação": "à educação",
    "a inclusão": "à inclusão",
    "a medida que": "à medida que",
    "seculo": "século",
    "possivel": "possível",
    "economica": "econômica",
    "ultimos": "últimos",
    "voce": "você",
}

def split_sentences(text: str):
    return [s.strip() for s in re.split(r'(?<=[\.\?\!])\s+', text) if s.strip()]

def tokenize(text: str):
    return re.findall(r"[A-Za-zÀ-ÿ\-']+", text.lower())

def type_token_ratio(tokens):
    if not tokens: return 0
    return len(set(tokens))/len(tokens)

def count_paragraphs(text: str) -> int:
    paras = [p for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]
    return len(paras) if paras else (1 if text.strip() else 0)

def has_title(text: str):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines: return False, "", text
    first = lines[0]
    is_title = (len(first) <= 85) and (not first.endswith('.')) and (len(first.split()) >= 3) and first[0].isupper()
    if is_title:
        return True, first, text[text.find(first)+len(first):].strip()
    return False, "", text

def score_expression(text: str):
    detail = {}
    base = 0.0
    
    ortho_penalties = 0
    lowered = text.lower()
    for wrong, right in ORTHO_TARGETS.items():
        occurrences = len(re.findall(r'\b'+re.escape(wrong)+r'\b', lowered))
        if occurrences:
            ortho_penalties += min(occurrences, 3) * 1.5
    if " vc " in lowered or " q " in lowered:
        ortho_penalties += 2
    if re.search(r"\bkkk+\b", lowered):
        ortho_penalties += 2
    ortho_score = max(0, 10 - ortho_penalties)
    detail["Convenções ortográficas"] = round(ortho_score,2)
    base += ortho_score
    
    sents = split_sentences(text)
    if not sents: sents = [text]
    avg_len = sum(len(s.split()) for s in sents)/len(sents)
    long_sents = sum(1 for s in sents if len(s.split()) >= 35)
    no_commas = sum(1 for s in sents if ("," not in s and len(s.split())>20))
    p_pen = 0
    if avg_len > 28: p_pen += 2
    p_pen += long_sents * 1.5 + no_commas * 1.0
    punct_score = max(0, 8 - p_pen)
    detail["Pontuação"] = round(punct_score,2)
    base += punct_score
    
    fragments = sum(1 for s in sents if len(s.split()) < 3)
    runons = sum(1 for s in sents if len(s.split()) >= 50)
    que_ratio = sum(s.lower().split().count("que") for s in sents) / max(1, sum(len(s.split()) for s in sents))
    sm_pen = fragments*1.5 + runons*2 + (3 if que_ratio>0.06 else 0)
    sm_score = max(0, 12 - sm_pen)
    detail["Sintaxe e morfossintaxe"] = round(sm_score,2)
    base += sm_score
    
    tokens = tokenize(text)
    ttr = type_token_ratio(tokens)
    rep_pen = 0
    if ttr < 0.36: rep_pen += 2
    fillers = ["coisa","negócio","legal","tipo","muito","bem","aí"]
    rep_pen += sum(1 for f in fillers if f in tokens) * 0.5
    sem_score = max(0, 10 - rep_pen)
    detail["Semântica (escolha vocabular)"] = round(sem_score,2)
    base += sem_score
    
    thesis_hits = sum(1 for m in THESIS_MARKERS if re.search(r"\b"+re.escape(m)+r"\b", lowered))
    arg_markers = sum(1 for c in CONNECTIVES if re.search(r"\b"+re.escape(c)+r"\b", lowered))
    dt_score = min(10, 5 + min(thesis_hits,3)*1.5 + min(arg_markers,6)*0.5)
    detail["Domínio da tipologia (argumentação)"] = round(dt_score,2)
    base += dt_score
    
    return base, detail

def score_structure_content(text: str, theme_keywords: List[str]):
    detail = {}
    base = 0.0
    
    has_tit, title, body = has_title(text)
    paras = [p for p in re.split(r'\n\s*\n', body if has_tit else text) if p.strip()]
    p_count = len(paras) if paras else 1
    lengths = [len(tokenize(p)) for p in paras] if paras else [len(tokenize(text))]
    if p_count == 1 and len(text) > 0:
        org_score = 5
    else:
        balance = (max(lengths) - min(lengths)) if lengths else 0
        org_score = 10
        if not has_tit: org_score -= 2
        if p_count < 2: org_score -= 3
        if p_count > 6: org_score -= 1.5
        if balance > 120: org_score -= 1.5
    org_score = max(0, org_score)
    detail["Organização do texto (título, parágrafos)"] = round(org_score,2)
    base += org_score
    
    lowered = text.lower()
    kw_hits = sum(1 for k in theme_keywords if re.search(r"\b"+re.escape(k.lower())+r"\b", lowered))
    coverage = kw_hits / max(1, len(theme_keywords))
    has_pdv = bool(re.search(r"\b(defendo|sustento|ponto de vista|tese|na minha opinião|entendo que)\b", lowered))
    dev_score = 5 + coverage*5 + (2 if has_pdv else 0)
    dev_score = min(12, dev_score)
    detail["Desenvolvimento do tema e ponto de vista"] = round(dev_score,2)
    base += dev_score
    
    example_hits = sum(1 for m in EXAMPLE_MARKERS if re.search(r"\b"+re.escape(m)+r"\b", lowered))
    numbers = len(re.findall(r"\b\d{2,4}\b", text))
    qc = 4 + min(example_hits,5)*1.0 + min(numbers,3)*0.8
    qc = min(10, qc)
    detail["Qualidade de conteúdo (repertório, exemplos)"] = round(qc,2)
    base += qc
    
    conn_hits = sum(1 for c in CONNECTIVES if re.search(r"\b"+re.escape(c)+r"\b", lowered))
    tokens = [t for t in tokenize(text) if t not in {"de","da","do","a","o","e","que","em","um","uma","para","as","os"}]
    from collections import Counter
    counts = Counter(tokens)
    top_rep = max(counts.values()) if counts else 0
    rep_pen = 0
    if top_rep > max(3, len(tokens)*0.05):
        rep_pen += 1.5
    cohesion = max(0, min(8, 3 + min(conn_hits,8)*0.6 - rep_pen))
    detail["Coesão textual"] = round(cohesion,2)
    base += cohesion
    
    first_person = len(re.findall(r"\b(eu|acredito|penso|defendo|entendo|proponho|creio|considero|na minha opinião|ao meu ver)\b", lowered))
    rhetorical = "?" in text
    ia = 6 + min(first_person,3)*1.2 + (0.8 if rhetorical else 0)
    ia = min(10, ia)
    detail["Investimento autoral"] = round(ia,2)
    base += ia
    
    return base, detail

def grade_ufrgs(text: str, theme_keywords: List[str]) -> Dict:
    text = text.strip()
    exp_score, exp_detail = score_expression(text)
    esc_score, esc_detail = score_structure_content(text, theme_keywords)
    total_100 = exp_score + esc_score
    total_25 = round((total_100/100)*25, 2)
    return {
        "expressao_total_50": round(exp_score,2),
        "estrutura_conteudo_total_50": round(esc_score,2),
        "total_100": round(total_100,2),
        "total_escala_25": total_25,
        "detalhes_expressao": exp_detail,
        "detalhes_estrutura_conteudo": esc_detail
    }

if __name__ == "__main__":
    import json, sys
    if sys.stdin.isatty():
        print("Passe o texto via STDIN e palavras-chave separadas por vírgula como 1º argumento.")
        sys.exit(0)
    essay = sys.stdin.read()
    kws = sys.argv[1].split(",") if len(sys.argv)>1 else []
    result = grade_ufrgs(essay, kws)
    print(json.dumps(result, ensure_ascii=False, indent=2))
