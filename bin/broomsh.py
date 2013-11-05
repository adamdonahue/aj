#!/usr/bin/env python2.7
#
# broom - A Broom-enabled Python shell.

import argparse
import code
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rev", "-r",
        action="store",
        default="master"
        )
    group.add_argument("--local", "-l",
        action="store_true",
        default=False
        )
    args = parser.parse_args()

    if not args.local and args.rev:
        import broomloader
        sys.meta_path = sys.meta_path + [broomloader.AutoImporter(args.rev)]

    # Standard helpers will go here.

    console_args = {}
    console = code.InteractiveConsole(console_args)
    console.interact("[broomsh (source rev: %s)]" %
            args.rev if not args.local else "(local)")
