"""PROTOTYPE.

Interface to remote fetching of Broom modules/libraries
underlying the broomloader.py framework.

Should really be just another database, but for now
we're leveraging Git clones behind the scenes.

"""

import flask
import os
import json
import subprocess

# TODO: Productionize.

BASE = "/tmp/source"
MASTER = "/tmp/source/master"

app = flask.Flask(__name__)

def full_path(rev, *args):
    return os.path.join(BASE, rev, 'lib', *args)

def info(name, rev, recurse=True):
    path = name.replace('.', '/')
    if os.path.exists(full_path(rev, path + '.py')):
        return name, 'module', full_path(rev, path + '.py')
    elif os.path.isdir(full_path(rev, path)) \
            and os.path.exists(full_path(rev, path, '__init__.py')):
        return name, 'package', full_path(rev, path, '__init__.py')
    if not recurse or '.' not in name:
        return (name, None, None)
    name = '.'.join([name.rsplit('.', 2)[0], name.rsplit('.')[-1]])
    return info(name, rev, recurse=False)

@app.route('/source/<rev>/<name>')
def source(rev, name):
    # Parameters:
    #   refresh={0,1}       Whether to do a fetch/merge.
    args = flask.request.args
    git_path = os.path.join(BASE, rev)
    if not os.path.exists(MASTER):
        raise NotImplementedError("call to mk_git_rev()")
    if not os.path.exists(git_path):
        raise NotImplementedError("call to mk_git_rev()")
    if args.get('refresh', False):
        raise NotImplementedError("call to refresh_git_rev()")
    n, t, p = info(name, rev)
    if not t:
        return ('Not found: %s %s %s' % (n,t,p), 404, None)

    source = open(p).read()
    return json.dumps({'source': source,
            'type': t,
            'name': n,
            'path': '/%s' % p[p.index('lib/')+4:p.index('/__init__.py')] \
                            if t == 'package' \
                            else None,
            'file': '(%s)/%s' % (rev, p[p.index('lib/')+4:])
            })

def refresh_git_rev(rev, base=BASE):
    p = subprocess.Popen("cd {}/{} && git fetch" % (base, rev), shell=True)
    p.wait()

def mk_git_rev(source, rev, base=BASE):
    if not os.path.exists(base):
        os.makedirs(base)
    p = subprocess.Popen(
            "cd {base} && "
            "git clone {source} {rev} &&"
            "cd {rev} && "
            "git checkout {rev}"
            .format(
                    base=base,
                    source=source,
                    rev=rev
                    ), shell=True)
    p.wait()

if __name__ == '__main__':
    import socket
    app.run(socket.gethostname(), port=5001, debug=True)
