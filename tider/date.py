import time as _time

from .duration import Duration
from ._utils import _cmp, _build_struct_time, _ymd2ord, _ord2ymd
from ._utils import _wrap_strftime, _check_date_fields, _isoweek1monday
from ._utils import _MAXORDINAL, _DAYNAMES, _MONTHNAMES


class BaseDate:
    """Base for concrete Date types.

    Constructors:

    __init__()
    fromtimestamp()
    today()
    fromordinal()

    Operators:

    __repr__, __str__, __hash__
    __add__, __radd__, __sub__ (add/radd only with Duration arg)

    Methods:

    timetuple()
    toordinal()
    weekday()
    isoweekday(), isocalendar(), isoformat()
    ctime()
    strftime()

    Properties (readonly):
    year, month, day
    """
    __slots__ = '_year', '_month', '_day'

    def __init__(self, year, month=None, day=None):
        """Constructor.

        Arguments:

        year, month, day
        """
        _check_date_fields(year, month, day)
        self._year = year
        self._month = month
        self._day = day

    # Additional constructors

    @classmethod
    def fromtimestamp(cls, t):
        "Construct a Date from a POSIX timestamp (like time.time())."
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.localtime(t)
        return cls(y, m, d)

    @classmethod
    def today(cls):
        "Construct a Date from time.time()."
        t = _time.time()
        return cls.fromtimestamp(t)

    @classmethod
    def fromordinal(cls, n):
        """Contruct a Date from a proleptic Gregorian ordinal.

        January 1 of year 1 is day 1.  Only the year, month and day are
        non-zero in the result.
        """
        y, m, d = _ord2ymd(n)
        return cls(y, m, d)

    # Conversions to string

    def __repr__(self):
        """Convert to formal string, for repr().

        >>> dt = Basedate(2010, 1, 1)
        >>> repr(dt)
        'tider.Basedate(2010, 1, 1)'
        """
        return "%s(%d, %d, %d)" % ('Datetime.' + self.__class__.__name__,
                                   self._year,
                                   self._month,
                                   self._day)
    # XXX These shouldn't depend on time.localtime(), because that
    # clips the usable dates to [1970 .. 2038).  At least ctime() is
    # easily done without using strftime() -- that's better too because
    # strftime("%c", ...) is locale specific.


    def ctime(self):
        "Return ctime() style string."
        weekday = self.toordinal() % 7 or 7
        return "%s %s %2d 00:00:00 %04d" % (
            _DAYNAMES[weekday],
            _MONTHNAMES[self._month],
            self._day, self._year)

    def strftime(self, fmt):
        "Format using strftime()."
        return _wrap_strftime(self, fmt, self.timetuple())

    def __format__(self, fmt):
        if len(fmt) != 0:
            return self.strftime(fmt)
        return str(self)

    def isoformat(self):
        """Return the Date formatted according to ISO.

        This is 'YYYY-MM-DD'.

        References:
        - http://www.w3.org/TR/NOTE-Datetime
        - http://www.cl.cam.ac.uk/~mgk25/iso-time.html
        """
        return "%04d-%02d-%02d" % (self._year, self._month, self._day)

    __str__ = isoformat

    # Read-only field accessors
    @property
    def year(self):
        """year (1-9999)"""
        return self._year

    @property
    def month(self):
        """month (1-12)"""
        return self._month

    @property
    def day(self):
        """day (1-31)"""
        return self._day

    # Standard conversions, comparisons, __hash__ (and helpers)

    def timetuple(self):
        "Return local time tuple compatible with time.localtime()."
        return _build_struct_time(self._year, self._month, self._day,
                                  0, 0, 0, -1)

    def toordinal(self):
        """Return proleptic Gregorian ordinal for the year, month and day.

        January 1 of year 1 is day 1.  Only the year, month and day values
        contribute to the result.
        """
        return _ymd2ord(self._year, self._month, self._day)

    def replace(self, year=None, month=None, day=None):
        """Return a new Date with new values for the specified fields."""
        if year is None:
            year = self._year
        if month is None:
            month = self._month
        if day is None:
            day = self._day
        _check_date_fields(year, month, day)
        return self.__class__(year, month, day)

    # Comparisons of Date objects with other.

    def __eq__(self, other):
        if isinstance(other, BaseDate):
            return self._cmp(other) == 0
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, BaseDate):
            return self._cmp(other) != 0
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, BaseDate):
            return self._cmp(other) <= 0
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, BaseDate):
            return self._cmp(other) < 0
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, BaseDate):
            return self._cmp(other) >= 0
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, BaseDate):
            return self._cmp(other) > 0
        return NotImplemented

    def _cmp(self, other):
        assert isinstance(other, BaseDate)
        this = self._year, self._month, self._day
        other = other._year, other._month, other._day
        return _cmp(this, other)

    def __hash__(self):
        "Hash."
        return hash(self._getstate())

    # Computations

    def __add__(self, other):
        "Add a BaseDate to a Duration."
        if isinstance(other, Duration):
            o = self.toordinal() + other.days
            if 0 < o <= _MAXORDINAL:
                return BaseDate.fromordinal(o)
            raise OverflowError("result out of range")
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        """Subtract two dates, or a BaseDate and a Duration."""
        if isinstance(other, Duration):
            return self + Duration(-other.days)
        if isinstance(other, BaseDate):
            days1 = self.toordinal()
            days2 = other.toordinal()
            return Duration(days1 - days2)
        return NotImplemented

    def weekday(self):
        "Return day of the week, where Monday == 0 ... Sunday == 6."
        return (self.toordinal() + 6) % 7

    # Day-of-the-week and week-of-the-year, according to ISO

    def isoweekday(self):
        "Return day of the week, where Monday == 1 ... Sunday == 7."
        # 1-Jan-0001 is a Monday
        return self.toordinal() % 7 or 7

    def isocalendar(self):
        """Return a 3-tuple containing ISO year, week number, and weekday.

        The first ISO week of the year is the (Mon-Sun) week
        containing the year's first Thursday; everything else derives
        from that.

        The first week is 1; Monday is 1 ... Sunday is 7.

        ISO calendar algorithm taken from
        http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        """
        year = self._year
        week1monday = _isoweek1monday(year)
        today = _ymd2ord(self._year, self._month, self._day)
        # Internally, week and day have origin 0
        week, day = divmod(today - week1monday, 7)
        if week < 0:
            year -= 1
            week1monday = _isoweek1monday(year)
            week, day = divmod(today - week1monday, 7)
        elif week >= 52:
            if today >= _isoweek1monday(year+1):
                year += 1
                week = 0
        return year, week+1, day+1

    # Pickle support.

    def _getstate(self):
        return self._year, self._month, self._day

    def __setstate(self, string):
        import pdb;pdb.set_trace()
        self._year, self._month, self._day = string

    def __reduce__(self):
        return (self.__class__, self._getstate())


BaseDate.resolution = Duration(days=1)

# For the time, let's use just Gregorian Astronomical dates. That's wrong,
# but the best way of implementing other dates takes thinking.
Date = BaseDate
