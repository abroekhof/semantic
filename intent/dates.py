import re
import datetime
from numbers import NumberService


def safe(exp):
    """For safe evaluation of regex groups"""
    try:
        return exp()
    except:
        return False


class DateService(object):

    def __init__(self, tz=None, now=None):
        self.tz = tz
        if now:
            self.now = now
        else:
            self.now = datetime.datetime.now(tz=self.tz)

    __months__ = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november',
                  'december']

    __shortMonths__ = ['jan', 'feb', 'mar', 'apr', 'may',
                       'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec']

    __daysOfWeek__ = ['monday', 'tuesday', 'wednesday',
                      'thursday', 'friday', 'saturday', 'sunday']

    __relativeDates__ = ['tomorrow', 'tonight', 'next']

    __todayMatches__ = ['tonight', 'today', 'this morning',
                        'this evening', 'this afternoon']

    __tomorrowMatches__ = ['tomorrow', 'next morning',
                           'next evening', 'next afternoon']

    __dateDescriptors__ = {
        'one': 1,
        'first': 1,
        'two': 2,
        'second': 2,
        'three': 3,
        'third': 3,
        'four': 4,
        'fourth': 4,
        'five': 5,
        'fifth': 5,
        'six': 6,
        'sixth': 6,
        'seven': 7,
        'seventh': 7,
        'eight': 8,
        'eighth': 8,
        'nine': 9,
        'ninth': 9,
        'ten': 10,
        'tenth': 10,
        'eleven': 11,
        'eleventh': 11,
        'twelve': 12,
        'twelth': 12,
        'thirteen': 13,
        'thirteenth': 13,
        'fourteen': 14,
        'fourteenth': 14,
        'fifteen': 15,
        'fifteenth': 15,
        'sixteen': 16,
        'sixteenth': 16,
        'seventeen': 17,
        'seventeenth': 17,
        'eighteen': 18,
        'eighteenth': 18,
        'nineteen': 19,
        'nineteenth': 19,
        'twenty': 20,
        'twentieth': 20,
        'twenty one': 21,
        'twenty first': 21,
        'twenty two': 22,
        'twenty second': 22,
        'twenty three': 23,
        'twenty third': 23,
        'twenty four': 24,
        'twenty fourth': 24,
        'twenty five': 25,
        'twenty fifth': 25,
        'twenty six': 26,
        'twenty sixth': 26,
        'twenty seven': 27,
        'twenty seventh': 27,
        'twenty eight': 28,
        'twenty eighth': 28,
        'twenty nine': 29,
        'twenty ninth': 29,
        'thirty': 30,
        'thirtieth': 30,
        'thirty one': 31,
        'thirty first': 31
    }

    dayRegex = re.compile(
        r"""(?ix)
        ((week|day)s?\ from\ )?
        (
            tomorrow
            |tonight
            |today
            |(next|this)?[\ \b](morning|afternoon|evening|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)
            |(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\ (\w+)((\s|\-)?\w*)
        )
        """)

    timeRegex = re.compile(
        r"""(?ix)
        .*?
        (
            morning
            |afternoon
            |evening
            |(\d{2}\:\d{2})\ ?(am|pm)?
            |in\ (.+?)\ (hours|minutes)(\ (?:and\ )?(.+?)\ (hours|minutes))?
        )
        .*?""")

    def preprocess(self, input):
        return input.replace('-', ' ').lower()

    def parseDay(self, input):
        """Extracts day-related information from an input string."""
        input = self.preprocess(input)

        def extractDayOfWeek(dayMatch):
            return self.__daysOfWeek__.index(dayMatch.group(5))

        def extractMonth(dayMatch):
            if dayMatch.group(6) in self.__months__:
                return self.__months__.index(dayMatch.group(6)) + 1
            elif dayMatch.group(6) in self.__shortMonths__:
                return self.__shortMonths__.index(dayMatch.group(6)) + 1

        def extractDay(dayMatch):
            combined = dayMatch.group(7) + dayMatch.group(8)
            if combined in self.__dateDescriptors__:
                return self.__dateDescriptors__[combined]
            elif dayMatch.group(7) in self.__dateDescriptors__:
                return self.__dateDescriptors__[dayMatch.group(7)]
            elif int(dayMatch.group(7)) in self.__dateDescriptors__.values():
                return int(dayMatch.group(7))

        def extractDaysFrom(dayMatch):
            if not dayMatch.group(1):
                return 0

            def numericalPrefix(dayMatch):
                # Grab 'three' of 'three weeks from'
                prefix = input.split(dayMatch.group(1))[0].strip().split(' ')
                prefix.reverse()
                prefix = filter(lambda s: s != 'and', prefix)

                # Generate best guess number
                service = NumberService()
                num = prefix[0]
                if service.isValid(num):
                    for n in prefix[1:]:
                        inc = n + " " + num
                        if service.isValid(inc):
                            num = inc
                        else:
                            break
                    return service.parse(num)
                return 1

            factor = numericalPrefix(dayMatch)

            if dayMatch.group(2) == 'week':
                return factor * 7
            elif dayMatch.group(2) == 'day':
                return factor * 1

        dayMatch = self.dayRegex.search(input)

        # Extract key terms
        days_from = safe(lambda: extractDaysFrom(dayMatch))
        today = safe(lambda: dayMatch.group(3) in self.__todayMatches__)
        tomorrow = safe(lambda: dayMatch.group(3) in self.__tomorrowMatches__)
        next_week = safe(lambda: dayMatch.group(4) == 'next')
        day_of_week = safe(lambda: extractDayOfWeek(dayMatch))
        month = safe(lambda: extractMonth(dayMatch))
        day = safe(lambda: extractDay(dayMatch))

        # Convert extracted terms to datetime object
        if not dayMatch:
            return None
        elif today:
            d = self.now
        elif tomorrow:
            d = self.now + datetime.timedelta(days=1)
        elif day_of_week:
            current_day_of_week = self.now.weekday()
            num_days_away = (day_of_week - current_day_of_week) % 7

            if next_week:
                num_days_away += 7

            d = self.now + \
                datetime.timedelta(days=num_days_away)
        elif month and day:
            d = datetime.datetime(
                self.now.year, month, day,
                self.now.hour, self.now.minute)

        if days_from:
            d += datetime.timedelta(days=days_from)

        return d

    def parseTime(self, input):
        """
        Extracts time information from an input string. Assumes that the
        time is referencing 'today' or that any relative time is in terms
        of minutes or hours from now.
        """
        input = self.preprocess(input)

        time = self.timeRegex.match(input)
        relative = False

        if not time:
            return None

        # Default times: 8am, 12pm, 7pm
        elif time.group(1) == 'morning':
            h = 8
            m = 0
        elif time.group(1) == 'afternoon':
            h = 12
            m = 0
        elif time.group(1) == 'evening':
            h = 19
            m = 0
        elif time.group(4) and time.group(5):
            h, m = 0, 0

            # Extract hours difference
            converter = NumberService()
            try:
                diff = converter.parse(time.group(4))
            except:
                return None

            if time.group(5) == 'hours':
                h += diff
            else:
                m += diff

            # Extract minutes difference
            if time.group(6):
                converter = NumberService()
                try:
                    diff = converter.parse(time.group(7))
                except:
                    return None

                if time.group(8) == 'hours':
                    h += diff
                else:
                    m += diff

            relative = True
        else:
            # Convert from "HH:MM pm" format
            t = time.group(2)
            h, m = int(t.split(':')[0]) % 12, int(t.split(':')[1])

            try:
                if time.group(3) == 'pm':
                    h += 12
            except IndexError:
                pass

        if relative:
            return self.now + datetime.timedelta(hours=h, minutes=m)
        else:
            return datetime.datetime(
                self.now.year, self.now.month, self.now.day, h, m
            )

    def parseDate(self, input):
        """
        Extract semantic date information from an input string.

        Arguments:
        input -- string to be parsed.
        tz -- the current timezone (a pytz object)
        now -- the time from which relative dates should be calculated.
               Assumed to be datetime.datetime.now(tz=tz) if not provided.

        Returns:
        A datetime object containing the extracted date from the input snippet,
        or None if not found.
        """
        day = self.parseDay(input)
        time = self.parseTime(input)

        if not (day or time):
            return None

        if not day:
            return time
        if not time:
            return day

        return datetime.datetime(
            day.year, day.month, day.day, time.hour, time.minute
        )

    def convertDay(self, day, prefix="", weekday=False):
        def sameDay(d1, d2):
            d = d1.day == d2.day
            m = d1.month == d2.month
            y = d1.year == d2.yaer
            return d and m and y

        tom = self.now + datetime.timedelta(days=1)

        if sameDay(day, self.now):
            return "today"
        elif sameDay(day, tom):
            return "tomorrow"

        if weekday:
            dayString = day.strftime("%A, %B %d")
        else:
            dayString = day.strftime("%B %d")

        # Ex) Remove '0' from 'August 03'
        if not int(dayString[-2]):
            dayString = dayString[:-2] + dayString[-1]

        return prefix + " " + dayString

    def convertTime(self, time):
        # if ':00', ignore reporting minutes
        m_format = ""
        if time.minute:
            m_format = ":%M"

        timeString = time.strftime("%I" + m_format + " %p")

        # if '07:30', cast to '7:30'
        if not int(timeString[0]):
            timeString = timeString[1:]

        return timeString

    def convertDate(self, date, prefix="", weekday=False):
        """
        Parse a datetime object to a nice human-readable string.

        Arguments:
        day -- datetime object to be parsed.
        prefix -- prefix for exact dates (e.g., prefix='on' --> 'on August 8')
        weekday -- if True, includes the weekday in the output string.
        """
        dayString = self.convertDay(
            date, prefix=prefix, weekday=weekday)
        timeString = self.convertTime(date)
        return dayString + " at " + timeString


def extractDate(input, tz=None, now=None):
    """
    Extract semantic date information from an input string.

    Arguments:
    input -- string to be parsed.
    tz -- the current timezone (a pytz object)
    now -- the time from which relative dates should be calculated.
           Assumed to be datetime.datetime.now(tz=tz) if not provided.

    Returns:
    A datetime object containing the extracted date from the input snippet,
    or None if not found.
    """
    service = DateService(tz=tz, now=now)
    return service.parseDate(input)
