#!/usr/bin/env python
#
# Prepare an existing Maestro3 task for migration to Tasker.
#
# Essentially attempts to parse parameters, update method calls,
# repoint libraries, and perform other tasks on old scripts
# in order to move them to the new format, in anticipation of a
# developer then reviewing the code and handling more sophisticated
# conversions.
#

import json
import re
import shutil
import sys
import tempfile

def convert_parameter_spec(parameter_spec):
    return re.search(r'^\s*#\s*@([^\s]+)\s+(.*?)$', parameter_spec).groups()

def convert_parameter_specs(parameter_specs):
    params = [convert_parameter_spec(s) for s in parameter_specs]
    ret = {}
    for k,v in params:
        if k.startswith('DISABLED'):
            continue
        if k in ('note', 'endnote'):
            continue
        if k in ('tag',):
            ret.setdefault("{}s".format(k), []).extend(eval(v))
        elif k in ('parameter',):
            matches = re.search("(?<!\")([Tt]rue|[Ff]alse)(?!\")", v)
            if matches:
                match = matches.group(0)
                v = re.sub("(?<!\")" + match + "(?!\")", '"' + match + '"', v)
            ret.setdefault("{}s".format(k), []).append(eval(v))
        else:
            ret[k] = v
    return "# {{ \n%s\n# }}" % "\n".join(["# {}".format(l) for l in json.dumps(ret, indent=4).splitlines()])

def prep_source_file(infile, edit_in_place=False):
    if edit_in_place:
        outfile = tempfile.NamedTemporaryFile(delete=False)
    else:
        outfile = sys.stdout

    lines = infile.readlines()  # These scripts are small.
    llines = len(lines)
    for i in range(llines):
        if re.match(r'\s*#\s*@', lines[i]):
            break
        print >>outfile, lines[i],

    parameter_specs = []
    in_multiline_parameter = False
    while True:
        if i == llines:
            break
        if not re.match(r'\s*#\s*(@|$)', lines[i]) \
            and not in_multiline_parameter:
                break
        parameter_specs.append(lines[i])
        i += 1

    if parameter_specs:
        converted_parameter_specs = convert_parameter_specs(parameter_specs)
        print >>outfile, converted_parameter_specs

    for i in range(i, llines):
        print >>outfile, lines[i],

    if outfile != sys.stdout:
        outfile.close()
    infile.close()
    if infile != sys.stdin and edit_in_place:
        shutil.move(outfile.name, infile.name)

    return None

def main(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Prepare Maestro3 task source files for migration to Tasker.',
                                     epilog='And remember that a task still needs to be fully migrated.',
                                     )

    parser.add_argument('-i', '--edit-in-place',
            action='store_true',
            default=False,
            help='edit source in place'
            )

    parser.add_argument('-b', '--backup',
            action='store_true',
            default=False,
            help='create backup of source file when editing in place (default: %(default)s)'
            )

    parser.add_argument('-e', '--backup-extension',
            metavar='EXT',
            action='store',
            default='~'
            )

    parser.add_argument('infile', 
            type=argparse.FileType('rb', 0), 
            default=sys.stdin,
            nargs='?'
            )

    args = parser.parse_args(argv[1:])

    backup_file = None
    if args.edit_in_place:
        if args.infile == sys.stdin:
             parser.exit("Cannot edit <stdin> in place.")
        if args.backup:
            backup_file = ''.join([args.infile.name, args.backup_extension])
    if backup_file:
        shutil.copy2(args.infile.name, backup_file) # cp -p

    prep_source_file(args.infile, edit_in_place=args.edit_in_place)

if __name__ == '__main__':
    main(sys.argv)
