#!/usr/bin/python3 -i

import pycpsw
import re

class myvisitor(pycpsw.PathVisitor):
  def __init__(self, patt = None):
    pycpsw.PathVisitor.__init__(self)
    self.level=0
    if patt != None:
      self.re_prog = re.compile(patt)
      self.result  = []
    else:
      self.re_prog = None

  def visitPre(self, path):
    self.level = self.level + 1
    if self.re_prog == None:
      tl = path.tail()
      fr = path.getTailFrom()
      to = path.getTailTo()
      st = '{:<{}s}{}[{}'.format('',self.level,tl.getName(),fr)
      if fr == to:
        st+="]"
      else:
        st+="-{}]".format(to)
      print(st)
    elif self.re_prog.search( path.toString() ) != None:
      self.result.append(path.toString())
    return True

  def visitPost(self, path):
    self.level = self.level - 1
    pass

def pgrep(path, re_pattern):
  """Recurse through CPSW hierarchy looking for RE pattern matches

     Starts recursion at 'path' and returns a list of RE matches.
  """
  v = myvisitor(re_pattern)
  path.explore(v)
  if re_pattern != None:
    return v.result
  else:
    return None
