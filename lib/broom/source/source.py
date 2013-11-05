import broom
import os
import re
import subprocess

from broom.source.repo import GitRepository

class RevisionInfo(broom.BroomObject):
    ENTRIES = (
            'sha',
            'refs',
            'headers',
            'message',
            'linesAdded',
            'linesRemoved'
            )

    @broom.field(broom.Settable)
    def Path(self):
        return None

    @broom.field(broom.Settable)
    def _Log(self):
        return None

    @broom.field
    def CommitSHA(self):
        return self._Log()[self.ENTRIES.index('sha')]

    @broom.field
    def RefNames(self):
        return self._Log()[self.ENTRIES.index('refs')]

    @broom.field
    def Headers(self):
        return self._Log()[self.ENTRIES.index('headers')]

    @broom.field
    def AuthorName(self):
        return self.Headers()['Author']

    @broom.field
    def AuthorDate(self):
        return self.Headers()['AuthorDate']

    @broom.field
    def Message(self):
        return self._Log()[self.ENTRIES.index('message')]

class PySource(broom.BroomObject):
    """Python source code and metadata."""

    # TODO: This is a hack until we have proper backend
    #       storage (or a database interface to the Git
    #       repository) that allows us to 'set' this value
    #       (really, return a value that is a field) but
    #       not set it directly, as these objects should
    #       be fully read-only.
    @broom.field
    def Path(self):
        """Path to the source code relative to the Broom
        base library.

        """
        return self._path

    @broom.field
    def GitRepositoryPath(self):
        return GitRepository(WorkingDir=self.Path())

    def setRefName(self, value):
        revisionInfo = RevisionInfo(Path=self.Path(), _Log=self._LogByRefName()[value])
        return [broom.NodeChange(self.RefName, value),
                broom.NodeChange(self.RevisionInfo, revisionInfo)
                ]

    @broom.field(broom.Settable, delegate=setRefName)
    def RefName(self):
        # FIXME: This is not exactly right as 'revisions' are
        #        (annoyingly) on a repository level, so we'll
        #        eventually break this down so we can always know
        #        both the latest change, and the overall revision
        #        the file history was extracted from.
        #
        #        Git can be annoyingly stupid about certain
        #        things, even if it gets a lot of other things
        #        right.
        return self._Log()[0][0]

    @broom.field(broom.Settable)
    def RevisionInfo(self):
        # FIXME: This breaks because the graph believes it's a mutation.  We
        #        need to allow new objects to be returned by the graph
        #        because these can only be created via direct sets on
        #        stored fields.
        # return RevisionInfo(Path=self.Path(), CommitSHA=self.CurrentRevision())
        return None

    @broom.field
    def _Log(self):
        return gitlog(self.Path())

    @broom.field
    def _LogByRefName(self):
        entries = self._Log()
        ret = dict((e[0],e) for e in entries)
        ret.update(dict((r,e) for e in entries for ref in entries[1] for r in ref))
        return ret

    def History(self):
        raise NotImplementedError()

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
    if not os.path.isfile(path):
        raise RuntimeError("%s is not a file in a local Git repository." % path)
    dirname = os.path.dirname(path)
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


if __name__ == '__main__':
    pySource = PySource()
    pySource._path = './setup.py'
    pySource.RefName = pySource._Log()[0][0]

    print pySource.GitRepositoryPath()
    ri = pySource.RevisionInfo()
    print ri.AuthorName()
    print ri.Message()
    ri._Log = pySource._LogByRefName()['bd138addc92fa684ca43c649454f8e6d55155271']
    print ri.Message()
