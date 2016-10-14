#!/usr/bin/python3 -i
import pycpsw
import numpy

# A 'ModelParm' object represents a value/register on the target
class ModelParm(object):

  # call with a Path prefix and a CPSW entry name
  def __init__(self, pref, nam):
    self.nam_ = nam
    # create a DoubleVal
    if   nam == "vFriction":
      self.scl_ = 2.**(-32)
    elif nam == "gOverL" or nam == "mOverM" or nam == "length":
      self.scl_ = 2.**(-16)
    elif nam == "pos" or nam == "posRB":
      self.scl_ = 2.**(-31)
    elif nam == "phi" or nam == "phiRB":
      self.scl_ = numpy.pi*2.**(-30)
    elif nam == "iniVelo" or nam == "force":
      self.scl_ = 2.**(-15)
    elif nam == "timeRB":
      self.scl_ = 2.**(-8)
    else:
      # if there is any parameter for which we don't have a scale
      # then an error will result when someone tries to use it...
      self.scl_ = None
    try:
      self.val_ = pycpsw.DoubleVal.create( pref.findByName(nam) )
    except pycpsw.InterfaceNotImplementedError:
      # fall back to read-only
      self.val_ = pycpsw.DoubleVal_RO.create( pref.findByName(nam) )

  # convert the scaled representation to floating-point
  def getVal(self):
    return self.val_.getVal()*self.scl_

  # convert floating-point to scaled representation
  def setVal(self, val):
    self.val_.setVal(val/self.scl_)

  def getDescription(self):
    return self.val_.getDescription()

