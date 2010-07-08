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
        pass

    def __str__(self):
        return ''

class PTChar(ParseTree):
    def __init__(self, val):
        self.val = val

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
        return '{}{}'.format(self.left, self.right)

class PTCharSet(ParseTree):
    def __init__(self, cset_str):
        self.cset = set()
        i = 0
        while (i<len(cset_str)):
            if i==0 and cset_str[i]=='-':
                self.cset.add('-')

            elif cset_str[i] == '-' and i==(len(cset_str)-1):
                self.cset.add('-')
            
            elif cset_str[i] == '-':
                first_val = ord(cset_str[i-1])
                last_val = ord(cset_str[i+1])
                self.cset = self.cset.union(chr(x) for x in range(first_val, last_val+1))
                i+=1
            else:
                self.cset.add(cset_str[i])

            i+=1

    # ugly, but works
    def __str__(self):
        # return '{}'.format([x for x in self.cset])
        return '[{}]'.format(''.join(sorted(self.cset)))

# Tokens:
OTHER = 0
LPAREN = 1
RPAREN = 2
LBRACK = 3
RBRACK = 4
ASTERIK = 5
DASH = 6
PLUS = 7
BAR = 8

tokenTypes = {'(': LPAREN,
              ')': RPAREN,
              '[': LBRACK,
              ']': RBRACK,
              '+': PLUS,
              '-': DASH,
              '|': BAR,
              '*': ASTERIK}

def tokenFor(char):
    global tokenTypes
    return tokenTypes.get(char, OTHER)

class RE_SyntaxError(Exception):
    pass

class ParserState(object):
    def __init__(self, ins):
        self.string = ins
        self.position = 0

    def match(self, char):
        if self.curChar() == char:
            self.position += 1
            return True
        raise RE_SyntaxError

    def curChar(self):
        return self.string[self.position]

    def curToken(self):
        return tokenFor(self.curChar())

    def done(self):
        return self.position == len(self.string)

    def next(self):
        self.position += 1

    def __str__(self):
        # return '{} (position = {})'.format(self.string, self.position)
        if self.position>= len(self.string): return '{}_'.format(self.string)
        return '{}_{}'.format(self.string[0:self.position], self.string[self.position:])

def debug_ps(targ):
    def wrapp(*args):
        # print('{}({})'.format(targ.__name__, ','.join(str(arg) for arg in args)))
        res = targ(*args)
        # print("{}({}) got: {}".format(targ.__name__, ','.join(str(arg) for arg in args), res))
        return res
        
    return wrapp


@debug_ps
def R(pstate):
    if pstate.done(): return None
    r2, r1 = R2(pstate), R(pstate)
    if r1:
        return PTConcatenation(r2, r1)
    return r2

@debug_ps
def R2(pstate):
    pt = F(pstate)

    if pstate.done():
        return pt

    if pstate.curToken() == ASTERIK:
        pstate.match('*')
        return PTClosure(pt)

    elif pstate.curToken() == BAR:
        pstate.match('|')
        return PTAlternation(pt, R2(pstate))

    elif pstate.curToken() == PLUS:
        pstate.match('+')
        return PTConcatenation(pt, PTClosure(pt))

    elif pstate.curToken() in [OTHER, LPAREN, LBRACK]:
        return PTConcatenation(pt, F(pstate))

    else:
        return pt
    

@debug_ps
def CC(pstate):
    mys = ''
    while not pstate.done() and pstate.curToken() != RBRACK:
        mys += pstate.curChar()
        pstate.next()

    return PTCharSet(mys)

@debug_ps
def F(pstate):
    ct = pstate.curToken()

    if ct == LBRACK:
        pstate.match('[')
        rs = CC(pstate)
        pstate.match(']')
        if not pstate.done() and pstate.curToken() in [OTHER, LPAREN, LBRACK]:
            return PTConcatenation(rs, F(pstate))
        return rs

    elif ct == LPAREN:
        pstate.match('(')
        rs = R2(pstate)
        pstate.match(')')
        if not pstate.done() and pstate.curToken() in [OTHER, LPAREN, LBRACK]:
            return PTConcatenation(rs, F(pstate))
        return rs

    elif ct == OTHER:
        rv = PTChar(pstate.curChar())
        pstate.next()
        if not pstate.done() and pstate.curToken() in [OTHER, LPAREN, LBRACK]:
            return PTConcatenation(rv, F(pstate))
        return rv

    raise RE_SyntaxError
    
def parse(ins):
    ps = ParserState(ins)
    return R(ps)
    
def main():
    parseTree = PTAlternation(PTClosure(PTChar('a')), PTClosure(PTChar('b')))
    print(parseTree)
    return

if __name__=="__main__":
    main()

