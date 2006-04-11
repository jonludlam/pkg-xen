#!/bin/bash

HG=$(which hg)
HGDIR=$1
MAJOR=$2

if [ ! -x $HG ]; then
	echo "hg must be installed"
	exit 1
fi

if [ ! -d "$HGDIR" ] && [ ! -d "$HGDIR/.hg" ] || [ -z "$MAJOR" ]; then
	echo "Usage: $0 <xen-hg-dir> <major>"
	exit 1
fi


HASH=$( cd $HGDIR; $HG id | awk '{ print $1}')
CHANGESET=$( cd $HGDIR; $HG log -r $HASH | head -n 1 | sed -e 's/ //g;' | cut -d: -f2)

RELEASE_LG=$( cd $HGDIR; $HG tags | perl -ne 'BEGIN { $done = 0; } /RELEASE-([0-9.]+) +(\d+):/; if ($1 and $2 <= '$CHANGESET' and not $done) { print $2,":",$1,"\n"; $done = 1; }')
REL_CHG=$( echo $RELEASE_LG | cut -d: -f1 )
REL_VER=$( echo $RELEASE_LG | cut -d: -f2 )

if [ $MAJOR = "unstable" ]; then
	VERSION="hg${CHANGESET}"
elif [ $REL_CHG = $CHANGESET ]; then
	VERSION="${REL_VER}"
else
	VERSION="${REL_VER}+hg${CHANGESET}"
fi

DESTDIR="xen-${MAJOR}-${VERSION}"
DESTTAR="xen-${MAJOR}_${VERSION}.orig.tar.gz"

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

