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

ifeq (\$(XEN_EXTRAVERSION),-unstable)
MAJOR = unstable
else
MAJOR = \$(XEN_VERSION).\$(XEN_SUBVERSION)
endif

HASH = \$(shell cd $HGDIR; $HG id | awk '{ print \$\$1}')
CHANGESET = \$(shell cd $HGDIR; $HG log -r \$(HASH) | head -n 1 | sed -e 's/ //g;' | cut -d: -f2)

ifneq (\$(MAJOR),unstable)
RELEASE_CHG = \$(shell cd $HGDIR; $HG tags | perl -ne 'BEGIN { \$\$done = 0; } /RELEASE-([-0-9.]+) +(\d+):/; if (\$\$1 and \$\$2 <= '\$(CHANGESET)' and not \$\$done) { print "\$\$2\n"; \$\$done = 1; }')
endif

ifeq (\$(RELEASE_CHG),\$(CHANGESET))
VERSION = \$(XEN_FULLVERSION)
else
VERSION = \$(XEN_FULLVERSION)+hg\$(CHANGESET)
endif

PHONY: version
version:
	@echo DESTDIR="xen-\$(MAJOR)-\$(VERSION)"
	@echo DESTTAR="xen-\$(MAJOR)_\$(VERSION).orig.tar.gz"
EOF)

if [ -d $DESTDIR ]; then
	echo "Destination directory $DESTDIR already exists"
	exit 1
fi

if [ -f $DESTTAR ]; then
	echo "Destination file $DESTTAR already exists"
fi

echo "Exporting xen to $DESTDIR..."

mkdir $DESTDIR || exit 1;

cp -R $HGDIR/* $DESTDIR/ # This skips everything starting with a ., which is what we want
(cd $HGDIR; $HG log) > $DESTDIR/ChangeLog

echo "Creating orig file $DESTTAR..."

tar zcf $DESTTAR $DESTDIR || exit 1;

echo "DONE"
echo "Now please svn export your debian directory in $DESTDIR and check that the changelog version matches"

