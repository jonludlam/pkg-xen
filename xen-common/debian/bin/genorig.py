#!/usr/bin/env python

import os, os.path, re, shutil, sys

sys.path.append(sys.path[0] + '/../lib/python')

from debian_xen.debian import VersionXen, Changelog

class GenOrig(object):
    log = sys.stdout.write

    files = ['config', 'Config.mk', 'docs/Docs.mk', 'docs/Makefile', 'docs/man', 'tools/Rules.mk', 'tools/examples']

    def __init__(self, repo, tag, version):
        self.repo, self.tag, self.version = repo, tag, version

        self.changelog_entry = Changelog(version = VersionXen)[0]
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
        raise NotImplementedError

    def do_archive(self):
        self.log("Create archive.\n")
        include_args = ' '.join(('-I %s' % i for i in self.files))
        f = os.popen("cd %s; hg archive %s %s/%s" % (self.repo, include_args, os.path.realpath(self.dir), self.orig_dir))
        if f.close() is not None:
            raise RuntimeError

    def do_changelog(self):
        self.log("Exporting changelog.\n")
        file_args = ' '.join(self.files)
        f = os.popen("cd %s; hg log %s" % (self.repo, file_args))
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
