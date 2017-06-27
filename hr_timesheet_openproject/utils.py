# -*- coding: utf-8 -*-
import csv
import datetime

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
TIME_ENTRY_KEYS = (
    'date',
    'user',
    'activity',
    'project',
    'wp',
    'type',
    'subject',
    'hours',
    'comment',
)


class InvalidTimeEntryException(ValueError):
    pass


def unicode_csv_reader(fobj, encoding='utf-8', dialect=csv.excel,
                       **kwargs):
    csv_reader = csv.reader(fobj, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, encoding) for cell in row]


class MinMax(object):
    """Helper object for keeping track of min/max values."""

    def __init__(self, min_val=None, max_val=None):
        self.min, self.max = min_val, max_val

    def add(self, value):
        if self.min is None or value < self.min:
            self.min = value
        if self.max is None or value > self.max:
            self.max = value


def transform_time_entry(entry, date_fmt=DEFAULT_DATE_FORMAT):
    entry.update({
        'date': datetime.datetime.strptime(entry['date'], date_fmt).date(),
        'hours': float(entry.get('hours') or 0),
        'wp': int(entry.get('wp') or 0),
    })
    return entry


def parse_op_timesheet_csv(fobj, skip_first=True, date_fmt=DEFAULT_DATE_FORMAT,
                           delimiter=',', encoding='utf-8'):
    reader = unicode_csv_reader(
        fobj, encoding=encoding, delimiter=delimiter)
    entries, first = [], True
    for idx, row in enumerate(reader, start=1):
        if skip_first and first:
            first = False
            continue
        try:
            entries.append(transform_time_entry(
                dict(zip(TIME_ENTRY_KEYS, row[:len(TIME_ENTRY_KEYS)])),
                date_fmt=date_fmt,
            ))
        except (ValueError, TypeError):
            raise InvalidTimeEntryException(
                'Invalid time entry on line: %d' % idx)
    return entries
