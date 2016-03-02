import unittest
import tider  # Must be imported for eval to work in the roundtrip test.

from tider import FixedTimezone, Duration, Datetime


ZERO = Duration(0)
MINUTE = Duration(minutes=1)
HOUR = Duration(hours=1)
DAY = Duration(days=1)


class TestFixedTimezone(unittest.TestCase):

    def setUp(self):
        self.ACDT = FixedTimezone(Duration(hours=9.5), 'ACDT')
        self.EST = FixedTimezone(-Duration(hours=5), 'EST')
        #self.DT = Datetime(2010, 1, 1)

    def test_str(self):
        for tz in [self.ACDT, self.EST, FixedTimezone.utc,
                   FixedTimezone.min, FixedTimezone.max]:
            self.assertEqual(str(tz), tz.tzname(None))

    def test_repr(self):
        for tz in [self.ACDT, self.EST, FixedTimezone.utc,
                   FixedTimezone.min, FixedTimezone.max]:
            # test round-trip
            tzrep = repr(tz)
            self.assertEqual(tz, eval(tzrep))

    def test_class_members(self):
        limit = Duration(hours=23, minutes=59)
        self.assertEqual(FixedTimezone.utc.utcoffset(None), ZERO)
        self.assertEqual(FixedTimezone.min.utcoffset(None), -limit)
        self.assertEqual(FixedTimezone.max.utcoffset(None), limit)

    def test_constructor(self):
        self.assertEqual(FixedTimezone.utc, FixedTimezone(Duration(0), 'UTC'))
        # invalid offsets
        for invalid in [Duration(microseconds=1), Duration(1, 1),
                        Duration(seconds=1), Duration(1), -Duration(1)]:
            self.assertRaises(ValueError, FixedTimezone, invalid)
            self.assertRaises(ValueError, FixedTimezone, -invalid)

        with self.assertRaises(TypeError): FixedTimezone(42)
        with self.assertRaises(TypeError): FixedTimezone(ZERO, 42)
        with self.assertRaises(TypeError): FixedTimezone(ZERO, 'ABC', 'extra')

    def test_inheritance(self):
        self.assertIsInstance(FixedTimezone.utc, FixedTimezone)
        self.assertIsInstance(self.EST, FixedTimezone)

    #def test_utcoffset(self):
        #dummy = self.DT
        #for h in [0, 1.5, 12]:
            #offset = h * HOUR
            #self.assertEqual(offset, FixedTimezone(offset).utcoffset(dummy))
            #self.assertEqual(-offset, FixedTimezone(-offset).utcoffset(dummy))

        #with self.assertRaises(TypeError): self.EST.utcoffset('')
        #with self.assertRaises(TypeError): self.EST.utcoffset(5)

    #def test_dst(self):
        #self.assertIsNone(FixedTimezone.utc.dst(self.DT))

        #with self.assertRaises(TypeError): self.EST.dst('')
        #with self.assertRaises(TypeError): self.EST.dst(5)

    def test_tzname(self):
        self.assertEqual('UTC+00:00', FixedTimezone(ZERO).tzname(None))
        self.assertEqual('UTC-05:00', FixedTimezone(-5 * HOUR).tzname(None))
        self.assertEqual('UTC+09:30', FixedTimezone(9.5 * HOUR).tzname(None))
        self.assertEqual('UTC-00:01', FixedTimezone(Duration(minutes=-1)).tzname(None))
        self.assertEqual('XYZ', FixedTimezone(-5 * HOUR, 'XYZ').tzname(None))

        with self.assertRaises(TypeError): self.EST.tzname('')
        with self.assertRaises(TypeError): self.EST.tzname(5)

    #def test_fromutc(self):
        #with self.assertRaises(ValueError):
            #FixedTimezone.utc.fromutc(self.DT)
        #with self.assertRaises(TypeError):
            #FixedTimezone.utc.fromutc('not Datetime')
        #for tz in [self.EST, self.ACDT, Eastern]:
            #utctime = self.DT.replace(tzinfo=tz)
            #local = tz.fromutc(utctime)
            #self.assertEqual(local - utctime, tz.utcoffset(local))
            #self.assertEqual(local,
                             #self.DT.replace(tzinfo=FixedTimezone.utc))

    def test_comparison(self):
        self.assertNotEqual(FixedTimezone(ZERO), FixedTimezone(HOUR))
        self.assertEqual(FixedTimezone(HOUR), FixedTimezone(HOUR))
        self.assertEqual(FixedTimezone(-5 * HOUR), FixedTimezone(-5 * HOUR, 'EST'))
        with self.assertRaises(TypeError): FixedTimezone(ZERO) < FixedTimezone(ZERO)
        self.assertIn(FixedTimezone(ZERO), {FixedTimezone(ZERO)})
        self.assertTrue(FixedTimezone(ZERO) != None)
        self.assertFalse(FixedTimezone(ZERO) ==  None)

    #def test_aware_Datetime(self):
        ## test that FixedTimezone instances can be used by Datetime
        #t = Datetime(1, 1, 1)
        #for tz in [FixedTimezone.min, FixedTimezone.max, FixedTimezone.utc]:
            #self.assertEqual(tz.tzname(t),
                             #t.replace(tzinfo=tz).tzname())
            #self.assertEqual(tz.utcoffset(t),
                             #t.replace(tzinfo=tz).utcoffset())
            #self.assertEqual(tz.dst(t),
                             #t.replace(tzinfo=tz).dst())

