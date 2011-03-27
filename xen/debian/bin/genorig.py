#!/usr/bin/env python

import sys
sys.path.append(sys.path[0] + '/../lib/python')

import itertools
import os, os.path
import shutil
import subprocess

from debian_xen.debian import VersionXen
from debian_linux.debian import Changelog


class RepoHg(object):
    def __init__(self, repo):
        self.repo = repo

    def do_archive(self, info):
        orig_dir = os.path.join(info.temp_dir, info.orig_dir)
        args = ('hg', 'archive', '-r', info.options.tag, os.path.realpath(orig_dir))
        subprocess.check_call(args, cwd=self.repo)

    def do_changelog(self, info, log):
        args = ('hg', 'log', '-r', '%s:0' % info.options.tag)
        subprocess.check_call(args, cwd=self.repo, stdout=log)


class Main(object):
    log = sys.stdout.write

    def __init__(self, options, repo):
        self.options = options

        self.changelog_entry = Changelog(version=VersionXen)[0]
        self.source = self.changelog_entry.source

        if self.options.version:
            self.version = self.options.version
        else:
            raise NotImplementedError

        if os.path.exists(os.path.join(repo, '.hg')):
            self.repo = RepoHg(repo)
        else:
            raise NotImplementedError

        self.orig_dir = "%s-%s" % (self.source, self.version)
        self.orig_tar = "%s_%s.orig.tar.gz" % (self.source, self.version)

    def __call__(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp(prefix='genorig', dir='debian')
        try:
            self.do_archive()
            self.do_changelog()
            self.do_tar()
        finally:
            shutil.rmtree(self.temp_dir)

    def do_archive(self):
        self.log("Create archive.\n")
        self.repo.do_archive(self)

    def do_changelog(self):
        self.log("Exporting changelog.\n")
        log = open(os.path.join(self.temp_dir, self.orig_dir, 'Changelog'), 'w')
        self.repo.do_changelog(self, log)
        log.close()

    def do_tar(self):
        out = "../orig/%s" % self.orig_tar
        self.log("Generate tarball %s\n" % out)

        subprocess.check_call(('tar', '-C', self.temp_dir, '-czf', out, self.orig_dir))


if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser(prog=sys.argv[0], usage='%prog [OPTION]... DIR')
    p.add_option("-t", "--tag", dest="tag", default='tip')
    p.add_option("-v", "--version", dest="version")
    options, args = p.parse_args()
    if len(args) != 1:
        raise RuntimeError
    Main(options, *args)()
