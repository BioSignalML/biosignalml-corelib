######################################################
#
#  BioSignalML Management in Python
#
#  Copyright (c) 2010-2011  David Brooks
#
#  $ID$
#
######################################################


__docformat__ = 'restructuredtext'

import biosignalml.model as model
from biosignalml.bsml import BSML
from biosignalml.model.data import TimeSeries
from biosignalml.utils import file_uri


def not_implemented(instance, method):
#=====================================
  raise NotImplementedError('%s.%s()' % (instance.__class__.__name__, method))


class BSMLRecording(model.Recording):
#====================================

  """A generic signal recording.

  """

  def __init__(self, fname=None, uri=None, mode='r', metadata={}):
  #---------------------------------------------------------------
    if fname:
      if 'source' not in metadata: metadata['source'] = file_uri(fname)
      if not uri: uri = metadata['source']
    elif 'source' not in metadata:
      metadata['source'] = uri
    if 'format' not in metadata: metadata['format'] = BSML.RAW
    super(BSMLRecording, self).__init__(uri, metadata=metadata)
    if metadata.get('digest'): self.metadata['digest'] = metadata['digest']

  @classmethod
  def open(cls, fname, uri=None, mode='r', **kwds):
  #------------------------------------------------
    return cls(fname, uri=uri, mode=mode, **kwds)

  @classmethod
  def create(cls, fname, uri=None, **kwds):
  #----------------------------------------
    return cls.open(fname, uri=uri, mode='w', **kwds)

  def close(self):
  #---------------
    pass

  def rdf_metadata(self, format='turtle', prefixes={}):
  #----------------------------------------------------
    not_implemented(self, 'save_metadata')


class BSMLSignal(model.Signal):
#==============================

  def __init__(self, uri, metadata={}):
  #------------------------------------
    super(BSMLSignal, self).__init__(uri, metadata=metadata)

    """
    :return: A :class:TimeSeries containing signal data covering the interval.
    """
  def read(self, interval=None):
  #-----------------------------
    not_implemented(self, 'read')

  def append(self, timeseries):
  #----------------------------
    not_implemented(self, 'append')

  def data(self, n):
  #----------------
    not_implemented(self, 'data')

  def time(self, n):
  #----------------
    not_implemented(self, 'time')


from raw  import RAWRecording
from edf  import EDFRecording
from sdf  import SDFRecording
from wfdb import WFDBRecording
from hdf5 import HDF5Recording
