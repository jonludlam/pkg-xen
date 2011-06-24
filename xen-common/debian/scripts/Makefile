ETC_SCRIPTS = \
	qemu-ifup

GLOBAL_WRAPPER_SCRIPTS = \
	cpuperf-perfcntr \
	cpuperf-xen \
	xend \
	xenperf \
	xenpm \
	xentop \
	xentrace \
	xentrace_format \
	xentrace_setmask \
	xentrace_setsize \
	xl \
	xm

PRIVATE_SCRIPTS = \
	xen-version \
	$(WRAPPER)

WRAPPER = xen-utils-wrapper

ETC_SCRIPTS_DIR = /etc/xen/scripts
GLOBAL_SCRIPTS_DIR = /usr/sbin
PRIVATE_SCRIPTS_DIR = /usr/lib/xen-common/bin

install:
	install -d $(DESTDIR)$(ETC_SCRIPTS_DIR)
	install $(ETC_SCRIPTS) $(DESTDIR)$(ETC_SCRIPTS_DIR)
	install -d $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)
	@for i in $(GLOBAL_WRAPPER_SCRIPTS); do \
	    echo ln -s $(PRIVATE_SCRIPTS_DIR)/$(WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i; \
	    ln -s $(PRIVATE_SCRIPTS_DIR)/$(WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i || exit 1; \
	done
	install -d $(DESTDIR)$(PRIVATE_SCRIPTS_DIR)
	install $(PRIVATE_SCRIPTS) $(DESTDIR)$(PRIVATE_SCRIPTS_DIR)

