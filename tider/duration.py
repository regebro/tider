from __future__ import division
import math

from ._utils import _cmp, _cmperror


class Duration(object):
    """Represent a duration of time, such as "5 seconds" or "2 hours".

    A Duration is used for doing time based arithmetic. If you subtract
    a Datetime from another Datetime the result is a Duration.
    """
    __slots__ = '_days', '_seconds', '_microseconds', '_hashcode'

    def __new__(cls, days=0, seconds=0, microseconds=0,
                milliseconds=0, minutes=0, hours=0, weeks=0):
        # Doing this efficiently and accurately in C is going to be difficult
        # and error-prone, due to ubiquitous overflow possibilities, and that
        # C double doesn't have enough bits of precision to represent
        # microseconds over 10K years faithfully.  The code here tries to make
        # explicit where go-fast assumptions can be relied on, in order to
        # guide the C implementation; it's way more convoluted than speed-
        # ignoring auto-overflow-to-long idiomatic Python could be.

        # Final values, all integer.
        # s and us fit in 32-bit signed ints; d isn't bounded.
        d = s = us = 0

        # Normalize everything to days, seconds, microseconds.
        days += weeks*7
        seconds += minutes*60 + hours*3600
        microseconds += milliseconds*1000

        # Get rid of all fractions, and normalize s and us.
        # Take a deep breath <wink>.
        if isinstance(days, float):
            dayfrac, days = math.modf(days)
            daysecondsfrac, daysecondswhole = math.modf(dayfrac * 86400)
            s = int(daysecondswhole)
            d = int(days)
        elif isinstance(days, int):
            daysecondsfrac = 0.0
            d = days
        else:
            raise ValueError('The "days" argument must be int or float.')
        # days isn't referenced again before redefinition

        if isinstance(seconds, float):
            secondsfrac, seconds = math.modf(seconds)
            seconds = int(seconds)
            secondsfrac += daysecondsfrac
        elif isinstance(seconds, int):
            secondsfrac = daysecondsfrac
        else:
            raise ValueError('The "seconds" argument must be int or float.')
        # daysecondsfrac isn't referenced again

        days, seconds = divmod(seconds, 86400)
        d += days
        s += seconds
        # seconds isn't referenced again before redefinition

        us = secondsfrac * 1e6
        # secondsfrac isn't referenced again

        if isinstance(microseconds, float):
            microseconds = round(microseconds + us)
            seconds, microseconds = divmod(microseconds, 1000000)
            # On Python 2, divmod returns whole number floats for the quotient
            # if the argument is a float, so we force seconds to be an int:
            days, seconds = divmod(int(seconds), 86400)
            d += days
            s += seconds
        elif isinstance(microseconds, int):
            microseconds = int(microseconds)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 86400)
            d += days
            s += seconds
            microseconds = round(microseconds + us)
        else:
            raise ValueError('The "microseconds" argument must be int or float.')

        # Just a little bit of carrying possible for microseconds and seconds.
        seconds, us = divmod(microseconds, 1000000)
        s += int(seconds)
        days, s = divmod(s, 86400)
        d += days

        # Finally assert that we didn't mess upp somewhere:
        assert isinstance(d, int)
        assert isinstance(s, int) and 0 <= s < 86400
        assert isinstance(us, int) and 0 <= us < 1000000

        if abs(d) > 999999999:
            raise OverflowError("Duration # of days is too large: %d" % d)

        self = object.__new__(cls)
        self._days = d
        self._seconds = s
        self._microseconds = us
        self._hashcode = -1
        return self

    def __repr__(self):
        if self._microseconds:
            return "tider.Duration(%d, %d, %d)" % (self._days,
                                                   self._seconds,
                                                   self._microseconds)
        if self._seconds:
            return "tider.Duration(%d, %d)" % (self._days,
                                               self._seconds)
        return "tider.Duration(%d)" % (self._days)

    def __str__(self):
        mm, ss = divmod(self._seconds, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d:%02d" % (hh, mm, ss)
        if self._days:
            def plural(n):
                return n, abs(n) != 1 and "s" or ""
            s = ("%d day%s, " % plural(self._days)) + s
        if self._microseconds:
            s = s + ".%06d" % self._microseconds
        return s

    def total_seconds(self):
        """Total seconds in the duration."""
        return ((self.days * 86400 + self.seconds) * 10**6 +
                self.microseconds) / 10**6

    # Read-only field accessors
    @property
    def days(self):
        """days"""
        return self._days

    @property
    def seconds(self):
        """seconds"""
        return self._seconds

    @property
    def microseconds(self):
        """microseconds"""
        return self._microseconds

    def __add__(self, other):
        if isinstance(other, Duration):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real Duration
            return Duration(self._days + other._days,
                            self._seconds + other._seconds,
                            self._microseconds + other._microseconds)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Duration):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real Duration
            return Duration(self._days - other._days,
                            self._seconds - other._seconds,
                            self._microseconds - other._microseconds)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Duration):
            return -self + other
        return NotImplemented

    def __neg__(self):
        # for CPython compatibility, we cannot use
        # our __class__ here, but need a real Duration
        return Duration(-self._days,
                        -self._seconds,
                        -self._microseconds)

    def __pos__(self):
        return self

    def __abs__(self):
        if self._days < 0:
            return -self
        else:
            return self

    def __mul__(self, other):
        if isinstance(other, int):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real Duration
            return Duration(self._days * other,
                            self._seconds * other,
                            self._microseconds * other)
        if isinstance(other, float):
            usec = self._to_microseconds()
            return Duration(0, 0, usec * other)
        return NotImplemented

    __rmul__ = __mul__

    def _to_microseconds(self):
        return ((self._days * 86400 + self._seconds) * 1000000 +
                self._microseconds)

    def __floordiv__(self, other):
        if not isinstance(other, (int, Duration)):
            return NotImplemented
        usec = self._to_microseconds()
        if isinstance(other, Duration):
            return usec // other._to_microseconds()
        if isinstance(other, int):
            return Duration(0, 0, usec // other)

    def __truediv__(self, other):
        if not isinstance(other, (int, float, Duration)):
            return NotImplemented
        usec = self._to_microseconds()
        if isinstance(other, Duration):
            return usec / other._to_microseconds()
        if isinstance(other, int):
            return Duration(0, 0, round(usec/other))
        if isinstance(other, float):
            return Duration(0, 0, round(usec/other))

    def __mod__(self, other):
        if isinstance(other, Duration):
            r = self._to_microseconds() % other._to_microseconds()
            return Duration(0, 0, r)
        return NotImplemented

    def __divmod__(self, other):
        if isinstance(other, Duration):
            q, r = divmod(self._to_microseconds(),
                          other._to_microseconds())
            return q, Duration(0, 0, r)
        return NotImplemented

    # Comparisons of Duration objects with other.

    def __eq__(self, other):
        if isinstance(other, Duration):
            return self._cmp(other) == 0
        else:
            return False

    def __le__(self, other):
        if isinstance(other, Duration):
            return self._cmp(other) <= 0
        else:
            _cmperror(self, other)

    def __lt__(self, other):
        if isinstance(other, Duration):
            return self._cmp(other) < 0
        else:
            _cmperror(self, other)

    def __ge__(self, other):
        if isinstance(other, Duration):
            return self._cmp(other) >= 0
        else:
            _cmperror(self, other)

    def __gt__(self, other):
        if isinstance(other, Duration):
            return self._cmp(other) > 0
        else:
            _cmperror(self, other)

    def _cmp(self, other):
        assert isinstance(other, Duration)
        return _cmp(self._getstate(), other._getstate())

    def __hash__(self):
        if self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        return self._hashcode

    def __bool__(self):
        return (self._days != 0 or
                self._seconds != 0 or
                self._microseconds != 0)

    # Pickle support.
    def _getstate(self):
        return (self._days, self._seconds, self._microseconds)

    def __reduce__(self):
        return (self.__class__, self._getstate())


# Why is there even max and mins? We can handle sys.maxsize.
Duration.min = Duration(-999999999)
Duration.max = Duration(days=999999999, hours=23, minutes=59, seconds=59,
                        microseconds=999999)
Duration.resolution = Duration(microseconds=1)
