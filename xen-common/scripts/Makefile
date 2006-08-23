SCRIPTS = \
	cpuperf-perfcntr \
	cpuperf-xen \
	xend \
	xenperf \
	xenstore-chmod \
	xenstore-control \
	xenstore-exists \
	xenstore-list \
	xenstore-ls \
	xenstore-read \
	xenstore-rm \
	xenstore-write \
	xentop \
	xentrace \
	xentrace_format \
	xentrace_setmask \
	xentrace_setsize \
	xm

WRAPPER = xen-utils-wrapper

SCRIPTS_DIR = /usr/sbin
WRAPPER_DIR = /usr/lib/xen-common/bin

install:
	install -d $(DESTDIR)$(SCRIPTS_DIR)
	install -d $(DESTDIR)$(WRAPPER_DIR)
	@for i in $(SCRIPTS); do \
	    echo ln -s $(WRAPPER_DIR)/$(WRAPPER) $(DESTDIR)$(SCRIPTS_DIR)/$$i; \
	    ln -s $(WRAPPER_DIR)/$(WRAPPER) $(DESTDIR)$(SCRIPTS_DIR)/$$i || exit 1; \
	done
	install $(WRAPPER) $(DESTDIR)$(WRAPPER_DIR)

