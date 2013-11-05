import broom
import git
import os
import re
import subprocess
import tempfile

from ..utility.sequence import loneItem

def workingDir(path):
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    output = subprocess.check_output(
            "cd %(path)s && "
            "git rev-parse "
            "--show-toplevel" % locals(), shell=True)
    return output.strip()

def parseRevision(lines):
    c = re.search(r'^commit ([^\s]+)(?: \((.*)\)$)?', lines[0]) #  ?(?:\s\(([^,)]+)\))?$', lines[0])
    if not c:
        raise RuntimeError("Invalid format.")
    commit, refs = c.groups()
    refs = [r.strip() for r in refs.split(',')] if refs else []
    headers = {}
    for i,l in enumerate(lines[1:]):
        if not l.strip():
            break
        header, value = l.split(':', 1)
        headers[header] = value.strip()
    i += 2
    message = []
    for j,l in enumerate(lines[i:]):
        if re.match('[0-9]', l):
            break
        message.append(re.sub(r'^    ', '', l.rstrip()))
    message = "\n".join(message)
    for change in lines[j+i:]:
        print 'C: ', change
    linedAdded, linesRemoved = lines[-1].split("\t")[0:2]
    return (commit, refs, headers, message, linedAdded, linesRemoved)

def gitlog(path, revision='master'):
    """Fetch the log for the specified file in a local Git
    repository.

    """
    # TODO: This is a temporary routine to test functionality
    #       until Git commits are logged to a relational
    #       database.

    # FORMAT: %h - commit
    #
    path = os.path.abspath(path)
    dirname = os.path.dirname(path) if not os.path.isdir(path) else path
    output = subprocess.check_output(
            "cd %(dirname)s && "
            "git log %(revision)s "
            "--numstat "
            "--decorate "
            "%(path)s" % locals(), shell=True
            )
    revisions = []
    for entry in re.split(r'\n(?=commit)', output):
        revisions.append(parseRevision(entry.splitlines()))
    return revisions

class GitRepositoryException(Exception):
    pass

class GitRepository(broom.BroomObject):
    """A Git repository."""

    @classmethod
    def clone(cls, source, path=None):
        path = path or tempfile.mkdtemp()
        repo = git.Repo.clone_from(source, path)
        return cls(_Repository=repo)

    @classmethod
    def isRepository(cls, path='.'):
        """Returns True if the specified path is part of a
        working directory for a Git repository, or False
        otherwise.

        """
        try:
            repo = git.Repo(path)
        except git.exc.InvalidGitRepositoryError:
            return False
        return True

    @broom.field(broom.Settable)
    def _Repository(self):
        """The underlying git.Repo object."""
        if not self.WorkingDir():
            return
        return git.Repo(self.WorkingDir())

    @broom.field(broom.Settable)
    def RemoteURI(self):
        section = self.RemoteConfigReader()._section_name
        return self.RemoteConfig("url")

    # TODO: Make delegates work for loaded objects.
    def setWorkingDir(self, value):
        return [broom.NodeChange(self.WorkingDir, workingDir(value))]

    @broom.field(broom.Settable)
    def WorkingDir(self):
        if not self._Repository():
            return
        return self._Repository().working_dir

    @broom.field
    def Remote(self):
        return self._Repository().remote()

    @broom.field
    def RemoteConfigReader(self):
        return self.Remote().config_reader

    @broom.field
    def RemoteConfigSection(self):
        return self.RemoteConfigReader()._section_name

    @broom.field
    def _RemoteConfig(self):
        return self.RemoteConfigReader().config

    @broom.field
    def RemoteConfig(self, key):
        config = self._RemoteConfig()
        return config.get(self.RemoteConfigSection(), key)

    def dirty(self):
        return self._Repository().is_dirty()

    def dirtyIndex(self):
        return self._Repository().is_dirty(index=True, working_tree=False)

    def dirtyWorkingTree(self):
        return self._Repository().is_dirty(index=False)

    def untrackedFiles(self):
        return self._Repository().untracked_files

    def branches(self):
        return [branch.name for branch in self._Repository().branches]

    def head(self):
        return self._Repository().head

    def currentBranch(self):
        head = self._Repository().head
        if head.is_detached:
            raise GitRepositoryException("HEAD is currently detached and "
                                         "pointing to {}"\
                                                 .format(str(head.commit)))
        return head.ref.name

    def tags(self):
        return [tag.name for tag in self._Repository().tags]

    def commitForTag(self, tag):
        return getattr(self._Repository().tags, tag).commit.hexsha

    def commitForBranch(self, branch):
        return getattr(self._Repository().heads, branch).commit.hexsha

    def createTag(self, tag, ref='HEAD', message=None, force=False):
        repo = self._Repository()
        if message is None:
            message = "Created tag {} on ref {}.".format(tag, ref)
        return repo.create_tag(tag,
                               ref     = ref,
                               message = message,
                               force   = force
                               )

    def pushTag(self, tag):
        pushInfos = self.Remote().push(':refs/tags/{}'.format(tag))
        if pushInfos is None:
            raise GitRepositoryException("Error pushing tag '{}' to remote 'origin'.".format(tag))
        return

    def deleteTags(self, tags):
        return self._Repository().delete_tag(*tags)

    def deleteTag(self, tag):
        return self.deleteTags([tag])

    @broom.field
    def RepositoryName(self):
        results = self._Repository().git.remote('-v').splitlines()
        for line in results:
            if '(fetch)' in line:
                return re.search(r':([/\w.-]+)(\.git)?', line).group(1)
        return None

    @broom.field
    def IsNetPackageRepository(self):
        """Returns True if the repository is used to version
        an externally-sourced package.

        """
        if self.RepositoryName().startswith('net-pkg/'):
            return True
        return False

    @broom.field
    def IsAppRepository(self):
        try:
            self.AppName()
        except:
            return False
        return True

    @broom.field
    def IsAppConfigRepository(self):
        name = self.RepositoryName()
        if name is None or not name.startswith('app-config/'):
            return False
        return True

    @broom.field
    def BaseName(self):
        return self.RepositoryName().rsplit('/', 1)[-1]

    @broom.field
    def AppName(self):
        if not self.RepositoryName().startswith('app/'):
            return None
        return self.BaseName()

    def log(self, path=None, revision=None):
        path = path or self.WorkingDir()
        revision = revision or self.head()
        return gitlog(path, revision)

    def push(self):
        self.Remote().push()

    def pull(self):
        self.Remote().pull()

    def fetch(self):
        self.Remote().fetch()

    def fetchTags(self):
        self.Remote().fetch(tags=True)

    def isTag(self, ref):
        """Returns True if the specified ref identifies a
        tag, or False otherwise.

        """
        if ref.startswith('refs/tags'):
            ref = ref.split('/', 2)[-1]
        return ref in self.tags()

    def isBranch(self, ref):
        """Returns True if the specified ref identifies a
        branch, or False otherwise.

        """
        if ref.startswith('refs/heads'):
            ref = ref.split('/', 2)[-1]
        return ref in self.branches()

    def checkout(self, rev, force=False, fetch=False):
        """Checks out the specified revision, which can be
        either a branch, a tag, or commit SHA.

        If fetch is True, also fetches latest updates from
        the remote server (picking up new branches and tags
        as well).

        """
        repo = self._Repository()
        if fetch:
            self.fetch()
        repo.git.checkout(rev, force=force)

    def specFileNames(self):
        def walk(a, dirName, fileNames):
            for fileName in fileNames:
                if fileName.endswith('.spec'):
                    a.append(fileName)
        accum = []
        os.path.walk(self.WorkingDir(), walk, accum)
        return accum

    def specFileName(self):
        """Returns the expected path to the repository's RPM spec file.

        """
        return loneItem(self.specFileNames())

    def hasSpecFiles(self):
        return bool(len(self.specFileNames()))

    def __repr__(self):
        return '<GitRepository %s;"%s";uri="%s";dirty=%s>' % (
                self.RepositoryName(),
                self.WorkingDir(),
                self.RemoteURI(),
                self.dirty()
                )
