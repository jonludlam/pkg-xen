#!/usr/bin/env python2.4
import sys
sys.path.append(sys.argv[2]+ "/lib/python")
import debian_linux.gencontrol
from debian_linux.config import *
from debian_linux.debian import *

class gencontrol(debian_linux.gencontrol.gencontrol):
    makefile_targets = ('binary-arch', 'build', 'setup')

    def __init__(self):
        super(gencontrol, self).__init__()
        self.process_changelog(read_changelog())

    def do_main_setup(self, vars, makeflags, extra):
        makeflags.update({
            'MAJOR': self.version['xen']['major'],
            'VERSION': self.version['xen']['version'],
            'SHORT_VERSION': self.version['xen']['short_version'],
            'EXTRAVERSION': self.version['xen']['extraversion'],
            'ABINAME': self.abiname,
        })

    def do_main_packages(self, packages, extra):
        packages.extend(self.process_packages(self.templates["control.main"], self.vars))

        packages['source']['Build-Depends'].append('linux-support-%s' % sys.argv[1])

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

    def process_changelog(self, changelog):
        self.version = changelog[0]['Version']
        self.version['xen'] = parse_version_xen(self.version['complete'])
        self.abiname = '-%s' % self.config['abi',]['abiname']
        self.vars = {
            'major': self.version['xen']['major'],
            'version': self.version['xen']['version'],
            'short_version': self.version['xen']['short_version'],
            'abiname': self.abiname,
        }

def parse_version_xen(version):
    version_re = ur"""
^
(?P<source>
    (?P<upstream>
        (?P<version>
            (?P<major>\d+\.\d+)
            (
                (
                    (?P<minor>\.\d+)
                    (
                        (-\d+)
                        |
                        (~rc\d+)
                    )
                )
                |
                (?P<unstable>-unstable)
            )
        )
        (?:
            \+hg
            (?P<hg_rev>
                \d+
            )
        )?
    )
    -
    (?P<debian>[^-]+)
)
$
"""
    match = re.match(version_re, version, re.X)
    if match is None:
        raise ValueError
    ret = match.groupdict()
    if ret['unstable'] is not None:
        ret['major'] = 'unstable'
        ret['short_version'] = ret['version']
        ret['extraversion'] = ret['unstable']
    else:
        ret['version'] = ret['major'] + ret['minor']
        ret['short_version'] = ret['major']
        ret['extraversion'] = ret['minor']
    del ret['unstable']
    return ret

if __name__ == '__main__':
    gencontrol()()
