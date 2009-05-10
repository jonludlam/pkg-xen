#!/usr/bin/env python

import sys
sys.path.append(sys.path[0] + '/../lib/python')

import itertools
import os, os.path
import shutil
import subprocess

from debian_xen.debian import VersionXen, Changelog

class Main(object):
    log = sys.stdout.write

    files = ('config', 'Config.mk', 'docs/Docs.mk', 'docs/Makefile', 'docs/man', 'tools/Rules.mk', 'tools/examples')

    def __init__(self, options, repo):
        self.options, self.repo = options, repo

        self.changelog_entry = Changelog(version = VersionXen)[0]
        self.source = self.changelog_entry.source

    def __call__(self):
        import tempfile
        self.dir = tempfile.mkdtemp(prefix='genorig', dir='debian')
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
        if not self.options.tag:
            return

        self.log('Updating to tag %s.\n' % self.options.tag)
        p = subprocess.Popen(('hg', 'update', '-r', self.options.tag), cwd=self.repo)
        if p.wait():
            raise RuntimeError

    def do_version(self):
        if self.options.version:
            self.version = self.options.version
            return
        raise NotImplementedError

    def do_archive(self):
        self.log("Create archive.\n")

        arg_dir = os.path.join(os.path.realpath(self.dir), self.orig_dir)
        args = ('hg', 'archive', arg_dir) + tuple(itertools.chain(*(('-I', i) for i in self.files)))
        p = subprocess.Popen(args, cwd=self.repo)
        if p.wait():
            raise RuntimeError

    def do_changelog(self):
        self.log("Exporting changelog.\n")

        log = open("%s/%s/Changelog" % (self.dir, self.orig_dir), 'w')

        args = ('hg', 'log') + tuple(self.files)
        p = subprocess.Popen(args, cwd=self.repo, stdout=log)
        if p.wait():
            raise RuntimeError

        log.close()

    def do_tar(self):
        out = "../orig/%s" % self.orig_tar
        self.log("Generate tarball %s\n" % out)
        f = os.popen("tar -C %s -czf %s %s" % (self.dir, out, self.orig_dir))
        if f.close() is not None:
            raise RuntimeError

if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser(prog=sys.argv[0], usage='%prog [OPTION]... DIR')
    p.add_option("-t", "--tag", dest="tag")
    p.add_option("-v", "--version", dest="version")
    options, args = p.parse_args()
    if len(args) != 1:
        raise RuntimeError
    Main(options, *args)()
