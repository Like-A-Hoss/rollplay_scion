import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utilities.dice import ScionDice

class TestScionDice(unittest.TestCase):
    def setUp(self):
        self.dice = ScionDice(dice_pool=5, enhancement=2, hero_type="hero", scale=1, difficulty=3, divinity_dice=2, tn=8, again=10)

    def test_roll(self):
        results = self.dice.roll()
        self.assertEqual(len(results), 5)

    def test_roll_divinity(self):
        results = self.dice.roll_divinity()
        self.assertEqual(len(results), 2)

    def test_count_successes(self):
        results = [7, 8, 9]
        divine_results = []
        exploded_results = []
        unmodified_dice = ScionDice(
            dice_pool=5,
            enhancement=0,
            hero_type="Hero",
            scale=0,
            difficulty=3,
            divinity_dice=0,
            tn=8,
            again=10,
        )

        successes = unmodified_dice.count_successes(
            results, divine_results, exploded_results
        )

        self.assertEqual(successes, 2)

    def test_count_successes_includes_divine_and_exploded_dice(self):
        results = [7, 8]
        divine_results = [8]
        exploded_results = [10]

        successes = self.dice.count_successes(results, divine_results, exploded_results)

        self.assertEqual(successes, 7)

    def test_count_successes_returns_zero_without_a_success(self):
        results = [1, 7]

        successes = self.dice.count_successes(results)

        self.assertEqual(successes, 0)

    def test_check_botch(self):
        results = [1, 2, 3]
        exploded_results = [1]
        botch = self.dice.check_botch(results, exploded_results, successes=0)
        self.assertTrue(botch)

    def test_check_explode(self):
        results = [10, 9]
        exploded_results = self.dice.check_explode(results)
        self.assertTrue(all(die >= 1 for die in exploded_results))

    def test_check_catastrophic_success(self):
        divine_results = [7, 8]
        cs = self.dice.check_catastrophic_success(divine_results)
        self.assertTrue(cs)

    def test_check_mortal_fail(self):
        mortal_dice = [1, 2, 3]
        mortal_fail = self.dice.check_mortal_fail(mortal_dice)
        self.assertTrue(mortal_fail)

if __name__ == "__main__":
    unittest.main()

