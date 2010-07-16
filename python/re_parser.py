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

# See the file grammar.txt for the EBNF this is based on

# The source of the grammar:
#     http://www.cs.sfu.ca/~cameron/Teaching/384/99-3/regexp-plg.html

import ply.yacc as yacc

from relex import tokens

from nfa import Transition

class ParseTree(object):
    def __init__(self):
        pass

    def __str__(self):
        return ''
    
    def getTransitions(self, in_s):
        raise Exception('No transitions for this class')

class PTChar(ParseTree):
    def __init__(self, val):
        if val is None:
            raise Exception('cannot have None character')
        self.val = val

    def __str__(self):
        return self.val
    
    def getTransitions(self, in_s):
        return (in_s + 1, [Transition(in_s, self.val, in_s+1)])

class PTClosure(ParseTree):
    def __init__(self, child):
        if child is None:
            raise Exception('cannot have None closure')
        self.child = child

    def __str__(self):
        return '({})*'.format(self.child)

    def getTransitions(self, in_s):
        ns, childTrans = self.child.getTransitions(in_s+1)
        
        return (ns+1, [Transition(in_s, '_eps', in_s+1),
                      Transition(in_s, '_eps', ns+1),
                      Transition(ns, '_eps', in_s+1),
                      Transition(ns, '_eps', ns+1)] + childTrans)


class PTAlternation(ParseTree):
    def __init__(self, left, right):
        if left is None or right is None:
            raise Exception('cannot have None in Alternation')
        self.left = left
        self.right = right

    def __str__(self):
        return '({})|({})'.format(self.left, self.right)


    def getTransitions(self, in_s):
        ns, leftTrans = self.left.getTransitions(in_s+1)
        ns2, rightTrans = self.right.getTransitions(ns+1)
        
        
        return (ns2+1, [Transition(in_s, '_eps', in_s+1),
                      Transition(in_s, '_eps', ns+1),
                      Transition(ns, '_eps', ns2+1),
                      Transition(ns2, '_eps', ns2+1)] + leftTrans + rightTrans)

class PTConcatenation(ParseTree):
    def __init__(self, left, right):
        if left is None or right is None:
            raise Exception('cannot have None in Concatenation')
        self.left = left
        self.right = right

    def __str__(self):
        return '{}{}'.format(self.left, self.right)

    def getTransitions(self, in_s):
        ns, leftTrans = self.left.getTransitions(in_s)
        ns2, rightTrans = self.right.getTransitions(ns)
        
        return (ns2, leftTrans + rightTrans)

class PTCharSet(ParseTree):
    def __init__(self, cset_str):
        if cset_str is None:
            raise Exception('cannot have None in CharSet')
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

    def getTransitions(self, in_s):
        if len(self.cset)==0:
            return (in_s, [])

        trs = []
        for char in sorted(self.cset):
            trs.append(Transition(in_s, char, in_s+1))
        return (in_s + 1, trs)

def debug_p(msg='', res=[]):
    # print('{}: {}'.format(msg, [str(x) for x in list(res)]))
    pass

def p_re(p):
    '''re : union
          | simplere
    '''
    debug_p('re', p)
    p[0] = p[1]
    debug_p('  re', p)
    
def p_union(p):
    '''union : re BAR simplere
    '''
    debug_p('union', p)
    p[0] = PTAlternation(p[1], p[3])
    debug_p('  union', p)

def p_simplere(p):
    '''simplere : concat
                | basicre
    '''
    debug_p('simplere', p)
    p[0] = p[1]
    debug_p('  simplere', p)

def p_concat(p):
    '''concat : simplere basicre
    '''
    debug_p('concat', p)
    p[0] = PTConcatenation(p[1], p[2])
    debug_p('  concat', p)
    
def p_basicre(p):
    ''' basicre : star
                | plus
                | elemre
    '''
    debug_p('bre', p)
    p[0] = p[1]
    debug_p('  bre', p)

def p_star(p):
    ''' star : elemre ASTERIK
    '''
    debug_p('star', p)
    p[0] = PTClosure(p[1])
    debug_p('  star', p)

def p_plus(p):
    ''' plus : elemre PLUS
    '''
    debug_p('plus', p)
    p[0] = PTConcatenation(p[1], PTClosure(p[1]))
    debug_p('  plus', p)

def p_elemre(p):
    ''' elemre : group
               | char
               | cset
    '''
    debug_p('elemre', p)
    p[0] = p[1]
    debug_p('  elemre', p)

def p_group(p):
    ''' group : LPAREN re RPAREN
    '''
    debug_p('(', p)
    p[0] = p[2]
    debug_p('  )', p)

def p_char(p):
    ''' char : OTHER
    '''
    debug_p('.', p)
    p[0] = PTChar(p[1])
    debug_p('  .', p)

def p_cset(p):
    ''' cset : LBRACK setitems RBRACK
    '''
    debug_p('[', p)
    p[0] = PTCharSet(p[2])
    debug_p('  ]', p)

def p_setitems(p):
    ''' setitems : setitem
                 | setitem setitems
    '''
    if len(p)>2:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]

def p_setitem(p):
    ''' setitem : OTHER
    '''
    p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input: {}".format(p))

# Build the parser
parser = yacc.yacc()

def parse(ins):
    return parser.parse(ins)
    
def main():
    return

if __name__=="__main__":
    main()

