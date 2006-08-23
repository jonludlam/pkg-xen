GLOBAL_SCRIPTS = \
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

PRIVATE_SCRIPTS = \
	xen-utils-root \
	$(WRAPPER)

WRAPPER = xen-utils-wrapper

GLOBAL_SCRIPTS_DIR = /usr/sbin
PRIVATE_SCRIPTS_DIR = /usr/lib/xen-common/bin

install:
	install -d $(DESTDIR)$(GLOBAL_SCRIPTS_DIR) $(DESTDIR)$(PRIVATE_SCRIPTS_DIR)
	@for i in $(GLOBAL_SCRIPTS); do \
	    echo ln -s $(PRIVATE_SCRIPTS_DIR)/$(WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i; \
	    ln -s $(PRIVATE_SCRIPTS_DIR)/$(WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i || exit 1; \
	done
	install $(PRIVATE_SCRIPTS) $(DESTDIR)$(PRIVATE_SCRIPTS_DIR)

