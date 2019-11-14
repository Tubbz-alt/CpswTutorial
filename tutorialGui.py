#!/usr/bin/python3

import sys
import signal
import numpy
from   PyQt5 import Qt, QtGui, QtCore, QtWidgets

# Import the pendulum model - this is a class which is supposed to 
# provide the following methods
#
#         __init__      ( self, pollMilliSecs, pendLength )  -> initialize; pendLength normalized to 1/2 track length
#  float  getParm       ( self, name_string               )  -> read parameter 'name' and return float value
#  string getDescription( self, name_string               )  -> read description for parameter 'name'
#         setParm       ( self, name_string, float_value  )  -> set parameter 'name' to float 'value'
#         setState      ( self, phi, horiz_pos            )  -> initialize state to 'phi' / 'position'
#         shutDown      ( self                            )  -> shutdown all threads
#
# The model is supposed to emit a signal '_posChanged' when the pendulum position has
# changed (either a result of polling or the underlying simulator pushing a new value)
#
# The following parameters are expected to exist:
#
#  "vFriction"
#  "gOverL"
#  "mOverM"
#  "iniVelo"
#  "length"
#
import UdpsrvInterface as Pendmod
#import pendmod as Pendmod

# Class which connects a parameter from the model to a QLineEdit widget
class ParmField(QtWidgets.QLineEdit):

  def __init__(self, nam, modl, parent=None):
    super(ParmField,self).__init__(parent)
    self.nam_  = nam
    self.modl_ = modl
    self.setValidator( QtGui.QDoubleValidator() )
    self.setText( '{:f}'.format( modl.getParm(nam) ) )
    # returnPressed is only emitted if the string passes validation
    self.returnPressed.connect( self.updateVal )
    #Qt4: QtCore.QObject.connect( self, QtCore.SIGNAL("returnPressed()"),   self.updateVal )
    # editingFinished is emitted after returnPressed or lost focus (with valid string)
    # if we lose focus w/o return being hit then we restore the original string
    self.editingFinished.connect( self.restoreTxt )
    #Qt4: QtCore.QObject.connect( self, QtCore.SIGNAL("editingFinished()"), self.restoreTxt  )
 
  # the user entered a new value into the GUI; propagate to the model
  def updateVal(self):
    self.modl_.setParm(self.nam_, float( self.text() ))

  # user edit was aborted; restore the GUI text to the (unmodified) value from the model
  def restoreTxt(self):
    self.setText( '{:f}'.format( self.modl_.getParm( self.nam_ ) ) )
   

# Pendulum GUI. Pass a reference to the model.
class Pend(QtWidgets.QFrame):

  def __init__(self, modl, parent=None, flags=QtCore.Qt.WindowFlags()):
    super(Pend,self).__init__( parent, flags )
    tracklim = 200 # track extends 2*tracklim
    penw = 3
    penl = modl.getParm("length")*tracklim
    # print("penl is {}".format(modl.getParm("length")))
    self.tracklim   = tracklim
    self.tracklen   = 2*tracklim
    self.penl       = penl
    self.cirw       = 20
    self.carw       = 20
    self.carh       = 10
    self.trackstart = self.cirw   + penl
    self.winw       = 2*self.trackstart + self.tracklen
    self.winh       = 2*penl + penl
    self.arm        = numpy.ndarray( (5,2) );
    self.phi_       = 0
    self.dx_        = 0
    self.arm[0]     = [    0, -penw/2 ]
    self.arm[1]     = [ penl, -penw/2 ]
    self.arm[2]     = [ penl,       0 ]
    self.arm[3]     = [ penl, +penw/2 ]
    self.arm[4]     = [    0, +penw/2 ]
    self.origin     = [self.winw/2, self.winh/2]
    self.modl_      = modl
    self.ltim_      = 0.
    self.lphi_      = 0.
    self.ldx_       = 0.
    self.kCorr_     = numpy.array([-5.24,-3.2,.3125,1.269])
    self.setLineWidth(2)
    self.setFrameStyle( QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken )
    self.setMinimumSize(self.winw, self.winh)
    modl._posChanged.connect( self.updatePos )

  # Transform points 'pts': rotate by 'fi' and shift by 'dx'
  def xfrm(self, fi, dx, pts):
    rot = numpy.ndarray((2,2))
    rot[0,0] = numpy.cos(fi)
    rot[1,0] = -numpy.sin(fi)
    rot[0,1] = +rot[1,0] # drawing 'y' axis is - 'physical' y axis
    rot[1,1] = -rot[0,0] #
    # y-axis in translation (dx) would also have to be inverted
    return numpy.dot(pts,rot) + self.origin + [dx, 0]

  # state-space controller
  def runController(self, pos):
    tim    = pos[0]
    phi    = pos[1]
    dx     = pos[2]
    delta  = (phi - numpy.pi/2.)
    # the position - normalized to half of the horiz. track length
    dt     = tim - self.ltim_
    if 0. == dt:
      return
    phidot = (phi-self.lphi_)/dt
    dxdot  = (dx -self.ldx_)/dt
  
    self.ltim_ = tim
    self.lphi_ = phi
    self.ldx_  = dx

    state = numpy.array([delta, phidot, dx, dxdot])
  
    # if linear approximation becomes too bad disable
    # the controller...
    if abs(delta) < numpy.pi/4.:
  	  self.modl_.setParm("force", numpy.dot(self.kCorr_, state))
    else:
  	  self.modl_.setParm("force", 0)
  

  # Handler for signal '_posChanged' which is emitted by model.
  # update our phi_/dx_ members with the new values sent by the
  # model and cause a 'paintEvent'
  def updatePos(self, pos):
    self.runController(pos)
    self.phi_ = pos[1]
    self.dx_  = pos[2]*self.tracklim
    self.update()

  # calculate the pendulum arm position
  def armPoints(self, fi, dx):
    l = QtGui.QPolygon()
    for i in self.xfrm(fi, dx, self.arm):
      l.append(QtCore.QPoint(i[0],i[1])) 
    return l

  def paintEvent(self, e):
    super(Pend,self).paintEvent(e)
    self.doDraw(self.phi_, self.dx_)

  # reinitialize the pendulum position based on user input
  def mousePressEvent(self, ev):
    x = float(ev.x() - self.origin[0])
    y = float(self.origin[1] - ev.y())
    if abs(y) >= self.penl:
      dx  = x
      phi = numpy.sign(y)*numpy.pi/2
    else:
      if x > 0:
        phi = numpy.arcsin(y/self.penl)
        dx  = x - self.penl*numpy.cos(phi)
      else:
        phi = numpy.pi - numpy.arcsin(y/self.penl)
        dx  = x - self.penl*numpy.cos(phi)
    dx /= self.tracklim
    self.lphi_ = phi
    self.ldx_  = dx
    self.ltim_ = 0
    self.modl_.setState(phi, dx)

  def doDraw(self, phi, dx):
    qp = QtGui.QPainter()
    qp.begin(self)
    self.draw(qp, phi, dx)
    qp.end()

  def draw(self, qp, phi, dx):
    color = QtGui.QColor(0,0,0)
    color.setNamedColor('#d4d4d4')
    qp.setPen(color)

    qp.setBrush( QtGui.QColor(50,50,50) )
    qp.drawRect( self.trackstart, self.origin[1], self.tracklen, 2 )

    qp.setBrush( QtGui.QColor(0,0,0) )
    poly = self.armPoints( phi, dx )
    qp.drawConvexPolygon( poly )
    cent = poly.point(2)
    qp.drawEllipse( cent.x() - self.cirw/2,
                    cent.y() - self.cirw/2,
                    self.cirw,
                    self.cirw )
    qp.drawRect   ( self.origin[0] + dx - self.carw/2,
                    self.origin[1] - self.carh/2,
                    self.carw,
                    self.carh )

def addField(form, fieldName, modl):
  form.addRow( modl.getDescription(fieldName), ParmField(fieldName, modl) )
  
def main():
  signal.signal( signal.SIGINT, signal.SIG_DFL )
  app  = QtWidgets.QApplication(sys.argv)
  vbox = QtWidgets.QVBoxLayout()
  modl = Pendmod.Model(50, .4)
  form = QtWidgets.QFormLayout()
  addField(form, "vFriction", modl)
  addField(form, "gOverL"   , modl)
  addField(form, "mOverM"   , modl)
  addField(form, "iniVelo"  , modl)
  formw = QtWidgets.QWidget()
  formw.setLayout( form )
  vbox.addWidget( formw )
  vbox.addWidget( QtWidgets.QLabel("Click in pendulum area to re-initialize position"),
                  alignment=QtCore.Qt.AlignHCenter )
  vbox.addWidget( Pend(modl), alignment=QtCore.Qt.AlignHCenter )
  strmErr = modl.getStreamErrorState()
  if strmErr:
    vbox.addWidget( QtWidgets.QLabel("Mode: Polled; " + strmErr) )
  else:
    vbox.addWidget( QtWidgets.QLabel("Mode: Streaming") )
  top = QtWidgets.QWidget()
  top.setLayout( vbox )
  top.setWindowTitle("Pendulum on Cart")
  top.show()
  rval = app.exec_()
  modl.shutDown()
  sys.exit(rval)

if __name__ == '__main__':
  main()
