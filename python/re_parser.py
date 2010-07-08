#!/usr/bin/python3

# re_parser.py

# Copyright (c) 2010, Jeremiah LaRocco jeremiah.larocco@gmail.com

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

class ParseTree(object):
    def __init__(self):
        self.children = None

    def __str__(self):
        return ''

class PTChar(ParseTree):
    def __init__(self, val):
        self.val = val
        self.children = None

    def __str__(self):
        return self.val

class PTClosure(ParseTree):
    def __init__(self, child):
        self.child = child

    def __str__(self):
        return '({})*'.format(self.child)

class PTAlternation(ParseTree):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return '({})|({})'.format(self.left, self.right)

class PTConcatenation(ParseTree):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return '({})({})'.format(self.left, self.right)

class PTCharSet(ParseTree):
    def __init__(self, cset):
        self.cset = cset

    # ugly, but works
    def __str__(self):
        return '[{}]'.format(''.join(sorted(self.cset)))


def parse(ins):
    
    return ParseTree()
    
def main():
    parseTree = PTAlternation(PTClosure(PTChar('a')), PTClosure(PTChar('b')))
    print(parseTree)
    return

if __name__=="__main__":
    main()
