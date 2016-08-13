# -*- coding: utf-8 -*-
import codecs
import collections
import csv
import datetime
import itertools


class InvalidTimeEntryException(ValueError):
    pass


class UTF8Recoder:
    '''
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    '''
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeOrderedDictReader:
    '''
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.

    Rows are returned in an collections.OrderedDict, which means that column
    order is preserved.
    '''

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.header = self.reader.next()

    def next(self):
        return collections.OrderedDict(
            itertools.izip(
                self.header, [s.decode('utf-8') for s in self.reader.next()]
            )
        )

    def __iter__(self):
        return self


def parse_op_timesheet_csv(fobj, member_col=0, date_fmt='%Y-%m-%d',
                           delimiter=',', encoding='utf-8'):
    reader = UnicodeOrderedDictReader(
        fobj, encoding=encoding, delimiter=delimiter)
    entries = collections.OrderedDict()

    for idx, row in enumerate(reader, start=1):
        member = row.pop(row.keys()[member_col])
        entries[member] = collections.OrderedDict()
        for date_str, cell in row.iteritems():
            try:
                dt = datetime.datetime.strptime(date_str, date_fmt).date()
            except ValueError:
                pass
            else:
                if cell:
                    try:
                        hours = float(cell)
                    except ValueError:
                        raise InvalidTimeEntryException(
                            'Invalid time entry value: "%s" on line: %d' %
                            (cell, idx)
                        )
                else:
                    hours = 0.0

                entries[member][dt] = hours

    return entries
