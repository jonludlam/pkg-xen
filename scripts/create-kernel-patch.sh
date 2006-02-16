#!/bin/bash
LINUX_VERSION=2.6.12

make linux-2.6-xen-config CONFIGMODE=oldconfig
cat linux-$LINUX_VERSION-xen/Makefile | grep -v "EXTRAVERSION =" | sed '/SUBLEVEL\ =/a EXTRAVERSION\ =' > linux-$LINUX_VERSION-xen/Makefile
diff -Nurp pristine-linux-$LINUX_VERSION/ linux-$LINUX_VERSION-xen/ >linux-$LINUX_VERSION-xen.patch
