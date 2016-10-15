#!/usr/bin/python3 -i
import pycpsw
import numpy

# A 'ModelParm' object represents a value/register on the target
class ModelParm(object):

  # call with a Path prefix and a CPSW entry name
  def __init__(self, pref, nam):
    self.nam_ = nam
    try:
      self.val_ = pycpsw.DoubleVal.create( pref.findByName(nam) )
    except pycpsw.InterfaceNotImplementedError:
      # fall back to read-only
      self.val_ = pycpsw.DoubleVal_RO.create( pref.findByName(nam) )

  # convert the scaled representation to floating-point
  # (conversion already done by the Int2Dbl c++ object)
  def getVal(self):
    return self.val_.getVal()

  # convert floating-point to scaled representation
  # (conversion already done by the Int2Dbl c++ object)
  def setVal(self, val):
    self.val_.setVal(val)

  def getDescription(self):
    return self.val_.getDescription()

