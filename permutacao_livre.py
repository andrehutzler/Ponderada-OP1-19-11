import random
import nltk

try:
    nltk.data.find("corpora/words")
except LookupError:
    nltk.download("words")

from nltk.corpus import words as nltk_words


class EnglishScorer:
    def __init__(self):
        self.english_words = set(w.lower() for w in nltk_words.words())
        self.english_bigrams = [
            "th","he","in","er","an","re","on","at","en","nd",
            "ti","es","or","te","of","ed","is","it","al"
        ]

    def score(self, text):
        score = 0
        text = text.lower()
        for w in text.split():
            if w in self.english_words:
                score += 5
        for i in range(len(text)-1):
            if text[i:i+2] in self.english_bigrams:
                score += 1
        return score


class PermutationCipher:
    def __init__(self, key):
        self.key = self._normalize_key(list(key))

    def _normalize_key(self, key):
        n = len(key)
        if any(k >= n or k < 0 for k in key):
            try:
                key1 = [int(k) for k in key]
            except Exception:
                return key
            if max(key1) == n:
                return [k-1 for k in key1]
            else:
                return key1
        return key

    def encrypt(self, plaintext):
        n = len(self.key)
        blocks = [plaintext[i:i+n] for i in range(0, len(plaintext), n)]
        encrypted = ""
        for block in blocks:
            if len(block) < n:
                block = block.ljust(n)
            encrypted += "".join(block[self.key[i]] for i in range(n))
        return encrypted

    def decrypt(self, ciphertext):
        n = len(self.key)
        inverse = [0] * n
        for i, k in enumerate(self.key):
            inverse[k] = i
        blocks = [ciphertext[i:i+n] for i in range(0, len(ciphertext), n)]
        decrypted = ""
        for block in blocks:
            if len(block) < n:
                block = block.ljust(n)
            decrypted += "".join(block[inverse[i]] for i in range(n))
        return decrypted.rstrip()


class SubstitutionCipher:
    def __init__(self, key):
        self.key = {k.upper(): v.upper() for k, v in key.items()}
        self.inverse_key = {v: k for k, v in self.key.items()}

    def encrypt(self, plaintext):
        result = []
        for c in plaintext.upper():
            result.append(self.key.get(c, c))
        return "".join(result)

    def decrypt(self, ciphertext):
        result = []
        for c in ciphertext.upper():
            result.append(self.inverse_key.get(c, c))
        return "".join(result)


class GeneticBreaker:
    def __init__(self, scorer, population_size=200, mutation_rate=0.1, generations=300):
        self.scorer = scorer
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.generations = generations

    def detect_permutation_block_size(self, ciphertext):
        best_size = 2
        best_repeats = -1
        for size in range(2, min(40, max(13, len(ciphertext)//2 + 1))):
            if size <= 0:
                continue
            blocks = [ciphertext[i:i+size] for i in range(0, len(ciphertext), size)]
            repeats = len(blocks) - len(set(blocks))
            if repeats > best_repeats:
                best_repeats = repeats
                best_size = size
        return best_size

    def generate_random_key(self, cipher_type, key_size=None):
        if cipher_type == "permutation":
            key = list(range(key_size))
            random.shuffle(key)
            return key
        elif cipher_type == "substitution":
            letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            shuffled = letters[:]
            random.shuffle(shuffled)
            return dict(zip(letters, shuffled))

    def mutate(self, key, cipher_type):
        if cipher_type == "permutation":
            a, b = random.sample(range(len(key)), 2)
            key[a], key[b] = key[b], key[a]
        elif cipher_type == "substitution":
            a, b = random.sample(list(key.keys()), 2)
            key[a], key[b] = key[b], key[a]
        return key

    def crossover(self, k1, k2, cipher_type):
        if cipher_type == "permutation":
            size = len(k1)
            a, b = sorted(random.sample(range(size), 2))
            child = [-1] * size
            child[a:b+1] = k1[a:b+1]
            fill = [x for x in k2 if x not in child]
            idx = 0
            for i in range(size):
                if child[i] == -1:
                    child[i] = fill[idx]
                    idx += 1
            return child
        elif cipher_type == "substitution":
            letters = list(k1.keys())
            size = len(letters)
            a, b = sorted(random.sample(range(size), 2))
            child = {}
            for i in range(a, b+1):
                child[letters[i]] = k1[letters[i]]
            used = set(child.values())
            for l in letters:
                if l not in child:
                    for cand in [k2[l]] + letters:
                        if cand not in used:
                            child[l] = cand
                            used.add(cand)
                            break
            return child

    def break_cipher(self, ciphertext, cipher_class):
        cipher_type = "substitution" if cipher_class == SubstitutionCipher else "permutation"
        if cipher_type == "permutation":
            key_size = self.detect_permutation_block_size(ciphertext)
        else:
            key_size = None
        population = [self.generate_random_key(cipher_type, key_size) for _ in range(self.population_size)]
        best_key = None
        best_score = float("-inf")
        elite_size = max(2, self.population_size // 10)
        for _ in range(self.generations):
            scored = []
            for key in population:
                cipher = cipher_class(key)
                decrypted = cipher.decrypt(ciphertext)
                score = self.scorer.score(decrypted)
                scored.append((score, key, decrypted))
            scored.sort(key=lambda x: x[0], reverse=True)
            if scored and scored[0][0] > best_score:
                best_score = scored[0][0]
                best_key = scored[0][1]
            elite = [k for _, k, _ in scored[:elite_size]]
            new_population = elite[:]
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(elite, 2)
                child = self.crossover(parent1, parent2, cipher_type)
                if random.random() < self.mutation_rate:
                    child = self.mutate(child, cipher_type)
                new_population.append(child)
            population = new_population
        return best_key
