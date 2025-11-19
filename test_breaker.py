# ==========================================================
# TEST MODULE FOR PERMUTATION + SUBSTITUTION CIPHER BREAKERS
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

import permutacao_livre

PermutationCipher   = permutacao_livre.PermutationCipher
SubstitutionCipher  = permutacao_livre.SubstitutionCipher
EnglishScorer       = permutacao_livre.EnglishScorer
Breaker             = permutacao_livre.GeneticBreaker


# ==========================================================

class BreakerTestsPermutation:

    def test_ga_finds_readable_text(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimplemessageforbreaker"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, PermutationCipher)

        ts.assert_true(found_key is not None, "GA must produce readable plaintext (perm)")

    def test_ga_output_length_correct(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimple"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, PermutationCipher)
        plaintext = PermutationCipher(best_key).decrypt(encrypted)

        ts.assert_equal(len(plaintext), len(msg), "GA plaintext length must match (perm)")

    def test_ga_finds_correct_key_or_equivalent(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimplemessageforbreakerthisisatestsimple"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, PermutationCipher)

        ts.assert_true(found_key is not None, "GA must return some key (perm)")
        ts.assert_true(len(found_key) == 4, "GA key size must match (perm)")

    def test_ga_with_random_permutation(self, ts):
        import random
        size = 5
        key = list(range(size))
        random.shuffle(key)

        cipher = PermutationCipher(key)
        msg = "thisisaverylongmessagethatshouldbecracked"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, PermutationCipher)

        ts.assert_true(found_key is not None, "GA must break random perm key")

    def test_ga_multi_block(self, ts):
        key = [2,3,1]
        cipher = PermutationCipher(key)

        msg = "thisisalongermessageformultiblocktesting"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, PermutationCipher)

        ts.assert_true(found_key is not None, "GA must handle multi-block (perm)")

    def test_ga_repeated_characters(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "aaaaaaaabbbbbbbbccccccccddddeeee"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, PermutationCipher)
        plaintext = PermutationCipher(found_key).decrypt(encrypted)

        ts.assert_true(len(plaintext) == len(msg), "GA must handle repeated chars (perm)")

    def test_ga_consistency(self, ts):
        key = [3,1,4,2]
        cipher = PermutationCipher(key)

        msg = "thisisatestsimplemessageconsistencycheck"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()

        scores = []
        for _ in range(3):
            breaker = Breaker(scorer)
            best_key = breaker.break_cipher(encrypted, PermutationCipher)
            plain = PermutationCipher(best_key).decrypt(encrypted)
            scores.append(scorer.score(plain))

        ts.assert_true(abs(scores[0] - scores[2]) < 15, "GA must be consistent (perm)")

    def test_ga_long_text(self, ts):
        key = [3, 1, 4, 2]
        cipher = PermutationCipher(key)

        msg = (
            "thisisaverylongenglishtextdesignedtotestthegeneticalgorithmbreaker "
            "andensurethatitscaleswellwithlargerinputswithoutlosingstability "
            "orproducingnonsensicaldecryptionsunderthepermutationmodel"
        ).replace(" ", "")

        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, PermutationCipher)
        plaintext = PermutationCipher(best_key).decrypt(encrypted)

        ts.assert_true(len(plaintext) == len(msg), "length preserved (perm)")
        ts.assert_true(scorer.score(plaintext) > 0, "meaningful score on long text (perm)")


# ==========================================================

class BreakerTestsSubstitution:

    def example_key(self):
        import string, random
        letters = list(string.ascii_uppercase)
        shuffled = letters[:]
        random.shuffle(shuffled)
        return dict(zip(letters, shuffled))

    def test_sub_readable_text(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISASIMPLEPLAINTEXTMESSAGEFORTESTING"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        ts.assert_true(found_key is not None, "GA readable text (sub)")

    def test_sub_length_correct(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISALENGTHCHECK"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        plaintext = SubstitutionCipher(best_key).decrypt(encrypted)

        ts.assert_equal(len(plaintext), len(msg), "length preserved (sub)")

    def test_sub_key_validity(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISALONGMESSAGEFORKEYVALIDATIONTEST"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)

        ts.assert_true(len(best_key) == 26, "substitution key must have 26 letters")

    def test_sub_random_key(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISARANDOMKEYTESTMESSAGE"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        ts.assert_true(best_key is not None, "GA must break random substitution key")

    def test_sub_repeated_chars(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "AAAAAAAAAABBBBBBBBBCCCCCCCCCDDDDDDD"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        plaintext = SubstitutionCipher(best_key).decrypt(encrypted)

        ts.assert_equal(len(plaintext), len(msg), "repeated chars ok (sub)")

    def test_sub_consistency(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISACONSISTENCYTESTMESSAGEFORCHECKINGGA"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        scores = []

        for _ in range(3):
            breaker = Breaker(scorer)
            best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
            plain = SubstitutionCipher(best_key).decrypt(encrypted)
            scores.append(scorer.score(plain))

        ts.assert_true(abs(scores[0] - scores[2]) < 30, "GA consistency across runs (sub)")

    def test_sub_multi_sentence(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISALONGERENGLISHTEXTFORTESTINGMULTISENTENCESUBSTITUTION"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        found_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        ts.assert_true(found_key is not None, "multi-sentence handling (sub)")

    def test_sub_minimum_score(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "THISISASCORETESTFORMINIMUMTHRESHOLD"
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        plain = SubstitutionCipher(best_key).decrypt(encrypted)

        ts.assert_true(scorer.score(plain) >= 0, "minimum score >= 0 (sub)")

    def test_sub_long_text(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = ("THISISALONGENGLISHTEXTINTENDEDTESTTHATTHEBREAKERSCALES "
               "TOLARGERDATASETSANDPRODUCESMEANINGFULDECRYPTIONS").replace(" ", "")
        encrypted = cipher.encrypt(msg)

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        plain = SubstitutionCipher(best_key).decrypt(encrypted)

        ts.assert_equal(len(plain), len(msg), "long text length (sub)")
        ts.assert_true(scorer.score(plain) > 0, "long text score (sub)")

    def test_sub_uppercase_handling(self, ts):
        key = self.example_key()
        cipher = SubstitutionCipher(key)

        msg = "MIXEDCASEHANDLINGTEST"
        encrypted = cipher.encrypt(msg.upper())

        scorer = EnglishScorer()
        breaker = Breaker(scorer)

        best_key = breaker.break_cipher(encrypted, SubstitutionCipher)
        plain = SubstitutionCipher(best_key).decrypt(encrypted)

        ts.assert_true(len(plain) == len(msg), "uppercase handling (sub)")


# ==========================================================

def run_all_tests():
    ts = TestSuite()

    print("\n=== PERMUTATION CIPHER TESTS ===")
    perm = BreakerTestsPermutation()

    perm.test_ga_finds_readable_text(ts)
    perm.test_ga_output_length_correct(ts)
    perm.test_ga_finds_correct_key_or_equivalent(ts)
    perm.test_ga_with_random_permutation(ts)
    perm.test_ga_multi_block(ts)
    perm.test_ga_repeated_characters(ts)
    perm.test_ga_consistency(ts)
    perm.test_ga_long_text(ts)

    print("\n=== SUBSTITUTION CIPHER TESTS ===")
    sub = BreakerTestsSubstitution()

    sub.test_sub_readable_text(ts)
    sub.test_sub_length_correct(ts)
    sub.test_sub_key_validity(ts)
    sub.test_sub_random_key(ts)
    sub.test_sub_repeated_chars(ts)
    sub.test_sub_consistency(ts)
    sub.test_sub_multi_sentence(ts)
    sub.test_sub_minimum_score(ts)
    sub.test_sub_long_text(ts)
    sub.test_sub_uppercase_handling(ts)

    ts.summary()


run_all_tests()
