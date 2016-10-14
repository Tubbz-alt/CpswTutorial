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

# Add PROGRAMS here (before including 'rules.mak')

# Include rules
include $(CPSW_DIR)/rules.mak

clean_local:
	$(RM) -r __pycache__
