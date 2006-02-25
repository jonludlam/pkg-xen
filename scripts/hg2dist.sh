#!/bin/bash

HG=$(which hg)
HGDIR=$1

if [ ! -x $HG ]; then
	echo "hg must be installed"
	exit 1
fi

if [ ! \( -d "$HGDIR" -a -d "$HGDIR/.hg" \) ]; then
	echo "Usage: $0 <xen-hg-dir>"
	exit 1
fi


CHANGESET=$( (cd $HGDIR; $HG log | head -1 ) | sed -e 's/ //g;' | cut -d: -f2)

RELEASE_LG=$( (cd $HGDIR; $HG log | grep -B 1 "tag:.*RELEASE" | head -2) | sed -e 's/ //g')
REL_CHG=$( echo $RELEASE_LG | cut -d: -f2 )
REL_VER=$( echo $RELEASE_LG | cut -d- -f2 )

if [ $REL_CHG = $CHANGESET ]; then
	DESTDIR="xen-${REL_VER}"
	DESTTAR="xen_${REL_VER}.orig.tar.gz"
else
	DESTDIR="xen-${REL_VER}+hg${CHANGESET}"
	DESTTAR="xen_${REL_VER}+hg${CHANGESET}.orig.tar.gz"
fi


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

