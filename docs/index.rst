Tider
=====

Can I make a date/time library? I don't know, but hey, let's give it a try!

Design decisions
----------------

* Separate Date and DateTime objects. I see no usecase for Python's Time
  object, but will include for completeness.
  
* Separate Period and Duration classes, like in lubridate. They both represent
  lengths of time, but Duration is a fixed length and a Period are used for
  lengths of time that are not fixed but can vary, such as years, months and
  days.
  
* For time zone aware classes, the internal arithmetic will be based on
  UTC, not local time.

* Stores everything in separate ints, so that we are not affected by the
  Year 2038 problem and can have dates like -1000, 5, 7, etc.
  
* Implements only Gregorian calendar, but will have baseclasses/interfaces
  to implement other calendars. But probably not for other planets.
  

Implementation
--------------

Almost all code comes from other places. 

Most of Duration, Date, Time and Datetime are taken from Pythons excellent
datetime standard library module (mostly written by Tim Peters).


Changes from datetime
---------------------

* Classes are capitalized for PEP8 compatibility.

* There is less type checking. For example, tider assumes that the Timezone
  objects are correctly implemented, and returns Durations, and does not check
  that this is the case for every call.
  
  Input parameters are still checked, both for ranges and that they are
  integers (or floats, when that is allowed).

* timedelta is called Duration.

* timedelta uses a function called ``_divide_and_round()``, whose documentation
  claims that it will divide two numbers, and then round the result to an
  integer, and if the result is exactly halfway between two integers, it
  will round to the nearest even integer.
  
  However, that function does in fact not do that, but often rounds incorrectly.
  Instead of figuring out why, I just use Pythons built in ``round()`` that
  does this rounding correctly. This means for example that 
  ``Duration(seconds=1) * 0.6112295`` in fact returns a Duration that is
  611230 microseconds, where timedelta(seconds=1) * 0.6112295 will return
  a timedelta that is 611229 microseconds.
  
* The Time object does not support time zones, as those are nonsensical
  without a date anyway. This is confirmed by the tests in dateutil for
  times with timezones. There tests are only for correct rendering and 
  pickling unpickling etc. Those tests can equally well be done on the
  time zone object itself, for fixed utc offsets. For non-fixed UTC offsets,
  you can't make these tests unless you also have a date.

* The Date object is no longer restricts to years between 1 and 9999.
