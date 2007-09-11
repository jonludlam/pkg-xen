#!/usr/bin/env python
import os, sys
sys.path.append(os.path.join(sys.path[0], "../lib/python"))
from debian_xen.debian import VersionXenUnstable
from debian_linux.gencontrol import Gencontrol as Base
from debian_linux.config import *
from debian_linux.debian import *

class Gencontrol(Base):
    makefile_targets = ('binary-arch', 'build', 'setup')

    def __init__(self):
        super(Gencontrol, self).__init__()
        self.process_changelog()

    def do_main_setup(self, vars, makeflags, extra):
        makeflags.update({
            'MAJOR': self.version.xen_major,
            'VERSION': 'unstable',
            'ABINAME': '',
        })

    def do_main_packages(self, packages, extra):
        packages.extend(self.process_packages(self.templates["control.main"], self.vars))

    def do_arch_setup(self, vars, makeflags, arch, extra):
        for i in (
            ('xen-arch', 'XEN_ARCH'),
        ):
            if vars.has_key(i[0]):
                makeflags[i[1]] = vars[i[0]]

    def do_arch_packages(self, packages, makefile, arch, vars, makeflags, extra):
        utils = self.templates["control.utils"]
        packages_utils = self.process_packages(utils, vars)

        for package in packages_utils:
            name = package['Package']
            if packages.has_key(name):
                package = packages.get(name)
                package['Architecture'].append(arch)
            else:
                package['Architecture'] = [arch]
                packages.append(package)

        package_utils_name = packages_utils[0]['Package']

        for i in ('postinst', 'prerm'):
            j = self.substitute(self.templates["xen-utils.%s" % i], vars)
            file("debian/%s.%s" % (package_utils_name, i), 'w').write(j)

        cmds_binary_arch = []
        cmds_binary_arch.append(("$(MAKE) -f debian/rules.real binary-arch-arch %s" % makeflags))
        cmds_build = []
        cmds_build.append(("$(MAKE) -f debian/rules.real build-arch %s" % makeflags,))
        cmds_setup = []
        cmds_setup.append(("$(MAKE) -f debian/rules.real setup-arch %s" % makeflags,))
        makefile.append(("binary-arch-%s-real:" % arch, cmds_binary_arch))
        makefile.append(("build-%s-real:" % arch, cmds_build))
        makefile.append(("setup-%s-real:" % arch, cmds_setup))

    def do_subarch_makefile(self, makefile, arch, subarch, makeflags, extra):
        pass

    def do_flavour_setup(self, vars, makeflags, arch, subarch, flavour, extra):
        for i in (
            ('config', 'CONFIG'),
        ):
            if vars.has_key(i[0]):
                makeflags[i[1]] = vars[i[0]]

    def do_flavour_makefile(self, makefile, arch, subarch, flavour, makeflags, extra):
        for i in self.makefile_targets:
            makefile.append("%s-%s:: %s-%s-%s" % (i, arch, i, arch, flavour))
            makefile.append("%s-%s-%s:: %s-%s-%s-real" % (i, arch, flavour, i, arch, flavour))

    def do_flavour_packages(self, packages, makefile, arch, subarch, flavour, vars, makeflags, extra):
        hypervisor = self.templates["control.hypervisor"]

        if not vars.has_key('desc'):
            vars['desc'] = ''

        packages_own = []
        packages_own.extend(self.process_packages(hypervisor, vars))

        for package in packages_own:
            name = package['Package']
            if packages.has_key(name):
                package = packages.get(name)
                package['Architecture'].append(arch)
            else:
                package['Architecture'] = [arch]
                packages.append(package)

        package_name = packages_own[0]['Package']

        for i in ('postinst', 'postrm'):
            j = self.substitute(self.templates["xen-hypervisor.%s" % i], vars)
            file("debian/%s.%s" % (package_name, i), 'w').write(j)

        cmds_binary_arch = []
        cmds_binary_arch.append(("$(MAKE) -f debian/rules.real binary-arch-flavour %s" % makeflags,))
        cmds_build = []
        cmds_build.append(("$(MAKE) -f debian/rules.real build-flavour %s" % makeflags,))
        cmds_setup = []
        cmds_setup.append(("$(MAKE) -f debian/rules.real setup-flavour %s" % makeflags,))
        makefile.append(("binary-arch-%s-%s-real:" % (arch, flavour), cmds_binary_arch))
        makefile.append(("build-%s-%s-real:" % (arch, flavour), cmds_build))
        makefile.append(("setup-%s-%s-real:" % (arch, flavour), cmds_setup))
        makefile.append(("source-%s-%s-real:" % (arch, flavour)))

    def process_changelog(self):
        changelog = Changelog(version = VersionXenUnstable)
        self.version = changelog[0].version
        self.vars = {
            'major': self.version.xen_major,
            'version': 'unstable',
            'abiname': '',
        }

if __name__ == '__main__':
    Gencontrol()()
