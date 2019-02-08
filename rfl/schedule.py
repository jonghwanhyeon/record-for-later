import asyncio
import datetime
import re

from collections import defaultdict, namedtuple

_weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

class TimeRange(namedtuple('TimeRange', ['start', 'end'])):
    @staticmethod
    def parse(timerange_str):
        match = re.match(r'(\d{1,2}):(\d{1,2})-(\d{1,2}):(\d{1,2})', timerange_str)
        start_hour, start_minute, end_hour, end_minute = map(int, match.groups())

        return TimeRange(
            datetime.time(start_hour, start_minute),
            datetime.time(end_hour, end_minute),
        )
TimeRange.day = TimeRange(datetime.time(0, 0), datetime.time(23, 59))


class Schedule:
    def __init__(self, interval):
        self.schedule = defaultdict(list)
        self._prepare_schedule(interval)

    async def next(self):
        if self.interval == 0:
            while self.interval == 0:
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(self.interval)

    @property
    def interval(self):
        now = datetime.datetime.now()
        weekday = _weekdays[now.weekday()]

        for timerange, interval in self.schedule[weekday]:
            if timerange.start <= now.time() <= timerange.end:
                return interval
        else:
            return 0

    def _prepare_schedule(self, interval):
        for key, values in interval.items():
            if key in _weekdays:
                if isinstance(values, int):
                    self.schedule[key] = [(TimeRange.day, values)]
                else:
                    self.schedule[key] = [
                        (TimeRange.parse(timerange_str), value)
                        for timerange_str, value in values.items()
                    ]

        for key, value in interval.items():
            if key not in _weekdays:
                for weekday in _weekdays:
                    self.schedule[weekday].append((TimeRange.parse(key), value))
