import sys
import csv, codecs, cStringIO

################################################################################
# UNICODE I/O
################################################################################

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

################################################################################
# END UNICODE I/O
################################################################################

mHeader = ['university','name', 'website', 'rank', 'field', 'bachelors', 'masters', 'phd', 'postdoc', 'othersrcs']
professors = {}
with open('master.csv', 'rb') as csvfile:
  reader = UnicodeReader(csvfile)
  for row in reader:
    # get all data except for the 'number' field
    r = row
    r = [s.rstrip() for s in r]
    r = [s.lstrip() for s in r]

    r[1] = r[1].title()
    name = r[1]

    # Sanitation check
    if r[3].find('Lecturer') != -1 or r[3].find('Teaching') != -1 or r[3].find('Research') != -1 or r[3].find('Emeritus') != -1 or r[3].find('Scientist') != -1:
    #if (r[3].encode()).contains('Lecturer'):
      continue

    if name not in professors.keys():
      professors[name] = r
    else:
      for elem, i in zip(r, range(0,len(r))):
        index = r[i]
        if professors[name][i] == elem or elem == '':
          continue
        else:
          if professors[name][i] == '':
            newInfo = elem
          else:
            newInfo = professors[name][i] + ';' + elem
          professors[name][i] = newInfo


with open('master_clean.csv', 'wb') as csvfile:
  w = UnicodeWriter(csvfile)
  w.writerow(mHeader)
  for name, info in professors.iteritems():
    w.writerow(info)
