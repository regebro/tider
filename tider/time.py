import time as _time  # TODO: Move all things from time into tider

from .duration import Duration
from ._utils import _check_int_field
from ._utils import _cmp, _cmperror


def _check_time_fields(hour, minute, second, microsecond):
    hour = _check_int_field(hour)
    minute = _check_int_field(minute)
    second = _check_int_field(second)
    microsecond = _check_int_field(microsecond)
    if not 0 <= hour <= 23:
        raise ValueError('hour must be in 0..23', hour)
    if not 0 <= minute <= 59:
        raise ValueError('minute must be in 0..59', minute)
    if not 0 <= second <= 59:
        raise ValueError('second must be in 0..59', second)
    if not 0 <= microsecond <= 999999:
        raise ValueError('microsecond must be in 0..999999', microsecond)
    return hour, minute, second, microsecond


def _format_time(hh, mm, ss, us):
    # Skip trailing microseconds when us==0.
    result = "%02d:%02d:%02d" % (hh, mm, ss)
    if us:
        result += ".%06d" % us
    return result


# Correctly substitute for %z and %Z escapes in strftime formats.
# TODO: Make a new strftime that does this correctly
def _wrap_strftime(object, format, timetuple):
    # Don't call utcoffset() or tzname() unless actually needed.
    freplace = None  # the string to use for %f
    zreplace = None  # the string to use for %z
    Zreplace = None  # the string to use for %Z

    # Scan format for %z and %Z escapes, replacing as needed.
    newformat = []
    push = newformat.append
    i, n = 0, len(format)
    while i < n:
        ch = format[i]
        i += 1
        if ch == '%':
            if i < n:
                ch = format[i]
                i += 1
                if ch == 'f':
                    if freplace is None:
                        freplace = '%06d' % getattr(object,
                                                    'microsecond', 0)
                    newformat.append(freplace)
                elif ch == 'z':
                    if zreplace is None:
                        zreplace = ""
                        if hasattr(object, "utcoffset"):
                            offset = object.utcoffset()
                            if offset is not None:
                                sign = '+'
                                if offset.days < 0:
                                    offset = -offset
                                    sign = '-'
                                h, m = divmod(offset, Duration(hours=1))
                                fraction = m % Duration(minutes=1)
                                assert not fraction, "whole minute"
                                m //= Duration(minutes=1)
                                zreplace = '%c%02d%02d' % (sign, h, m)
                    assert '%' not in zreplace
                    newformat.append(zreplace)
                elif ch == 'Z':
                    if Zreplace is None:
                        Zreplace = ""
                        if hasattr(object, "tzname"):
                            s = object.tzname()
                            if s is not None:
                                # strftime is going to have at this: escape %
                                Zreplace = s.replace('%', '%%')
                    newformat.append(Zreplace)
                else:
                    push('%')
                    push(ch)
            else:
                push('%')
        else:
            push(ch)
    newformat = "".join(newformat)
    return _time.strftime(newformat, timetuple)

class Time(object):
    """A time object"""

    __slots__ = ('_hour', '_minute', '_second', '_microsecond', '_hashcode')

    def __new__(cls, hour=0, minute=0, second=0, microsecond=0):
        """Constructor.

        Arguments:

        hour, minute (required)
        second, microsecond (default to zero)
        """
        if isinstance(hour, bytes) and len(hour) == 6 and hour[0] < 24:
            # Pickle support
            self = object.__new__(cls)
            self.__setstate(hour, minute or None)
            self._hashcode = -1
            return self
        hour, minute, second, microsecond = _check_time_fields(
            hour, minute, second, microsecond)
        self = object.__new__(cls)
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._hashcode = -1
        return self

    # Read-only field accessors
    @property
    def hour(self):
        """hour (0-23)"""
        return self._hour

    @property
    def minute(self):
        """minute (0-59)"""
        return self._minute

    @property
    def second(self):
        """second (0-59)"""
        return self._second

    @property
    def microsecond(self):
        """microsecond (0-999999)"""
        return self._microsecond

    # Standard conversions, __hash__ (and helpers)

    # Comparisons of Time objects with other.

    def __eq__(self, other):
        if isinstance(other, Time):
            return self._cmp(other, allow_mixed=True) == 0
        else:
            return False

    def __le__(self, other):
        if isinstance(other, Time):
            return self._cmp(other) <= 0
        else:
            _cmperror(self, other)

    def __lt__(self, other):
        if isinstance(other, Time):
            return self._cmp(other) < 0
        else:
            _cmperror(self, other)

    def __ge__(self, other):
        if isinstance(other, Time):
            return self._cmp(other) >= 0
        else:
            _cmperror(self, other)

    def __gt__(self, other):
        if isinstance(other, Time):
            return self._cmp(other) > 0
        else:
            _cmperror(self, other)

    def _cmp(self, other, allow_mixed=False):
        assert isinstance(other, Time)
        myoff = otoff = None

        return _cmp((self._hour, self._minute, self._second,
                     self._microsecond),
                    (other._hour, other._minute, other._second,
                     other._microsecond))

    def __hash__(self):
        """Hash."""
        if self._hashcode == -1:
            self._hashcode = hash(self._getstate()[0])
        return self._hashcode

    def __repr__(self):
        """Convert to formal string, for repr()."""
        if self._microsecond != 0:
            s = ", %d, %d" % (self._second, self._microsecond)
        elif self._second != 0:
            s = ", %d" % self._second
        else:
            s = ""
        s = "%s.%s(%d, %d%s)" % (self.__class__.__module__,
                                 self.__class__.__qualname__,
                                 self._hour, self._minute, s)
        return s

    def isoformat(self):
        """Return the Time formatted according to ISO.

        This is 'HH:MM:SS.mmmmmm+zz:zz', or 'HH:MM:SS+zz:zz' if
        self.microsecond == 0.
        """
        return _format_time(self._hour, self._minute, self._second,
                         self._microsecond)

    __str__ = isoformat

    def strftime(self, fmt):
        """Format using strftime().  The date part of the timestamp passed
        to underlying strftime should not be used.
        """
        # The year must be >= 1000 else Python's strftime implementation
        # can raise a bogus exception.
        timetuple = (1900, 1, 1,
                     self._hour, self._minute, self._second,
                     0, 1, -1)
        return _wrap_strftime(self, fmt, timetuple)

    def __format__(self, fmt):
        if not isinstance(fmt, str):
            raise TypeError("must be str, not %s" % type(fmt).__name__)
        if len(fmt) != 0:
            return self.strftime(fmt)
        return str(self)

    def replace(self, hour=None, minute=None, second=None, microsecond=None):
        """Return a new Time with new values for the specified fields."""
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        return Time(hour, minute, second, microsecond)

    # Pickle support.

    def _getstate(self):
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        basestate = bytes([self._hour, self._minute, self._second,
                           us1, us2, us3])
        return (basestate,)

    def __setstate(self, string, tzinfo):
        self._hour, self._minute, self._second, us1, us2, us3 = string
        self._microsecond = (((us1 << 8) | us2) << 8) | us3

    def __reduce__(self):
        return (Time, self._getstate())

Time.min = Time(0, 0, 0)
Time.max = Time(23, 59, 59, 999999)
Time.resolution = Duration(microseconds=1)
