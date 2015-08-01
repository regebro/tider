import pickle
import unittest


# Helper function from the standard libraries test suites:
requires_IEEE_754 = unittest.skipUnless(
    float.__getformat__("double").startswith("IEEE"),
    "test requires IEEE 754 doubles")


# Common variables
pickle_choices = [(pickle, pickle, proto)
                  for proto in range(pickle.HIGHEST_PROTOCOL + 1)]
assert len(pickle_choices) == pickle.HIGHEST_PROTOCOL + 1

# An arbitrary collection of objects of non-datetime types, for testing
# mixed-type comparisons.
OTHERSTUFF = (10, 34.5, "abc", {}, [], ())


# Base class for testing a particular aspect of timedelta, time, date and
# datetime comparisons.

class HarmlessMixedComparison:
    # Test that __eq__ and __ne__ don't complain for mixed-type comparisons.

    # Subclasses must define 'theclass', and theclass(1, 1, 1) must be a
    # legit constructor.

    def test_harmless_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertFalse(me == ())
        self.assertTrue(me != ())
        self.assertFalse(() == me)
        self.assertTrue(() != me)

        self.assertIn(me, [1, 20, [], me])
        self.assertIn([], [me, 1, 20, []])

    def test_harmful_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertRaises(TypeError, lambda: me < ())
        self.assertRaises(TypeError, lambda: me <= ())
        self.assertRaises(TypeError, lambda: me > ())
        self.assertRaises(TypeError, lambda: me >= ())

        self.assertRaises(TypeError, lambda: () < me)
        self.assertRaises(TypeError, lambda: () <= me)
        self.assertRaises(TypeError, lambda: () > me)
        self.assertRaises(TypeError, lambda: () >= me)
