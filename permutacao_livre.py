class PermutationCipher:
    def __init__(self, key):
        self.key = key                  # e.g. [3,1,4,2]
        self.inverse_key = self._invert_key(key)

    def _invert_key(self, key):
        inv = [0] * len(key)
        for i, k in enumerate(key):
            inv[k-1] = i+1
        return inv

    def encrypt_block(self, block):
        if len(block) != len(self.key):
            return block
        return ''.join(block[self.key[i]-1] for i in range(len(block)))

    def decrypt_block(self, block):
        if len(block) != len(self.inverse_key):
            return block
        return ''.join(block[self.inverse_key[i]-1] for i in range(len(block)))

    def encrypt(self, text):
        size = len(self.key)
        return ''.join(self.encrypt_block(text[i:i+size]) for i in range(0, len(text), size))

    def decrypt(self, text):
        size = len(self.key)
        return ''.join(self.decrypt_block(text[i:i+size]) for i in range(0, len(text), size))

import nltk
nltk.download("words")

from nltk.corpus import words


class EnglishScorer:
    def __init__(self):
        # Load the full English dictionary from NLTK
        self.english_words = set(w.lower() for w in words.words())

        # Most common English bigrams
        self.english_bigrams = [
            "th", "he", "in", "er", "an", "re", "on", "at", "en", "nd",
            "ti", "es", "or", "te", "of", "ed", "is", "it", "al"
        ]

    def score(self, text):
        score = 0
        text = text.lower()

        # Reward common English words
        for w in text.split():
            if w in self.english_words:
                score += 5

        # Reward common bigrams
        for i in range(len(text) - 1):
            if text[i:i+2] in self.english_bigrams:
                score += 1

        return score

import random

class GeneticBreaker:
    def __init__(self, scorer, block_size, population_size=50, mutation_rate=0.1, generations=200):
        self.scorer = scorer
        self.block_size = block_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.generations = generations

    def random_key(self):
        arr = list(range(1, self.block_size + 1))
        random.shuffle(arr)
        return arr

    def fitness(self, key, ciphertext):
        cipher = PermutationCipher(key)
        decrypted = cipher.decrypt(ciphertext)
        return self.scorer.score(decrypted), decrypted

    def tournament_selection(self, population, scores, k=3):
        best = None
        best_score = -1e9
        for _ in range(k):
            idx = random.randint(0, len(population)-1)
            if scores[idx] > best_score:
                best_score = scores[idx]
                best = population[idx]
        return best

    def crossover(self, parent1, parent2):
        size = len(parent1)
        a, b = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[a:b] = parent1[a:b]

        fill = [g for g in parent2 if g not in child]
        
        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = fill[idx]
                idx += 1

        return child

    def mutate(self, key):
        if random.random() < self.mutation_rate:
            a, b = random.sample(range(len(key)), 2)
            key[a], key[b] = key[b], key[a]

    def break_cipher(self, ciphertext):

        population = [self.random_key() for _ in range(self.population_size)]

        best_key = None
        best_plain = None
        best_score = -1e9

        for gen in range(self.generations):
            scores = []
            plaintexts = []

            for key in population:
                score, plain = self.fitness(key, ciphertext)
                scores.append(score)
                plaintexts.append(plain)

                if score > best_score:
                    best_score = score
                    best_key = key[:]
                    best_plain = plain

            new_pop = []

            for _ in range(self.population_size):
                p1 = self.tournament_selection(population, scores)
                p2 = self.tournament_selection(population, scores)

                child = self.crossover(p1, p2)
                self.mutate(child)
                new_pop.append(child)

            population = new_pop

        return best_key, best_plain, best_score


