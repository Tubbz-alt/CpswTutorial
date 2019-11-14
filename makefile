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

CPSW_DIR=framework/src

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
TGTS    += env
GENERATED_SRCS += env.slac

# Add SHARED_OBJS here (before including 'rules.mak')
SHARED_OBJS     += Int2Dbl.so
Int2Dbl_so_SRCS += int2dbl.cc
Int2Dbl_so_LIBS  = $(CPSW_LIBS)

# default target
install:

# Include rules
include $(CPSW_DIR)/rules.mak

clean_local:
	$(RM) -r __pycache__
	$(RM) *.pyc
	$(RM) env.slac

doc: sub-./docsrc@install_local
	@true

env: $(CPSW_DIR)/../config.mak $(wildcard $(CPSW_DIR)/../config.local.mak)
	@echo 'export LD_LIBRARY_PATH="$(abspath $(boostlib_DIR)):$(abspath $(yaml_cpplib_DIR)):$(abspath $(INSTALL_DIR)/$(TARCH)/lib):$${LD_LIBRARY_PATH:+:$${LD_LIBRARY_PATH}}"' > $@
	@echo 'export PYTHONPATH="$(abspath $(INSTALL_DIR)/$(TARCH)/bin)$${PYTHONPATH:+:$${PYTHONPATH}}"' >> $@
	@echo 'source "$(pyinc_DIR)/../../use.bash"' >> $@

uninstall_doc:
	$(RM) doc

env.slac:
	$(RM) $@
	ln -s O.$(HARCH)/env $@

.PHONY: env doc
