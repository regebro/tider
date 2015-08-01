import unittest
import tests
import tider  # Must be imported for eval to work in the roundtrip test.

from operator import truediv, floordiv, mod, mul
from tider import Duration


NAN = float("nan")
INF = float("inf")


class TestDuration(tests.HarmlessMixedComparison, unittest.TestCase):

    theclass = Duration

    def test_constructor(self):
        eq = self.assertEqual

        # Check keyword args to constructor
        eq(Duration(), Duration(weeks=0, days=0, hours=0, minutes=0, seconds=0,
                                milliseconds=0, microseconds=0))
        eq(Duration(1), Duration(days=1))
        eq(Duration(0, 1), Duration(seconds=1))
        eq(Duration(0, 0, 1), Duration(microseconds=1))
        eq(Duration(weeks=1), Duration(days=7))
        eq(Duration(days=1), Duration(hours=24))
        eq(Duration(hours=1), Duration(minutes=60))
        eq(Duration(minutes=1), Duration(seconds=60))
        eq(Duration(seconds=1), Duration(milliseconds=1000))
        eq(Duration(milliseconds=1), Duration(microseconds=1000))

        # Check float args to constructor
        eq(Duration(weeks=1.0/7), Duration(days=1))
        eq(Duration(days=1.0/24), Duration(hours=1))
        eq(Duration(hours=1.0/60), Duration(minutes=1))
        eq(Duration(minutes=1.0/60), Duration(seconds=1))
        eq(Duration(seconds=0.001), Duration(milliseconds=1))
        eq(Duration(milliseconds=0.001), Duration(microseconds=1))

    def test_computations(self):
        eq = self.assertEqual

        a = Duration(7)  # One week
        b = Duration(0, 60)  # One minute
        c = Duration(0, 0, 1000)  # One millisecond
        eq(a+b+c, Duration(7, 60, 1000))
        eq(a-b, Duration(6, 24*3600 - 60))
        eq(b.__rsub__(a), Duration(6, 24*3600 - 60))
        eq(-a, Duration(-7))
        eq(+a, Duration(7))
        eq(-b, Duration(-1, 24*3600 - 60))
        eq(-c, Duration(-1, 24*3600 - 1, 999000))
        eq(abs(a), a)
        eq(abs(-a), a)
        eq(Duration(6, 24*3600), a)
        eq(Duration(0, 0, 60*1000000), b)
        eq(a*10, Duration(70))
        eq(a*10, 10*a)
        eq(a*10, 10*a)
        eq(b*10, Duration(0, 600))
        eq(10*b, Duration(0, 600))
        eq(b*10, Duration(0, 600))
        eq(c*10, Duration(0, 0, 10000))
        eq(10*c, Duration(0, 0, 10000))
        eq(c*10, Duration(0, 0, 10000))
        eq(a*-1, -a)
        eq(b*-2, -b-b)
        eq(c*-2, -c+-c)
        eq(b*(60*24), (b*60)*24)
        eq(b*(60*24), (60*b)*24)
        eq(c*1000, Duration(0, 1))
        eq(1000*c, Duration(0, 1))
        eq(a//7, Duration(1))
        eq(b//10, Duration(0, 6))
        eq(c//1000, Duration(0, 0, 1))
        eq(a//10, Duration(0, 7*24*360))
        eq(a//3600000, Duration(0, 0, 7*24*1000))
        eq(a/0.5, Duration(14))
        eq(b/0.5, Duration(0, 120))
        eq(a/7, Duration(1))
        eq(b/10, Duration(0, 6))
        eq(c/1000, Duration(0, 0, 1))
        eq(a/10, Duration(0, 7*24*360))
        eq(a/3600000, Duration(0, 0, 7*24*1000))

        # Multiplication by float
        us = Duration(microseconds=1)
        eq((3*us) * 0.5, 2*us)
        eq((5*us) * 0.5, 2*us)
        eq(0.5 * (3*us), 2*us)
        eq(0.5 * (5*us), 2*us)
        eq((-3*us) * 0.5, -2*us)
        eq((-5*us) * 0.5, -2*us)

        # Issue #23521
        eq(Duration(seconds=1) * 0.123456, Duration(microseconds=123456))
        eq(Duration(seconds=1) * 0.6112295, Duration(microseconds=611230))

        # Division by int and float
        eq((3*us) / 2, 2*us)
        eq((5*us) / 2, 2*us)
        eq((-3*us) / 2.0, -2*us)
        eq((-5*us) / 2.0, -2*us)
        eq((3*us) / -2, -2*us)
        eq((5*us) / -2, -2*us)
        eq((3*us) / -2.0, -2*us)
        eq((5*us) / -2.0, -2*us)
        for i in range(-10, 10):
            eq((i*us/3)//us, round(i/3))
        for i in range(-10, 10):
            eq((i*us/-3)//us, round(i/-3))

        # Issue #23521
        eq(Duration(seconds=1) / (1 / 0.6112295),
           Duration(microseconds=611230))

        # Issue #11576
        eq(Duration(999999999, 86399, 999999) -
           Duration(999999999, 86399, 999998),
           Duration(0, 0, 1))
        eq(Duration(999999999, 1, 1) - Duration(999999999, 1, 0),
           Duration(0, 0, 1))

    def test_disallowed_computations(self):
        a = Duration(42)

        # Add/sub ints or floats should be illegal
        for i in 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # Division of int by Duration doesn't make sense.
        # Division by zero doesn't make sense.
        zero = 0
        self.assertRaises(TypeError, lambda: zero // a)
        self.assertRaises(ZeroDivisionError, lambda: a // zero)
        self.assertRaises(ZeroDivisionError, lambda: a / zero)
        self.assertRaises(ZeroDivisionError, lambda: a / 0.0)
        self.assertRaises(TypeError, lambda: a / '')

    @tests.requires_IEEE_754
    def test_disallowed_special(self):
        a = Duration(42)
        self.assertRaises(ValueError, a.__mul__, NAN)
        self.assertRaises(ValueError, a.__truediv__, NAN)

    def test_basic_attributes(self):
        days, seconds, us = 1, 7, 31
        d = Duration(days, seconds, us)
        self.assertEqual(d.days, days)
        self.assertEqual(d.seconds, seconds)
        self.assertEqual(d.microseconds, us)

    def test_total_seconds(self):
        d = Duration(days=365)
        self.assertEqual(d.total_seconds(), 31536000.0)
        for total_seconds in [123456.789012, -123456.789012, 0.123456, 0, 1e6]:
            d = Duration(seconds=total_seconds)
            self.assertEqual(d.total_seconds(), total_seconds)
        # Issue8644: Test that d.total_seconds() has the same
        # accuracy as d / Duration(seconds=1).
        for ms in [-1, -2, -123]:
            d = Duration(microseconds=ms)
            self.assertEqual(d.total_seconds(), d / Duration(seconds=1))

    def test_carries(self):
        t1 = Duration(days=100,
                      weeks=-7,
                      hours=-24*(100-49),
                      minutes=-3,
                      seconds=12,
                      microseconds=(3*60 - 12) * 1e6 + 1)
        t2 = Duration(microseconds=1)
        self.assertEqual(t1, t2)

    def test_hash_equality(self):
        t1 = Duration(days=100,
                      weeks=-7,
                      hours=-24*(100-49),
                      minutes=-3,
                      seconds=12,
                      microseconds=(3*60 - 12) * 1000000)
        t2 = Duration()
        self.assertEqual(hash(t1), hash(t2))

        t1 += Duration(weeks=7)
        t2 += Duration(days=7*7)
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

        d = {t1: 1}
        d[t2] = 2
        self.assertEqual(len(d), 1)
        self.assertEqual(d[t1], 2)

    def test_pickling(self):
        args = 12, 34, 56
        orig = Duration(*args)
        for pickler, unpickler, proto in tests.pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_compare(self):
        t1 = Duration(2, 3, 4)
        t2 = Duration(2, 3, 4)
        self.assertEqual(t1, t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t1 >= t2)
        self.assertFalse(t1 != t2)
        self.assertFalse(t1 < t2)
        self.assertFalse(t1 > t2)

        for args in (3, 3, 3), (2, 4, 4), (2, 3, 5):
            t2 = Duration(*args)   # this is larger than t1
            self.assertTrue(t1 < t2)
            self.assertTrue(t2 > t1)
            self.assertTrue(t1 <= t2)
            self.assertTrue(t2 >= t1)
            self.assertTrue(t1 != t2)
            self.assertTrue(t2 != t1)
            self.assertFalse(t1 == t2)
            self.assertFalse(t2 == t1)
            self.assertFalse(t1 > t2)
            self.assertFalse(t2 < t1)
            self.assertFalse(t1 >= t2)
            self.assertFalse(t2 <= t1)

        for badarg in tests.OTHERSTUFF:
            self.assertEqual(t1 == badarg, False)
            self.assertEqual(t1 != badarg, True)
            self.assertEqual(badarg == t1, False)
            self.assertEqual(badarg != t1, True)

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_str(self):
        eq = self.assertEqual

        eq(str(Duration(1)), "1 day, 0:00:00")
        eq(str(Duration(-1)), "-1 day, 0:00:00")
        eq(str(Duration(2)), "2 days, 0:00:00")
        eq(str(Duration(-2)), "-2 days, 0:00:00")

        eq(str(Duration(hours=12, minutes=58, seconds=59)), "12:58:59")
        eq(str(Duration(hours=2, minutes=3, seconds=4)), "2:03:04")
        eq(str(Duration(weeks=-30, hours=23, minutes=12, seconds=34)),
           "-210 days, 23:12:34")

        eq(str(Duration(milliseconds=1)), "0:00:00.001000")
        eq(str(Duration(microseconds=3)), "0:00:00.000003")

        eq(str(Duration(days=999999999, hours=23, minutes=59, seconds=59,
                        microseconds=999999)),
           "999999999 days, 23:59:59.999999")

    def test_repr(self):
        name = 'tider.Duration'
        self.assertEqual(repr(Duration(1)),
                         "%s(1)" % name)
        self.assertEqual(repr(Duration(10, 2)),
                         "%s(10, 2)" % name)
        self.assertEqual(repr(Duration(-10, 2, 400000)),
                         "%s(-10, 2, 400000)" % name)

    def test_roundtrip(self):
        for d in (Duration(days=999999999, hours=23, minutes=59,
                           seconds=59, microseconds=999999),
                  Duration(days=-999999999),
                  Duration(days=-999999999, seconds=1),
                  Duration(days=1, seconds=2, microseconds=3)):

            # Verify d -> string -> d identity.
            s = repr(d)
            self.assertTrue(s.startswith('tider.Duration'))
            d2 = eval(s)
            self.assertEqual(d, d2)

            # Verify identity via reconstructing from pieces.
            d2 = Duration(d.days, d.seconds, d.microseconds)
            self.assertEqual(d, d2)

    def test_resolution_info(self):
        self.assertIsInstance(Duration.min, Duration)
        self.assertIsInstance(Duration.max, Duration)
        self.assertIsInstance(Duration.resolution, Duration)
        self.assertTrue(Duration.max > Duration.min)
        self.assertEqual(Duration.min, Duration(-999999999))
        self.assertEqual(Duration.max, Duration(999999999, 24*3600-1, 1e6-1))
        self.assertEqual(Duration.resolution, Duration(0, 0, 1))

    def test_overflow(self):
        tiny = Duration.resolution

        d = Duration.min + tiny
        d -= tiny  # no problem
        self.assertRaises(OverflowError, d.__sub__, tiny)
        self.assertRaises(OverflowError, d.__add__, -tiny)

        d = Duration.max - tiny
        d += tiny  # no problem
        self.assertRaises(OverflowError, d.__add__, tiny)
        self.assertRaises(OverflowError, d.__sub__, -tiny)

        self.assertRaises(OverflowError, lambda: -Duration.max)

        day = Duration(1)
        self.assertRaises(OverflowError, day.__mul__, 10**9)
        self.assertRaises(OverflowError, day.__mul__, 1e9)
        self.assertRaises(OverflowError, day.__truediv__, 1e-20)
        self.assertRaises(OverflowError, day.__truediv__, 1e-10)
        self.assertRaises(OverflowError, day.__truediv__, 9e-10)

    @tests.requires_IEEE_754
    def _test_overflow_special(self):
        day = Duration(1)
        self.assertRaises(OverflowError, day.__mul__, INF)
        self.assertRaises(OverflowError, day.__mul__, -INF)

    def test_microsecond_rounding(self):
        eq = self.assertEqual

        # Single-field rounding.
        eq(Duration(milliseconds=0.4/1000), Duration(0))    # rounds to 0
        eq(Duration(milliseconds=-0.4/1000), Duration(0))    # rounds to 0
        eq(Duration(milliseconds=0.5/1000), Duration(microseconds=0))
        eq(Duration(milliseconds=-0.5/1000), Duration(microseconds=0))
        eq(Duration(milliseconds=0.6/1000), Duration(microseconds=1))
        eq(Duration(milliseconds=-0.6/1000), Duration(microseconds=-1))
        eq(Duration(seconds=0.5/10**6), Duration(microseconds=0))
        eq(Duration(seconds=-0.5/10**6), Duration(microseconds=0))

        # Rounding due to contributions from more than one field.
        us_per_hour = 3600e6
        us_per_day = us_per_hour * 24
        eq(Duration(days=.4/us_per_day), Duration(0))
        eq(Duration(hours=.2/us_per_hour), Duration(0))
        eq(Duration(days=.4/us_per_day, hours=.2/us_per_hour),
           Duration(microseconds=1))

        eq(Duration(days=-.4/us_per_day), Duration(0))
        eq(Duration(hours=-.2/us_per_hour), Duration(0))
        eq(Duration(days=-.4/us_per_day, hours=-.2/us_per_hour),
           Duration(microseconds=-1))

        # Test for a patch in Issue 8860
        eq(Duration(microseconds=0.5),
           0.5*Duration(microseconds=1.0))
        eq(Duration(microseconds=0.5)//Duration.resolution,
           0.5*Duration.resolution//Duration.resolution)

    def test_massive_normalization(self):
        d = Duration(microseconds=-1)
        self.assertEqual((d.days, d.seconds, d.microseconds),
                         (-1, 24*3600-1, 999999))

    def test_bool(self):
        self.assertTrue(Duration(1))
        self.assertTrue(Duration(0, 1))
        self.assertTrue(Duration(0, 0, 1))
        self.assertTrue(Duration(microseconds=1))
        self.assertFalse(Duration(0))

    def test_subclass_duration(self):

        class T(Duration):
            @staticmethod
            def from_Duration(d):
                return T(d.days, d.seconds, d.microseconds)

            def as_hours(self):
                sum = (self.days * 24 +
                       self.seconds / 3600.0 +
                       self.microseconds / 3600e6)
                return round(sum)

        t1 = T(days=1)
        self.assertIs(type(t1), T)
        self.assertEqual(t1.as_hours(), 24)

        t2 = T(days=-1, seconds=-3600)
        self.assertIs(type(t2), T)
        self.assertEqual(t2.as_hours(), -25)

        t3 = t1 + t2
        self.assertIs(type(t3), Duration)
        t4 = T.from_Duration(t3)
        self.assertIs(type(t4), T)
        self.assertEqual(t3.days, t4.days)
        self.assertEqual(t3.seconds, t4.seconds)
        self.assertEqual(t3.microseconds, t4.microseconds)
        self.assertEqual(str(t3), str(t4))
        self.assertEqual(t4.as_hours(), -1)

    def test_multiplication(self):
        t = Duration(hours=1, minutes=24, seconds=19)
        second = Duration(seconds=1)
        self.assertEqual(second * 5059.0, t)
        self.assertEqual(t * 2, Duration(hours=2, minutes=48, seconds=38))
        self.assertRaises(TypeError, mul, t, "2")

    def test_division(self):
        t = Duration(hours=1, minutes=24, seconds=19)
        second = Duration(seconds=1)
        self.assertEqual(t / second, 5059.0)
        self.assertEqual(t // second, 5059)

        t = Duration(minutes=2, seconds=30)
        minute = Duration(minutes=1)
        self.assertEqual(t / minute, 2.5)
        self.assertEqual(t // minute, 2)

        zerod = Duration(0)
        self.assertRaises(ZeroDivisionError, truediv, t, zerod)
        self.assertRaises(ZeroDivisionError, floordiv, t, zerod)

        self.assertRaises(TypeError, truediv, t, "2")
        self.assertRaises(TypeError, floordiv, t, "2")

    def test_remainder(self):
        t = Duration(minutes=2, seconds=30)
        minute = Duration(minutes=1)
        r = t % minute
        self.assertEqual(r, Duration(seconds=30))

        t = Duration(minutes=-2, seconds=30)
        r = t % minute
        self.assertEqual(r, Duration(seconds=30))

        zerod = Duration(0)
        self.assertRaises(ZeroDivisionError, mod, t, zerod)

        self.assertRaises(TypeError, mod, t, 10)

    def test_divmod(self):
        t = Duration(minutes=2, seconds=30)
        minute = Duration(minutes=1)
        q, r = divmod(t, minute)
        self.assertEqual(q, 2)
        self.assertEqual(r, Duration(seconds=30))

        t = Duration(minutes=-2, seconds=30)
        q, r = divmod(t, minute)
        self.assertEqual(q, -2)
        self.assertEqual(r, Duration(seconds=30))

        zerod = Duration(0)
        self.assertRaises(ZeroDivisionError, divmod, t, zerod)

        self.assertRaises(TypeError, divmod, t, 10)
