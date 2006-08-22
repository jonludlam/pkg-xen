#!/bin/bash

HG=$(which hg)
HGDIR=$1

if [ ! -x $HG ]; then
	echo "hg must be installed"
	exit 1
fi

if [ ! -d "$HGDIR" ] && [ ! -d "$HGDIR/.hg" ]; then
	echo "Usage: $0 <xen-hg-dir>"
	exit 1
fi



eval $(env -i -- make -f - version <<EOF
include $HGDIR/xen/Makefile

HASH = \$(shell cd $HGDIR; $HG id | awk '{ print \$\$1}')
CHANGESET = \$(shell cd $HGDIR; $HG log -r \$(HASH) | head -n 1 | sed -e 's/ //g;' | cut -d: -f2)

VERSION = \$(XEN_VERSION).\$(XEN_SUBVERSION)+hg\$(CHANGESET)

PHONY: version
version:
	@echo DESTDIR="xen-common-\$(VERSION)"
	@echo DESTTAR="xen-common_\$(VERSION).orig.tar.gz"
EOF)

if [ -d $DESTDIR ]; then
	echo "Destination directory $DESTDIR already exists"
	exit 1
fi

if [ -f $DESTTAR ]; then
	echo "Destination file $DESTTAR already exists"
fi

echo "Exporting xen-common to $DESTDIR..."

mkdir $DESTDIR || exit 1;

mkdir $DESTDIR/tools
cp -a $HGDIR/Config.mk $DESTDIR
cp -a $HGDIR/tools/{Rules.mk,examples} $DESTDIR/tools
(cd $HGDIR; $HG log Config.mk tools/{Rules.mk,examples}) > $DESTDIR/ChangeLog

echo "Creating orig file $DESTTAR..."

tar zcf $DESTTAR $DESTDIR || exit 1;

echo "DONE"
echo "Now please svn export your debian directory in $DESTDIR and check that the changelog version matches"

