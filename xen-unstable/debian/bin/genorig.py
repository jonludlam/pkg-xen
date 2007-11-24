#!/usr/bin/env python

import os, os.path, re, shutil, sys

sys.path.append(sys.path[0] + '/../lib/python')

from debian_xen.debian import VersionXenUnstable
from debian_linux.debian import Changelog

class GenOrig(object):
    log = sys.stdout.write

    def __init__(self, repo, tag = None, version = None):
        self.repo, self.tag, self.version = repo, tag, version

        self.changelog_entry = Changelog(version = VersionXenUnstable)[0]
        self.source = self.changelog_entry.source

    def __call__(self):
        import tempfile
        self.dir = tempfile.mkdtemp(prefix = 'genorig', dir = 'debian')
        try:
            self.do_update()
            self.do_version()

            self.orig_dir = "%s-%s" % (self.source, self.version)
            self.orig_tar = "%s_%s.orig.tar.gz" % (self.source, self.version)

            self.do_archive()
            self.do_changelog()
            self.do_tar()
        finally:
            shutil.rmtree(self.dir)

    def do_update(self):
        if self.tag is None:
            return
        raise NotImplementedError

    def do_version(self):
        if self.version is not None:
            return

        f = file('%s/xen/Makefile' % self.repo)
        for l in f:
            l = l.strip().split()
            if not l:
                continue
            if l[0] == 'export':
                l.pop(0)
            if l[0] == 'XEN_VERSION':
                xen_version = l[-1]
            elif l[0] == 'XEN_SUBVERSION':
                xen_subversion = l[-1]
        f.close()
        if xen_version is None or xen_subversion is None:
            raise RuntimeError("Can't find version in Xen source")

        f = os.popen("cd '%s'; hg id" % self.repo)
        id = f.read().strip().split()[0]
        f.close()
        f = os.popen("cd '%s'; hg log -r %s" % (self.repo, id))
        changeset = f.read().strip().split()[1].split(':')[0]

        self.version = '%s.%s-unstable+hg%s' % (xen_version, xen_subversion, changeset)

        self.log("Use version %s.\n" % self.version)

    def do_archive(self):
        self.log("Create archive.\n")
        f = os.popen("cd %s; hg archive %s/%s" % (self.repo, os.path.realpath(self.dir), self.orig_dir))
        if f.close() is not None:
            raise RuntimeError

    def do_changelog(self):
        self.log("Exporting changelog.\n")
        f = os.popen("cd %s; hg log" % (self.repo))
        f_out = file("%s/%s/Changelog" % (self.dir, self.orig_dir), 'w')
        shutil.copyfileobj(f, f_out)
        if f.close() is not None:
            raise RuntimeError
        f_out.close()

    def do_tar(self):
        out = "../orig/%s" % self.orig_tar
        self.log("Generate tarball %s\n" % out)
        f = os.popen("tar -C %s -czf %s %s" % (self.dir, out, self.orig_dir))
        if f.close() is not None:
            raise RuntimeError

if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option("-t", "--tag", dest = "tag")
    p.add_option("-v", "--version", dest = "version")
    options, args = p.parse_args(sys.argv)
    GenOrig(args[1], options.tag, options.version)()
