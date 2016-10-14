import pycpsw
import sys
import numpy
import array

class StreamHandler(object):

  def __init__(self, root):
    self.strm_ = pycpsw.Stream.create( root.findByName("pendsimStream" ) )
    # simulator streams little-endian data. If we happen to execute
    # on a big-endian machine then we need to byte-swap...
    self.bswp_ = (sys.byteorder != "little")
    # reserve buffer
    self.buff_ = array.array('q', (0 for i in range(3)))

  def read(self, timeoutMicroSecs):
    if self.strm_.read(self.buff_, timeoutMicroSecs) > 0:
      if self.bswp_:
        self.buff_.byteswap()
      # The stream data are three 64-bit integers
      # normalized to 2^32.

      # (simulation) 'time'
      tim = float(self.buff_[0])/(2.**32)
      # the angle of the pendulum with the horizontal track - normalized to 2 * PI
      phi = float(self.buff_[1])/(2.**32)
      pos = float(self.buff_[2])/(2.**32)
      return (tim, phi, pos)
    else:
      return None
