#!/usr/bin/python3 -i
import pycpsw
import numpy
import threading

import ModelParmScaled as ModelParm

from PyQt4 import QtCore

# Interface to pendulum module in udpsrv; use CPSW to access

class Model(QtCore.QThread):

  _posChanged = QtCore.pyqtSignal(object)

  def __init__(self, pollMs, pendLen, parent = None):
    super(Model, self).__init__(parent)
    self.root      = pycpsw.Path.loadYamlFile("./yaml/tutorial.yaml")
    self.modl      = self.root.findByName("mmio/pendsim")
    self.pollMs    = pollMs
    self.pendLen   = pendLen
    self.parms     = dict()
    self.stream    = None
    # Discover the parameters/registers present in this device
    # and add to the 'parms' dictionary
    for child in self.modl.tail().isHub().getChildren():
      nam = child.getName()
      self.parms[nam] = ModelParm.ModelParm( self.modl, nam )
    # Pendulum length (in proportion to the horizontal track length)
    # comes from the GUI - set it accordingly in the physical model.
    self.setParm('length', self.pendLen )
    self.setState( 0, numpy.pi/2.+.1 )
    # Start our thread
    self.streamErr = None
    try:
      import StreamHandler
      self.stream = StreamHandler.StreamHandler( self.root )
      # Found a the streaming interface; use it
    except (AttributeError, ImportError, NameError, pycpsw.CPSWError) as err:
      # No stream; fall back to polling but store cause of error
      try:
        modnam = getattr(err, "__module__")
        modnam += "."
      except AttributeError:
        modnam = ""
      self.streamErr = ( "Stream could not be opened due to "
                        + modnam
                        + type(err).__name__
                        + ": "
                        + err.__str__() )
    self.isUp = True
    self.start()

  ## "public" access -> set a value
  def setParm(self, nam, val):
    self.parms[nam].setVal( val )

  ## "public" access -> get a value
  def getParm(self, nam):
    return self.parms[nam].getVal()

  ## "public" access -> get description (for GUI)
  def getDescription(self, nam):
    return self.parms[nam].getDescription()

  ## "public" access -> set/reinit pendulum position (and velocity)
  def setState(self, phi, pos):
    self.setParm("force",   0)
    self.setParm("pos"  , pos)
    # NOTE: write 'phi' LAST since that causes the simulator to
    #       reinitialize the state (using latched 'pos').
    self.setParm("phi"  , phi)

  ## "public" access -> shut down the model thread
  def shutDown(self):
    self.isUp = False
    self.wait()
    if self.stream:
      del self.stream

  ## "public" access -> stream error status (None if stream is OK)
  def getStreamErrorState(self):
    return self.streamErr;

  def run(self):
    if self.stream:
      # use stream
      while self.isUp:
        measuredState = self.stream.read( 200000 )
        if measuredState != None:
          self._posChanged.emit( measuredState )
    else:
      # use polling
      # cache handles to the relevant parameters
      timeRB = self.parms['timeRB']
      phiRB  = self.parms['phiRB']
      posRB  = self.parms['posRB']
      while self.isUp:
        # sleep for a while
        QtCore.QThread.msleep( self.pollMs )
        # retrieve angle (normalized to 2*PI) + position
        # Note: read phi FIRST since that causes 'posRB' and 'timeRB'
        #       to be latched!
        phi = phiRB.getVal()
        pos = posRB.getVal()
        tim = timeRB.getVal()
        #print("phi {:8.5f} pos {:8.5f}".format(phi, pos))

        # Post to the GUI
        self._posChanged.emit( (tim, phi, pos) )
