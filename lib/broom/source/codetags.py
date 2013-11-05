"""A simple codetag extraction utility.

"""
import argparse
import collections
import itertools
import re
import token
import tokenize

# TODO: Integrate with Git metadata.
# TODO: Add ability to generate output in various formats.
# TODO: Add ability to create JIRA tickets for codetags.

# Based on PEP-0350: http://www.python.org/dev/peps/pep-0350.
MNEMONICS = [
    ('TODO', ('MILESTONE',
              'MLSTN',
              'DONE',
              'YAGNI',
              'TBD',
              'TOBEDONE'
              )
        ),
    ('FIXME', ('XXX',
               'DEBUG',
               'BROKEN',
               'REFACTOR',
               'REFACT',
               'RFCTR',
               'OOPS',
               'SMALL',
               'NEEDSWORK',
               'INSPECT'
               )
        ),
    ('BUG', ('BUGFIX',)),
    ('IDEA', ()),
    ('???', ('QUESTION',
             'QUEST',
             'QSTN',
             'WTF'
             )
        ),
    ('!!!', ('ALERT',)),
    ('HACK',  ('CLEVER',
               'MAGIC'
               )
        ),
    ('NOTE', ('HELP',)),
    ('TODOC', ('DOCDO',
               'DODOC',
               'NEEDSDOC',
               'EXPLAIN',
               'DOCUMENT'
               )
        )
    ]
MNEMONICS_ALIAS = dict((v,k) for k,vs in MNEMONICS for v in vs)
MNEMONICS_ALL = list(itertools.chain(*[tuple([k]) + vs for k,vs in MNEMONICS]))

Codetag = collections.namedtuple('Codetag',
                                 ['filename',
                                  'mnemonic',
                                  'comment',
                                  'start',
                                  'end',
                                  'revision',
                                  'author',
                                  'context',
                                  ]
                                 )

class CodetagCollector(object):

    CODETAG_RE = r'.*?#\s*(.*?):\s*(.*?)$'

    def __init__(self, fileName):
        self.fileName = fileName
        self.tokenizer = tokenize.generate_tokens(open(fileName).readline)
        self.pushed = None

    def wrappedNext(self):
        if self.pushed is not None:
            pushed = self.pushed
            self.pushed = None
            return pushed
        return self.tokenizer.next()

    def collect(self):
        self.codetags = []
        while True:
            try:
                token, value, start, end, line = self.wrappedNext()
            except StopIteration:
                break
            if not self.isComment(token):
                continue
            matches = re.search(self.CODETAG_RE, value)
            if not matches:
                continue
            mnemonic, comment = matches.groups()
            mnemonic = mnemonic.upper()
            if mnemonic not in MNEMONICS_ALL:
                continue
            p = False
            context = [value + "\n"]
            while True:
                try:
                    t,v,s,end,l = self.tokenizer.next()
                except:
                    break
                if self.isNewline(t):
                    if p:
                        break
                    p = True
                    continue
                elif not self.isComment(t) or self.isStart(v):
                    self.pushed = (t,v,s,end,l)
                    break
                context.append(re.sub(r'^\s*', '', l))
                v = re.sub('\s*?#', '', v.strip())
                p = False
                if not v:
                    continue
                comment += "\n" + v.lstrip()
            self.codetags.append(Codetag(self.fileName,
                                         MNEMONICS_ALIAS.get(mnemonic, mnemonic),
                                         comment,
                                         start,
                                         end,
                                         None,
                                         None,
                                         context
                                         )
                                 )

    def report(self, includeComment=False):
        if not hasattr(self, 'codetags'):
            raise Exception("You must first collect the tags.")
        for tag in self.codetags:
            comment = tag.comment.replace("\n", " ").replace("\t", " ")
            print "\t".join([tag.filename,
                             tag.mnemonic,
                             comment,
                             str(tag.start),
                             str(tag.end)
                             ])
            if includeComment and tag.context:
                print "\t" + "\t".join(tag.context)

    def isStart(self, line):
        return re.search(self.CODETAG_RE, line, re.IGNORECASE)

    def isNewline(self, tok):
        return token.tok_name[tok] in ['NL']

    def isComment(self, tok):
        return token.tok_name[tok] in ['COMMENT']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source',
            action='store',
            help='A Python script or module.'
            )
    parser.add_argument('--include-comment-text',
            action='store_true',
            default=False,
            help='Include the block of text from which the tag was extracted.'
            )
    args = parser.parse_args()
    collector = CodetagCollector(args.source)
    collector.collect()
    collector.report(includeComment=args.include_comment_text)

if __name__ == '__main__':
    main()
