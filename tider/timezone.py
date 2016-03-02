from .duration import Duration
from .datetime import Datetime


class FixedTimezone(object):

    def __init__(self, offset, name=None):
        if not isinstance(offset, Duration):
            raise TypeError("offset must be a Duration")
        elif name is not None and not isinstance(name, str):
            raise TypeError("name must be a string or None")
        if not self._minoffset <= offset <= self._maxoffset:
            raise ValueError("offset must be a Duration"
                             " strictly between -Duration(hours=24) and"
                             " Duration(hours=24).")
        if (offset.microseconds != 0 or
            offset.seconds % 60 != 0):
            raise ValueError("offset must be a Duration"
                             " representing a whole number of minutes")

        self._offset = offset
        self._name = name

    def __getinitargs__(self):
        """pickle support"""
        if self._name is None:
            return (self._offset,)
        return (self._offset, self._name)

    def __eq__(self, other):
        if type(other) != FixedTimezone:
            return False
        return self._offset == other._offset

    def __hash__(self):
        return hash(self._offset)

    def __repr__(self):
        """Convert to formal string, for repr().

        >>> tz = FixedTimezone.utc
        >>> repr(tz)
        'Datetime.FixedTimezone.utc'
        >>> tz = FixedTimezone(Duration(hours=-5), 'EST')
        >>> repr(tz)
        "Datetime.FixedTimezone(Datetime.Duration(-1, 68400), 'EST')"
        """
        if self is self.utc:
            return 'tider.FixedTimezone.utc'
        if self._name is None:
            return "%s(%r)" % ('tider.' + self.__class__.__name__,
                               self._offset)
        return "%s(%r, %r)" % ('tider.' + self.__class__.__name__,
                               self._offset, self._name)

    def __str__(self):
        return self.tzname(None)

    def utcoffset(self, dt):
        if isinstance(dt, Datetime) or dt is None:
            return self._offset
        raise TypeError("utcoffset() argument must be a Datetime instance"
                        " or None")

    def tzname(self, dt):
        if isinstance(dt, Datetime) or dt is None:
            if self._name is None:
                return self._name_from_offset(self._offset)
            return self._name
        raise TypeError("tzname() argument must be a Datetime instance"
                        " or None")

    def dst(self, dt):
        if isinstance(dt, Datetime) or dt is None:
            return None
        raise TypeError("dst() argument must be a Datetime instance"
                        " or None")

    def fromutc(self, dt):
        if isinstance(dt, Datetime):
            if dt.tzinfo is not self:
                raise ValueError("fromutc: dt.tzinfo "
                                 "is not self")
            return dt + self._offset
        raise TypeError("fromutc() argument must be a Datetime instance"
                        " or None")

    _maxoffset = Duration(hours=23, minutes=59)
    _minoffset = -_maxoffset

    @staticmethod
    def _name_from_offset(delta):
        if delta < Duration(0):
            sign = '-'
            delta = -delta
        else:
            sign = '+'
        hours, rest = divmod(delta, Duration(hours=1))
        minutes = rest // Duration(minutes=1)
        return 'UTC{}{:02d}:{:02d}'.format(sign, hours, minutes)


FixedTimezone.utc = FixedTimezone(Duration(0))
FixedTimezone.min = FixedTimezone(FixedTimezone._minoffset)
FixedTimezone.max = FixedTimezone(FixedTimezone._maxoffset)
