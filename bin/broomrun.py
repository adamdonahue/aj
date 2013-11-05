#!/usr/bin/env python2.7
#
# broomrun - The Broom runtime.
#

import argparse
import importlib
import sys

def main():
    parser = argparse.ArgumentParser(description='Run a Broom program.')
    parser.add_argument('--db-server',
            action='store',
            )
    parser.add_argument('--db',
            action='store',
            help='database to connect to (default: %(default)s)'
            )
    parser.add_argument('--rev', '-r',
            action='store',
            default=None
            )
    parser.add_argument('script',
            action='store',
            help='script to execute'
            )
    parser.add_argument('script_args',
            action='store',
            nargs=argparse.REMAINDER,
            help='arguments to pass to script'
            )

    args = parser.parse_args()

    # TODO: Add better handling of script-specific arguments.
    script_args = []
    script_kwargs = {}
    for arg in args.script_args:
        if not arg.startswith('-') or arg == '-':
            script_args.append(arg)
        elif not arg.startswith('--'):
            script_kwargs[arg[1:]] = True
        elif '=' in arg:
            k,v = arg.lstrip('-').split('=', 1)
            script_kwargs[k] = v
        else:
            script_kwargs[arg.lstrip('-')] = True

    if args.rev:
        import auto
        sys.meta_path = [auto.AutoImporter(args.rev)] + sys.meta_path

    module = importlib.import_module(args.script)
    if 'main' not in dir(module):
        raise NotImplementedError("No main function has been defined in %s" % module.__name__)
    sys.exit(module.main(*script_args, **script_kwargs))

if __name__ == '__main__':
    main()
