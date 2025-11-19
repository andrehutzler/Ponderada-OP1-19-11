# ==========================================================
# TEST MODULE FOR PERMUTATION CIPHER + BREAKERS (GA, etc.)
# FILE: test_breaker.py
# ==========================================================

class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def assert_equal(self, a, b, msg):
        if a == b:
            print("[OK] ", msg)
            self.passed += 1
        else:
            print("[FAIL] ", msg)
            print("   Expected:", b)
            print("   Got     :", a)
            self.failed += 1

    def assert_true(self, cond, msg):
        if cond:
            print("[OK] ", msg)
            self.passed += 1
        else:
            print("[FAIL] ", msg)
            self.failed += 1

    def summary(self):
        print("\n========== TEST SUMMARY ==========")
        print("PASSED:", self.passed)
        print("FAILED:", self.failed)
        print("==================================")


# ==========================================================
# IMPORT OR DEFINE YOUR CLASSES HERE
# (PermutationCipher, EnglishScorer, Breaker)
# ==========================================================

import permutacao_livre

PermutationCipher = permutacao_livre.PermutationCipher
EnglishScorer = permutacao_livre.EnglishScorer
Breaker = permutacao_livre.GeneticBreaker

# ==========================================================
# TESTS
# ==========================================================

class BreakerTests:

    # ------------------------- BASIC GA TESTS -------------------------
    def test_ga_finds_readable_text(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimplemessageforbreaker"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=4)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_true(score > 0, "GA breaker must produce readable plaintext")

    def test_ga_output_length_correct(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimple"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=4)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_equal(len(plaintext), len(msg.replace(" ", "")),
                        "GA plaintext must match original size")

    # ------------------------- ADVANCED TESTS -------------------------

    def test_ga_finds_correct_key_or_equivalent(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimplemessageforbreakerthisisatestsimple"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=4, generations=300)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_true(found_key is not None, "GA must return some key")
        ts.assert_true(len(found_key) == 4, "GA must return a key of correct size")

    def test_ga_with_random_permutation(self, ts):
        import random
        size = 5
        key = list(range(1, size+1))
        random.shuffle(key)

        cipher = PermutationCipher(key)
        msg = "thisisaverylongmessagethatshouldbecracked"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=size)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_true(score > 0, "GA must break cipher even with random permutation")

    def test_ga_multi_block(self, ts):
        key = [2,3,1]
        cipher = PermutationCipher(key)

        msg = "thisisalongermessageformultiblocktesting"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=3)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_true(score > 0, "GA must handle multi-block messages")

    def test_ga_repeated_characters(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "aaaaaaaabbbbbbbbccccccccddddeeee"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=4)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_true(len(plaintext) == len(msg), "GA must handle repeated characters")

    def test_ga_consistency(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimplemessageconsistencycheck"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        
        scores = []
        for _ in range(3):
            breaker = Breaker(scorer, block_size=4, generations=200)
            _, _, score = breaker.break_cipher(encrypted)
            scores.append(score)

        ts.assert_true(abs(scores[0] - scores[2]) < 15,
                       "GA must be reasonably consistent across runs")

    def test_ga_long_text(self, ts):
        """
        Test the GA breaker on a long text (hundreds of chars).
        Ensures the breaker can scale and still produce meaningful scores.
        """
        key = [3, 1, 4, 2]
        cipher = PermutationCipher(key)

        # A long English text (you can replace with any long input)
        msg = (
            "thisisaverylongenglishtextdesignedtotestthegeneticalgorithmbreaker "
            "andensurethatitscaleswellwithlargerinputswithoutlosingstability "
            "orproducingnonsensicaldecryptionsunderthepermutationmodel"
        ).replace(" ", "")

        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer, block_size=4, generations=350)

        found_key, plaintext, score = breaker.break_cipher(encrypted)

        ts.assert_true(score > 0, "GA must break long text with meaningful score")
        ts.assert_equal(len(plaintext), len(msg), "Long text length must be preserved")


# ==========================================================
# RUNNER
# ==========================================================

def run_all_tests():
    ts = TestSuite()
    bt = BreakerTests()

    bt.test_ga_finds_readable_text(ts)
    bt.test_ga_output_length_correct(ts)
    bt.test_ga_finds_correct_key_or_equivalent(ts)
    bt.test_ga_with_random_permutation(ts)
    bt.test_ga_multi_block(ts)
    bt.test_ga_repeated_characters(ts)
    bt.test_ga_consistency(ts)
    bt.test_ga_long_text(ts)

    ts.summary()


run_all_tests()
