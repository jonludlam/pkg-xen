#!/usr/bin/env python

import os, sys
sys.path.append(os.path.join(sys.path[0], "../lib/python"))

from debian_xen.debian import VersionXen
from debian_linux.config import ConfigCoreHierarchy
from debian_linux.debian import Changelog
from debian_linux.gencontrol import Gencontrol as Base
from debian_linux.utils import Templates

class Gencontrol(Base):
    def __init__(self):
        super(Gencontrol, self).__init__(ConfigCoreHierarchy(["debian/arch"]), Templates(["debian/templates"]))
        self.process_changelog()

    def do_main_setup(self, vars, makeflags, extra):
        makeflags.update({
            'VERSION': self.version.xen_version,
            'ABINAME': self.abiname,
        })

    def do_main_packages(self, packages, vars, makeflags, extra):
        packages.extend(self.process_packages(self.templates["control.main"], vars))

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

        for i in ('postinst', 'prerm', 'lintian-overrides'):
            j = self.substitute(self.templates["xen-utils.%s" % i], vars)
            file("debian/%s.%s" % (package_utils_name, i), 'w').write(j)

        cmds_binary_arch = ["$(MAKE) -f debian/rules.real binary-arch-arch %s" % makeflags]
        cmds_build = ["$(MAKE) -f debian/rules.real build-arch %s" % makeflags]
        cmds_setup = ["$(MAKE) -f debian/rules.real setup-arch %s" % makeflags]
        makefile.add('binary-arch_%s_real' % arch, cmds = cmds_binary_arch)
        makefile.add('build_%s_real' % arch, cmds = cmds_build)
        makefile.add('setup_%s_real' % arch, cmds = cmds_setup)

    def do_flavour_setup(self, vars, makeflags, arch, featureset, flavour, extra):
        for i in (
            ('config', 'CONFIG'),
        ):
            if vars.has_key(i[0]):
                makeflags[i[1]] = vars[i[0]]

    def do_flavour_packages(self, packages, makefile, arch, featureset, flavour, vars, makeflags, extra):
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

        cmds_binary_arch = ["$(MAKE) -f debian/rules.real binary-arch-flavour %s" % makeflags]
        cmds_build = ["$(MAKE) -f debian/rules.real build-flavour %s" % makeflags]
        cmds_setup = ["$(MAKE) -f debian/rules.real setup-flavour %s" % makeflags]
        makefile.add("binary-arch_%s_%s_%s" % (arch, featureset, flavour), cmds = cmds_binary_arch)
        makefile.add("build_%s_%s_%s" % (arch, featureset, flavour), cmds = cmds_build)
        makefile.add("setup_%s_%s_%s" % (arch, featureset, flavour), cmds = cmds_setup)

    def process_changelog(self):
        changelog = Changelog(version = VersionXen)
        self.version = changelog[0].version
        self.abiname = '-%s' % self.config['abi',]['abiname']
        self.vars = {
            'major': self.version.xen_major,
            'version': self.version.xen_version,
            'abiname': self.abiname,
        }

if __name__ == '__main__':
    Gencontrol()()
