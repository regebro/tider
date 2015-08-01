# Various internal helper functions


# The repetitive bit of comparisons

def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def _cmperror(x, y):
    raise TypeError("can't compare '%s' to '%s'" % (
                    type(x).__name__, type(y).__name__))


# Argument assertions

def _check_int_field(value):
    if isinstance(value, int):
        return value
    if not isinstance(value, float):
        try:
            value = value.__int__()
        except AttributeError:
            pass
        else:
            if isinstance(value, int):
                return value
            raise TypeError('__int__ returned non-int (type %s)' %
                            type(value).__name__)
        raise TypeError('an integer is required (got type %s)' %
                        type(value).__name__)
    raise TypeError('integer argument expected, got float')
