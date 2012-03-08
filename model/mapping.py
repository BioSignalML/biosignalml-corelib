######################################################
#
#  BioSignalML Management in Python
#
#  Copyright (c) 2010-2011  David Brooks
#
#  $ID: bbd3c04 on Wed Jun 8 16:47:09 2011 +1200 by Dave Brooks $
#
######################################################


import os
import logging
import importlib  # Python 2.7 onwards...
from collections import namedtuple
from datetime import datetime, timedelta
from isodate  import isoduration

from biosignalml.ontology import BSML
from biosignalml.rdf import Node, Uri, Statement
from biosignalml.rdf import RDFS, DCTERMS, XSD, TL, EVT

from biosignalml.timeline import TimeLine


_datatypes = { XSD.float:              float,
               XSD.double:             float,
               XSD.integer:            long,
               XSD.long:               long,
               XSD.int:                int,
               XSD.short:              int,
               XSD.byte:               int,
               XSD.nonPostiveInteger:  long,
               XSD.nonNegativeInteger: long,
               XSD.positiveInteger:    long,
               XSD.negativeInteger:    long,
               XSD.unsignedLong:       long,
               XSD.unsignedInt:        long,
               XSD.unsignedShort:      int,
               XSD.unsignedByte:       int,
             }


def get_uri(v):
#==============
  '''
  Get the `uri` attribute if it exists, otherwise the object as a string.
  '''
  return v.uri if getattr(v, 'uri', None) else str(v)

def datetime_to_isoformat(dt):
#=============================
  return dt.isoformat()

def isoformat_to_datetime(v):
#============================
  try:
    return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
  except ValueError:
    return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
  except Exception, msg:
    logging.error("Cannot convert datetime '%s': %s", v, msg)
    return None  

def seconds_to_isoduration(secs):
#================================
  return isoduration.duration_isoformat(
    timedelta(seconds=int(secs), microseconds=int(1000000*(secs - int(secs)) ))
    )

def isoduration_to_seconds(d):
#=============================
  try:
    td = isoduration.parse_duration(d)
    return td.days*86400 + td.seconds + td.microseconds/1000000.0
  except:
    pass
  return 0


class AttributeMap(object):
#==========================

  def __init__(self, attribute, property, metaclass=None, datatype=None, to_rdf=None, from_rdf=None):
  #--------------------------------------------------------------------------------------------------
    self.attribute = attribute
    self.property = property
    self.metaclass = metaclass
    self.datatype = datatype
    self.to_rdf = to_rdf
    self.from_rdf = from_rdf


ReverseEntry = namedtuple('ReverseEntry', 'attribute, datatype, from_rdf')


BSML_MAP = [
# Generic metadata:
  AttributeMap('label',           RDFS.label),
  AttributeMap('comment',         RDFS.comment),
  AttributeMap('description',     DCTERMS.description),
  AttributeMap('dateSubmitted" ', DCTERMS.dateSubmitted,
    None, XSD.dateTime, datetime_to_isoformat, isoformat_to_datetime),

# Recording specific metadata:
  AttributeMap('format',        DCTERMS.format,  BSML.Recording),
  AttributeMap('source',        DCTERMS.source,  BSML.Recording),
  AttributeMap('investigation', DCTERMS.subject, BSML.Recording),
  AttributeMap('starttime',     DCTERMS.created, BSML.Recording, XSD.dateTime, datetime_to_isoformat,  isoformat_to_datetime),
  AttributeMap('duration',      DCTERMS.extent,  BSML.Recording, XSD.duration, seconds_to_isoduration, isoduration_to_seconds),
##  AttributeMap('digest',        BSML.digest,     BSML.Recording),

# Timing specific metadata:
  AttributeMap('timeline', TL.timeline, to_rdf=get_uri, from_rdf=TimeLine),
  AttributeMap('at',       TL.atDuration,       TL.RelativeInstant,  XSD.duration, seconds_to_isoduration, isoduration_to_seconds),
  AttributeMap('start',    TL.beginsAtDuration, TL.RelativeInterval, XSD.duration, seconds_to_isoduration, isoduration_to_seconds),
  AttributeMap('duration', TL.durationXSD,      TL.RelativeInterval, XSD.duration, seconds_to_isoduration, isoduration_to_seconds),

# Event specific metadata:
  AttributeMap('time',   TL.time,    EVT.Event),
  AttributeMap('factor', EVT.factor, EVT.Event),

# Signal specific metadata:
  AttributeMap('recording',    BSML.recording,    BSML.Signal, to_rdf=get_uri),
  AttributeMap('units',        BSML.units,        BSML.Signal, to_rdf=get_uri),
##  AttributeMap('transducer',   BSML.transducer,   BSML.Signal),
  AttributeMap('filter',       BSML.preFilter,    BSML.Signal),
  AttributeMap('rate',         BSML.rate,         BSML.Signal, XSD.double),
##  AttributeMap('clock',        BSML.sampleClock,  BSML.Signal, to_rdf=get_uri),
  AttributeMap('minFrequency', BSML.minFrequency, BSML.Signal, XSD.double),
  AttributeMap('maxFrequency', BSML.maxFrequency, BSML.Signal, XSD.double),
  AttributeMap('minValue',     BSML.minValue,     BSML.Signal, XSD.double),
  AttributeMap('maxValue',     BSML.maxValue,     BSML.Signal, XSD.double),
  AttributeMap('index',        BSML.index,        BSML.Signal, XSD.integer),
  ]



def _uri_protocol(u):
#====================
  return u.startswith('file:') or u.startswith('http:')


def _load_mapping(maplist):
#==========================
  mapping = { }
  for m in maplist:
    key = m.attribute + (str(m.metaclass) if m.metaclass else '')
    mapping[key] = m
  return mapping

# Generic (BSML) mapping; format specific overrides.
_bsml_maps    = None
_bsml_mapping = None


def bsml_mapping():
#==================
  return _bsml_mapping


class Mapping(object):
#=====================

  def __init__(self, maplist=None):
  #--------------------------------
    self._mapping = _bsml_maps.copy()
    if maplist:
      if isinstance(maplist, tuple):
        for ml in maplist: self._mapping.update(_load_mapping(ml))
      else:
        self._mapping.update(_load_mapping(maplist))
    self._reverse = { (str(m.property) + (str(m.metaclass) if m.metaclass else '')):
      ReverseEntry(m.attribute, m.datatype, m.from_rdf) for m in self._mapping.itervalues() }

  @staticmethod
  def _makenode(v, dtype, mapfn):
  #------------------------------
    if   isinstance(v, Node) or isinstance(v, Uri):
      return Node(v)
    elif getattr(v, 'uri', None):
      if isinstance(v.uri, Node): return Node(v)
      else:                       return Node(Uri(v.uri))
    else:
      if mapfn:
        try: v = mapfn(v)
        except Exception, msg:
          logging.error("Exception mapping literal with '%s': %s", str(mapfn), msg)
      v = unicode(v)
      if _uri_protocol(v):
        return Node(Uri(v))
      else:
        result = { 'literal': v }
        if dtype: result['datatype'] = dtype.uri
        return Node(**result)

#  def statement(self, s, attr, v):
#  #-------------------------------
#    m = self._mapping[attr]
#    return (s, m[0], self._makenode(v, m[1], m[2]))

  def statement_stream(self, resource):
  #------------------------------------
    """
    Generate :class:`Statement`\s from a resource's attributes and
    elements in its `metadata` dictionary.

    :param resource: An object with a `metaclass` attributes on
      some of its classes.

    All attributes defined in the mapping table are tested to see if they are defined for
    the resource, and if so, their value in the resource is translated to an object node
    in a RDF statement.
    """
    if getattr(resource, 'uri', None):
      subject = resource.uri
      metaclasses = [ cls.metaclass for cls in resource.__class__.__mro__
                      if cls.__dict__.get('metaclass') ]
      metadict = getattr(resource, 'metadata', { })
      for m in self._mapping.itervalues():
        if m.metaclass is None or m.metaclass in metaclasses:  ## Or do we need str() before lookup ??
          if getattr(resource, m.attribute, None) not in [None, '']:
            yield Statement(subject, m.property, self._makenode(getattr(resource, m.attribute), m.datatype, m.to_rdf))
          if metadict.get(m.attribute, None) not in [None, '']:
            yield Statement(subject, m.property, self._makenode(metadict.get(m.attribute), m.datatype, m.to_rdf))


  @staticmethod
  def _makevalue(node, dtype, from_rdf):
  #-----------------------------------
    if node is None: return None
    elif node.is_resource(): v = node.uri
    elif node.is_blank(): v = node.blank
    else:
      v = node.literal[0]
      if dtype: v = _datatypes.get(dtype, str)(v) 
    return from_rdf(v) if from_rdf else v

  def metadata(self, statement, metaclass):
  #----------------------------------------
    """
    Given a RDF statement and a metaclass, lookup the statement's predicate
    in the reverse mapping table use its properties to translate the value of the
    statement's object.
    """
    m = self._reverse.get(str(statement.predicate.uri) + str(metaclass), None)
    if m is None: m = self._reverse.get(str(statement.predicate.uri), ReverseEntry(None, None, None))
    return (statement.subject.uri, m.attribute, self._makevalue(statement.object, m.datatype, m.from_rdf))

  def get_value_from_graph(self, resource, attr, graph):
  #-----------------------------------------------------
    """
    Find the property corresponding to a resource's attribute and if a statement
    about the resource using the property is in the graph, translate and return
    its object's value.
    """
    m = self._mapping.get(attr + str(resource.metaclass), None)
    if m is None: m = self._mapping.get(attr, None)
    if m:
      return self._makevalue(graph.get_object(resource.uri, m.property), m.datatype, m.from_rdf)


def initialise():
#================
  global _bsml_maps, _bsml_mapping
  if _bsml_maps is None:
    _bsml_maps = _load_mapping(BSML_MAP)
    _bsml_mapping = Mapping()   # Standard model


initialise()


#def shutdown():
##==============
#  global _bsml_maps, _bsml_mapping
#  if _bsml_maps:
#    del _bsml_maps
#    _bsml_maps = None
#  if _bsml_mapping:
#    del _bsml_mapping
#    _bsml_mapping = None


if __name__ == '__main__':
#=========================

  from biosignalml.rdf import Graph

  class C(object):
    def __init__(self):
      self.uri = 'uri'
      self.version = 1
      self.metadata = { 'description': 'Hello...' }

  md = Graph()
  md.add_metadata(C(), Mapping())
  print md
