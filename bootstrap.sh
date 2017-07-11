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
echo 'pyinc_DIR_linux_x86_64=/opt/TWWfsw/python27/include/python2.7/' >> framework/config.local.mak
echo "INSTALL_DIR=`pwd`" >> framework/config.local.mak
make doc
