import string
import random
import unicodedata
from collections import Counter

# =====================================================
# 0. CONFIGURAÇÃO GERAL
# =====================================================

ALPHABET = string.ascii_uppercase

# =====================================================
# 1. NORMALIZAÇÃO DO TEXTO (INGLÊS)
# =====================================================

def remove_accents(text: str) -> str:
    """
    Remove acentos/diacríticos (mais útil pra PT, mas deixamos genérico).
    """
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def normalize_ciphertext(text: str) -> str:
    """
    Converte para maiúsculas, remove acentos e mantém apenas A-Z + espaço.
    """
    text = text.upper()
    text = remove_accents(text)
    allowed = set(ALPHABET + " ")
    return "".join(c for c in text if c in allowed)

# =====================================================
# 2. FREQUÊNCIAS DE LETRAS EM INGLÊS
# =====================================================

# Ordem aproximada da mais frequente para a menos frequente em inglês
ENGLISH_FREQ_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

def letter_frequencies(text: str) -> Counter:
    letters = [c for c in text if c in ALPHABET]
    return Counter(letters)

def initial_key_guess(ciphertext: str) -> dict:
    """
    Gera um chute inicial de chave para substituição monoalfabética,
    baseado em frequências de letras do texto e do inglês.
    Retorna mapping: cipher_letter -> plain_letter.
    """
    freq = letter_frequencies(ciphertext)
    # Letras do texto cifrado, da mais frequente para a menos
    cipher_letters_sorted = [item[0] for item in freq.most_common()]

    # Garante que todas as letras do alfabeto apareçam
    for letter in ALPHABET:
        if letter not in cipher_letters_sorted:
            cipher_letters_sorted.append(letter)

    mapping = {}
    used_plain = set()

    for i, cipher_letter in enumerate(cipher_letters_sorted):
        if i < len(ENGLISH_FREQ_ORDER):
            plain_letter = ENGLISH_FREQ_ORDER[i]
        else:
            # Preenche com qualquer letra ainda não usada
            plain_letter = next(l for l in ALPHABET if l not in used_plain)
        mapping[cipher_letter] = plain_letter
        used_plain.add(plain_letter)

    return mapping

# =====================================================
# 3. APLICAR UMA CHAVE DE SUBSTITUIÇÃO
# =====================================================

def apply_mapping(text: str, mapping: dict) -> str:
    """
    Aplica um dicionário cipher_letter -> plain_letter ao texto.
    """
    result = []
    for c in text:
        if c in ALPHABET:
            result.append(mapping.get(c, c))
        else:
            result.append(c)
    return "".join(result)

# =====================================================
# 4. FUNÇÕES DE SCORE (INGLÊS: PALAVRAS, BIGRAMAS, VOGAIS)
# =====================================================

COMMON_WORDS_EN = [
    " THE ", " AND ", " TO ", " OF ", " IN ", " THAT ", " IT ",
    " IS ", " WAS ", " FOR ", " ON ", " WITH ", " AS ", " YOU ",
    " I ", " HE ", " SHE ", " THEY ", " THIS ", " BUT ",
    " WE ", " OUR ", " YOUR ", " PLEASE ", " FIND ", " ATTACHED ",
    " DOCUMENT ", " DOCUMENTS ", " REQUIRED ", " REVIEW ",
    " APPRECIATE ", " COOPERATION ", " REMAIN ", " DISPOSAL ",

    # palavras típicas dos seus exemplos de e-mail corporativo:
    " KINDLY ", " CONFIRM ", " PARTICIPATION ", " UPCOMING ",
    " TRAINING ", " SESSION ", " PRESENCE ", " ESSENTIAL ",
    " COMPLIANCE ", " PURPOSES ",
    " POLICY ", " GUIDELINES ", " EFFECT ", " MARCH ",
    " ADDITIONAL ", " INSTRUCTIONS ", " IMPLEMENTATION "
]

# Bigramas comuns em inglês (lista simplificada, com pesos arbitrários)
COMMON_BIGRAMS_EN = {
    "TH": 3.0, "HE": 2.8, "IN": 2.5, "ER": 2.3, "AN": 2.2, "RE": 2.1,
    "ON": 2.0, "AT": 1.9, "EN": 1.8, "ND": 1.7, "TI": 1.6, "ES": 1.6,
    "OR": 1.5, "TE": 1.5, "OF": 1.5, "ED": 1.4, "IS": 1.4, "IT": 1.4,
    "AL": 1.3, "AR": 1.3, "ST": 1.3, "TO": 1.3, "NT": 1.2, "HA": 1.2,
    "SE": 1.1
}

def score_common_words(text_plain: str) -> float:
    """
    Soma quantas vezes aparecem palavras comuns do inglês.
    """
    text_padded = f" {text_plain} "
    score = 0.0
    for w in COMMON_WORDS_EN:
        score += text_padded.count(w)
    return score

def score_bigrams(text_plain: str) -> float:
    """
    Soma pesos para bigramas comuns (pares de letras) em inglês.
    """
    score = 0.0
    filtered = "".join(c for c in text_plain if c in ALPHABET)
    for i in range(len(filtered) - 1):
        bg = filtered[i:i+2]
        score += COMMON_BIGRAMS_EN.get(bg, 0.0)
    return score

def score_vowel_ratio(text_plain: str) -> float:
    """
    Penaliza desvios grandes na proporção de vogais (AEIOU).
    Em inglês, algo em torno de ~0.4 costuma ser razoável.
    """
    vowels = set("AEIOU")
    num_vowels = sum(1 for c in text_plain if c in vowels)
    num_letters = sum(1 for c in text_plain if c in ALPHABET)
    if num_letters == 0:
        return 0.0
    ratio = num_vowels / num_letters
    target = 0.40
    penalty = abs(ratio - target)
    return -penalty  # quanto mais perto de 0.40, maior o score

def score_text(text_plain: str) -> float:
    """
    Combina vários critérios num score único.
    Aqui damos peso bem maior para palavras inteiras.
    """
    s_words = score_common_words(text_plain)
    s_bigrams = score_bigrams(text_plain)
    s_vowels = score_vowel_ratio(text_plain)

    # Pesos ajustados para priorizar palavras completas
    return 10.0 * s_words + 1.0 * s_bigrams + 2.0 * s_vowels

# =====================================================
# 5. (OPCIONAL) CÉSAR / ROT13 - fiz por engano
# =====================================================

# def decrypt_caesar(text: str, shift: int) -> str:
#     """
#     Decripta um texto cifrado com cifra de César (deslocamento 'shift').
#     NÃO ESTÁ SENDO USADO NESTA VERSÃO (APENAS MONOALFABÉTICA).
#     """
#     result = []
#     for c in text:
#         if c in ALPHABET:
#             idx = ALPHABET.index(c)
#             new_idx = (idx - shift) % 26  # decriptação anda pra trás
#             result.append(ALPHABET[new_idx])
#         else:
#             result.append(c)
#     return "".join(result)

# def break_caesar_english(ciphertext: str):
#     """
#     Testa todos os 26 deslocamentos possíveis e escolhe o melhor
#     com base em score_text. NÃO UTILIZADO NESTA VERSÃO.
#     """
#     cipher_norm = normalize_ciphertext(ciphertext)
#
#     best_shift = 0
#     best_plain = ""
#     best_score = float("-inf")
#
#     for shift in range(26):
#         cand_plain = decrypt_caesar(cipher_norm, shift)
#         s = score_text(cand_plain)
#         if s > best_score:
#             best_score = s
#             best_plain = cand_plain
#             best_shift = shift
#
#     return best_plain, best_shift, best_score

# =====================================================
# 6. HILL-CLIMBING + "SIMULATED ANNEALING LIGHT"
#    PARA SUBSTITUIÇÃO GERAL
# =====================================================

def generate_neighbor(mapping: dict) -> dict:
    """
    Gera uma chave vizinha trocando duas letras no lado plaintext (valores).
    """
    new_mapping = mapping.copy()

    # escolhe duas letras de plaintext quaisquer para trocar
    a, b = random.sample(ALPHABET, 2)

    # inverte mapping: plain_letter -> cipher_letter
    inv = {v: k for k, v in new_mapping.items()}
    cipher_for_a = inv[a]
    cipher_for_b = inv[b]

    # faz a troca
    new_mapping[cipher_for_a], new_mapping[cipher_for_b] = (
        new_mapping[cipher_for_b],
        new_mapping[cipher_for_a],
    )

    return new_mapping

def random_mapping() -> dict:
    """
    Gera uma chave totalmente aleatória (permutação do alfabeto).
    mapping: cipher_letter -> plain_letter
    """
    plain_letters = list(ALPHABET)
    random.shuffle(plain_letters)
    return {cipher: plain for cipher, plain in zip(ALPHABET, plain_letters)}

def hill_climb_single_run(ciphertext: str,
                          iterations: int = 10000,
                          use_freq_init: bool = True):
    """
    Executa uma corrida de hill-climbing com "simulated annealing light".
    Se use_freq_init=True, começa pela chave baseada em frequência.
    Se False, começa com chave totalmente aleatória.
    Retorna (melhor_texto_claro, melhor_mapping, melhor_score).
    """
    if use_freq_init:
        current_mapping = initial_key_guess(ciphertext)
    else:
        current_mapping = random_mapping()

    current_plain = apply_mapping(ciphertext, current_mapping)
    current_score = score_text(current_plain)

    best_mapping = current_mapping
    best_plain = current_plain
    best_score = current_score

    for i in range(iterations):
        neighbor_mapping = generate_neighbor(current_mapping)
        neighbor_plain = apply_mapping(ciphertext, neighbor_mapping)
        neighbor_score = score_text(neighbor_plain)

        delta = neighbor_score - current_score

        if delta > 0:
            # Melhorou, aceita sempre
            accept = True
        else:
            # Simulated annealing light: às vezes aceita piora
            T = max(0.1, (iterations - i) / iterations)  # decresce ao longo do tempo
            base_prob = 0.05  # probabilidade base de aceitar piora
            prob = base_prob * T
            accept = random.random() < prob

        if accept:
            current_mapping = neighbor_mapping
            current_plain = neighbor_plain
            current_score = neighbor_score

            if current_score > best_score:
                best_mapping = current_mapping
                best_plain = current_plain
                best_score = current_score

    return best_plain, best_mapping, best_score

# =====================================================
# 7. GANCHO PARA LLM (HUGGINGFACE
# =====================================================

def evaluate_with_llm(candidates_plain):
    """
    GANCHO para integrar com um modelo do Hugging Face.

    Exemplo (para implementar depois):

        from transformers import pipeline
        clf = pipeline("text-classification", model="SEU_MODELO_AQUI")
        scores = []
        for text in candidates_plain:
            out = clf(text[:512])
            # converter 'out' em algum número de qualidade
            scores.append(algum_valor)
        return scores

    Por enquanto, devolve 0 para todos (placeholder).
    """
    return [0.0 for _ in candidates_plain]

def choose_best_with_llm(candidates):
    """
    candidates: lista de tuplas (plain_text, mapping, heuristic_score).
    Combina score heurístico com score do LLM.
    """
    plain_list = [c[0] for c in candidates]
    llm_scores = evaluate_with_llm(plain_list)

    best_idx = 0
    best_total = float("-inf")

    for i, (plain, mapping, h_score) in enumerate(candidates):
        total = h_score + llm_scores[i]
        if total > best_total:
            best_total = total
            best_idx = i

    return candidates[best_idx]

# =====================================================
# 8. SUBSTITUIÇÃO GERAL
# =====================================================

def break_general_substitution_english(ciphertext: str,
                                       restarts: int = 50,
                                       iterations: int = 10000):
    """
    Quebra uma cifra de substituição genérica (chave monoalfabética),
    usando hill-climbing "turbinado" com múltiplos recomeços e (opcionalmente) LLM.
    Metade dos restarts começa com chute por frequência,
    metade com chave totalmente aleatória.
    """
    cipher_norm = normalize_ciphertext(ciphertext)

    candidates = []
    for seed in range(restarts):
        random.seed(seed)
        # metade dos restarts com freq, metade aleatória
        use_freq_init = (seed % 2 == 0)
        plain, mapping, score_h = hill_climb_single_run(
            cipher_norm,
            iterations=iterations,
            use_freq_init=use_freq_init
        )
        candidates.append((plain, mapping, score_h))

    best_plain, best_mapping, best_score = choose_best_with_llm(candidates)
    return best_plain, best_mapping, best_score

# =====================================================
# 9. INTERFACE SIMPLES DE LINHA DE COMANDO
# =====================================================

if __name__ == "__main__":
    print("=== BREAKING MONOALPHABETIC SUBSTITUTION CIPHER (ENGLISH) ===")
    print("Paste the ciphertext on a single line and press Enter:")
    cipher = input("> ")

    gen_plain, gen_mapping, gen_score = break_general_substitution_english(cipher)

    print("\n=== ASSUMING GENERAL SUBSTITUTION CIPHER ===")
    print(f"Score: {gen_score}")
    print("\nPlaintext candidate:\n")
    print(gen_plain)

    print("\nSubstitution table (CIPHER -> PLAIN):")
    for c in sorted(gen_mapping.keys()):
        print(f"{c} -> {gen_mapping[c]}")
