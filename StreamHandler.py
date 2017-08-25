import pycpsw
import sys
import numpy
# python3 could use native arrays...
#import array

class StreamHandler(object):

  def __init__(self, root):
    self.strm_ = pycpsw.Stream.create( root.findByName("pendsimStream" ) )
    # simulator streams little-endian data. If we happen to execute
    # on a big-endian machine then we need to byte-swap...
    self.bswp_ = (sys.byteorder != "little")
    # reserve buffer
    # python3 using array
    # self.buff_ = array.array('q', (0 for i in range(3)))
    self.buff_ = numpy.ndarray((3),dtype=numpy.int64)

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

  def __enter__(self):
    return self.strm_.__enter__()

  def __exit__(self, exc_type, exc_val, traceback):
    return self.strm_.__exit__(exc_type, exc_val, traceback)
