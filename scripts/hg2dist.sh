#!/bin/bash

HG=$(which hg)
HGDIR=$1

if [ ! -x $HG ]; then
	echo "hg must be installed"
	exit 1
fi

if [ ! \( -d $HGDIR -a -d $HGDIR/.hg \) ]; then
	echo "Usage: $0 <xen-hg-dir>"
	exit 1
fi


CHANGESET=$( (cd $HGDIR; $HG log | head -1 ) | sed -e 's/ //g;' | cut -d: -f2)
RELEASE=$( (cd $HGDIR; $HG log | grep "tag:.*RELEASE" | head -1) | sed -e 's/ //g; s/tag:RELEASE-//')

DESTDIR="xen-${RELEASE}+hg${CHANGESET}"
DESTTAR="xen_${RELEASE}+hg${CHANGESET}.orig.tar.gz"

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

tar -zc $DESTDIR -f $DESTTAR || exit 1;

echo "DONE"
echo "Now please svn export your debian directory in $DESTDIR and check that the changelog version matches"

