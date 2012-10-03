from biosignalml.rdf import Resource, NS

from ontology import UNITS


_direct = {
  'bmp':    'BeatsPerMinute',
  'cc':     'CubicCentimetre',
  'pm':     'PerMinute',
  '1/min':  'PerMinute',
  'Lpm':    'LitrePerMinute',
  'lpm':    'LitrePerMinute',
  'mv':     'Millivolt',
  'uV-mrs': 'Microvolt',
  'annotation': 'AnnotationData',
  }

_units = {
  '%':     'Percent',
  'A':     'ampere',
  'deg':   'DegreeOfArc',
  'degC':  'DegreeCelsius',
  'mHg':   'metresOfMercury',
  'mH2O':  'metresOfWater',
  'g':     'gram',
  'J':     'joule',
  'K':     'Kelvin',
  'l':     'litre',
  'L':     'litre',
  'm':     'metre',
  'min':   'minute',
  's':     'second',
  'V':     'volt',
  'W':     'watt',
  'bar':   'bar',
  'BPM':   'BeatsPerMinute',
  'bpm':   'BeatsPerMinute',
  }

_powers_prefix = {
  '2': 'Square',
  '3': 'Cubic',
  }

_powers_suffix = {
  '2': 'Squared',
  '3': 'Cubed',
  }


_prefixes = { 'Y': 'Yotta', 'Z': 'Zetta', 'E': 'Exa',
              'P': 'Peta',  'T': 'Tera',  'G': 'Giga',
              'M': 'Mega',  'K': 'Kilo',  'H': 'Hecto',
              'D': 'Deca',
              'd': 'Deci',  'c': 'Centi', 'm': 'Milli',
              'u': 'Micro', 'n': 'Nano',  'p': 'Pico',
              'f': 'Femto', 'a': 'Atto',  'z': 'Zepto',
              'y': 'Yocto',
              u'\u00b5': 'Micro',
            }


def _upperfirst(s):
#------------------
  return s[0].upper() + s[1:]

def _name(u):
#------------
  try:             return _upperfirst(_units[u])
  except KeyError: return _prefixes[u[0]] + _units[u[1:]]

def _power(u):
#-------------
  try:
    p = u.index('^')
    name = _name(u[:p])
    if name.lower().endswith('second'):
      return name + _powers_suffix[u[p+1:]]
    else:
      return _powers_prefix[u[p+1:]] + name
  except ValueError:
    return _name(u)

def _mult(u):
#------------
  return ''.join([_power(v) for v in u.split('*')])


def to_UNITS(units):
#==================
  if units:
    try:
      uome = _direct[units]
    except KeyError:
      try: uome = 'Per'.join([_mult(u) for u in units.split('/')])
      except KeyError: return None
    return getattr(UNITS, uome, None)
  return None

if __name__ == '__main__':
#=========================

  import sys

  def convert(u):
    try:
      o = to_UNITS(u)
      if o: print '%s --> %s' % (u, o)
      else: print 'Cannot convert: %s' % u
    except Exception, msg:
      print 'Error converting: %s (%s)' % (u, msg)

  for l in sys.stdin:
    for w in l.split():
      convert(w)

  '''
  test('Km')
  test('Kg*m/s^2/W*m')
  test('mm^2')
  test('Mm^3')
  test('ms')
  test('Mm/s')
  test('mg')
  test('deg')
  test('%')
  test('uV')
  test('mV')
  test('bar')
  test('mbar')
  test('degC')
  test('mmHg')
  test('cmH2O')
  test('bpm')
  test('')
  test(u'\u00b5V')
  '''
