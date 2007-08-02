#!/usr/bin/env python

import os, os.path, re, shutil, sys

class GenOrig(object):
    log = sys.stdout.write

    def __init__(self, source, repo, tag = None, version = None):
        self.source, self.repo, self.tag, self.version = source, repo, tag, version

    def __call__(self):
        import tempfile
        self.dir = tempfile.mkdtemp(prefix = 'genorig', dir = 'debian')
        try:
            self.do_update()
            self.do_version()

            self.orig_dir = "%s-%s.orig" % (self.source, self.version)
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
    GenOrig(args[1], args[2], options.tag, options.version)()
