# //@C Copyright Notice
# //@C ================
# //@C This file is part of CPSW. It is subject to the license terms in the LICENSE.txt
# //@C file found in the top-level directory of this distribution and at
# //@C https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
# //@C
# //@C No part of CPSW, including this file, may be copied, modified, propagated, or
# //@C distributed except according to the terms contained in the LICENSE.txt file.

# Makefile template for CPSW software:

# Locate CPSW:

CPSW_DIR=framework

# from 'release.mak' CPSW_DIR and other variables
# which define package locations may be overridden.
# Note: must include from $(SRCDIR) (which is redefined
#       when recursing into subdirs).
SRCDIR=.

-include $(SRCDIR)/release.mak
include $(CPSW_DIR)/defs.mak

# Recurse into subdirectories (prior to making this directory)
SUBDIRS += framework
SUBDIRS += docsrc

# Add SHARED_OBJS here (before including 'rules.mak')
SHARED_OBJS     += Int2Dbl.so
Int2Dbl_so_SRCS += int2dbl.cc
Int2Dbl_so_LIBS  = $(CPSW_LIBS)

# Include rules
include $(CPSW_DIR)/rules.mak

clean_local:
	$(RM) -r __pycache__
	$(RM) *.pyc

uninstall:
	$(RM) -r bin lib include doc

.PHONY: uninstall
