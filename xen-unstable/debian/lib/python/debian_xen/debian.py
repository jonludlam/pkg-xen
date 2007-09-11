import re
from debian_linux.debian import Version

class VersionXenUnstable(Version):
    _version_xen_rules = ur"""
^
(?P<version>
    \d+\.\d+
    -unstable
)
(?:
    \+hg
    (?P<hg_rev>
        \d+
    )
)
-
(?:[^-]+)
$
"""
    _version_xen_re = re.compile(_version_xen_rules, re.X)

    def __init__(self, version):
        super(VersionXenUnstable, self).__init__(version)
        match = self._version_xen_re.match(version)
        if match is None:
            raise ValueError("Invalid debian xen version")
        d = match.groupdict()
        self.xen_major = 'unstable'
        self.xen_version = d['version']

if __name__ == '__main__':
    gencontrol()()
