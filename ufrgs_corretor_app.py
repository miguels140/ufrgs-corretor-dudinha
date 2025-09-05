# Arquivo: ufrgs_corretor.py
from textblob import TextBlob
from spellchecker import SpellChecker

# =========================
# Funções de correção UFRGS
# =========================

def grade_ufrgs(texto, tema_keywords):
    detalhes_expressao = {}
    blob = TextBlob(texto)
    n_frases = len(blob.sentences)
    n_palavras = len(blob.words)
    detalhes_expressao['n_frases'] = n_frases
    detalhes_expressao['n_palavras'] = n_palavras
    media_palavras = n_palavras / n_frases if n_frases > 0 else 1
    if 12 <= media_palavras <= 20:
        expressao_total_50 = 50
    elif 8 <= media_palavras < 12:
        expressao_total_50 = 40
    else:
        expressao_total_50 = 30
    detalhes_estrutura_conteudo = {}
    contagem_keywords = sum(texto.lower().count(k.lower()) for k in tema_keywords)
    detalhes_estrutura_conteudo['palavras_chave_achadas'] = contagem_keywords
    if contagem_keywords >= 5:
        estrutura_conteudo_total_50 = 50
    elif contagem_keywords >= 3:
        estrutura_conteudo_total_50 = 40
    else:
        estrutura_conteudo_total_50 = 30
    total_100 = expressao_total_50 + estrutura_conteudo_total_50
    total_escala_25 = round(total_100 * 25 / 100, 2)
    return {
        'expressao_total_50': expressao_total_50,
        'estrutura_conteudo_total_50': estrutura_conteudo_total_50,
        'total_100': total_100,
        'total_escala_25': total_escala_25,
        'detalhes_expressao': detalhes_expressao,
        'detalhes_estrutura_conteudo': detalhes_estrutura_conteudo
    }

# =========================
# Mini IA de detecção de erros
# =========================

def detectar_erros(texto):
    erros = []
    spell = SpellChecker(language='pt')
    palavras = texto.split()
    for palavra in palavras:
        p = palavra.strip('.,;:!?()[]{}"')
        if p and p.lower() not in spell:
            erros.append(f"Possível erro de ortografia: '{palavra}'")
    if "os jovem" in texto or "a jovem" in texto or "os menino" in texto:
        erros.append("Possível erro de concordância: revise plural/singular")
    frases = texto.split(".")
    for f in frases:
        if len(f.split()) > 30:
            erros.append(f"Frase muito longa (mais de 30 palavras): '{f.strip()[:50]}...'")
    return erros
