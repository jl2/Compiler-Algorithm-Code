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

import ply.yacc as yacc

from relex import tokens

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


def p_r(p):
    '''r : r2
         | empty
    '''
    if len(p)>2 and p[2]:
        print("Got: {}".format(p[2]))
        p[0] = PTConcatenation(p[1], p[2])
    else:
        p[0] = p[1]

def p_r2_alt(p):
    "r2 : r BAR r"
    p[0] = PTAlternation(p[1], p[3])

# def p_r_bar(p):
#     'r : r BAR r'
#     p[0] = p[1]
    
def p_empty(p):
    'empty :'
    pass

def p_r2_closure(p):
    "r2 : r ASTERIK"
    p[0] = PTClosure(p[1])

def p_r2_plus(p):
    "r2 : r PLUS"
    p[0] = PTConcatenation(p[1], PTClosure(p[1]))

def p_r2_f(p):
    "r2 : f"
    p[0] = p[1]

def p_f_paren(p):
    'f : LPAREN r RPAREN'
    p[0] = p[2]

def p_f_char(p):
    "f : OTHER"
    p[0] = PTChar(p[1])

def p_f_cc(p):
    "f : LBRACK OTHER RBRACK"
    p[0] = PTCharSet(p[2])

# def p_ccin(p):
#     """ccin : OTHER ccin
#             | empty"""
#     print('in ccin: {}'.format(list(p)))
#     if len(p)>2 and p[2]:
#         p[0] = p[1] + p[2]
#     else:
#         p[0] = p[1]

precedence = (
    ('nonassoc', 'BAR'),
    ('left', 'ASTERIK', 'PLUS'),
)

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input: {}".format(p))


# Build the parser
parser = yacc.yacc()

def parse(ins):
    return parser.parse(ins)
    
def main():
    parseTree = PTAlternation(PTClosure(PTChar('a')), PTClosure(PTChar('b')))
    print(parseTree)
    return

if __name__=="__main__":
    main()

