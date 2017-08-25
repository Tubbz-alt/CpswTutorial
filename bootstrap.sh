#!/bin/sh
if [ ! -f .git/hooks/post-checkout ] ; then
	echo '#!/bin/sh' > .git/hooks/post-checkout
	echo 'git submodule update --init --recursive' >> .git/hooks/post-checkout
	chmod a+x .git/hooks/post-checkout
fi
if [ ! -f .git/hooks/post-merge ]; then
	cp .git/hooks/post-checkout .git/hooks/post-merge
fi
git submodule update --init --recursive
echo "INSTALL_DIR=`pwd`" > release.mak
CONFIG_LOCAL=framework/config.local.mak 
if [ ! -e $CONFIG_LOCAL] || ! grep -q "ARCHES[ \t]*[=]" $CONFIG_LOCAL; then
	echo '# Build tutorial for host-arch only' >> $CONFIG_LOCAL
	echo 'ARCHES=$(HARCH)'                     >> $CONFIG_LOCAL
fi
make doc
