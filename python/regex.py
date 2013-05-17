#!/usr/bin/env python3

# regex.py

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

import ply.lex as lex
import ply.yacc as yacc
from collections import namedtuple

# List of token names.   This is always required

tokens = (
    'LPAREN', 'RPAREN',

    'LBRACK', 'RBRACK',

    'LBRACE', 'RBRACE',

    'ASTERIK',
    'PLUS',
    'BAR',
    'NUMBER',
    'COMMA',
    'COLON',
    'OPT',
    'OTHER'
)

# Regular expression rules for simple tokens
t_LPAREN = '\('
t_RPAREN = '\)'

t_LBRACK = '\['
t_RBRACK = '\]'

t_LBRACE = '{'
t_RBRACE = '}'

t_ASTERIK = '\*'
t_PLUS = '\+'
t_BAR = '\|'
t_COMMA = ','
t_OPT = '\?'
t_COLON = ':'

def t_NUMBER(t):
    '[0-9]+'
    return t

def t_OTHER(t):
    '[^][()|+*{}?:, \t]'
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

Transition = namedtuple('Transition', 'os, ch, ns')

class ParseTree(object):
    def __init__(self):
        raise Exception('Impossible to create a base class ParseTree')

    def __str__(self):
        raise Exception('Use a subclass')
    
    def getTransitions(self, in_s):
        raise Exception('No transitions for ParseTree base class')

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

class PTCount(ParseTree):
    def __init__(self, child, cmin, cmax):
        if child is None:
            raise Exception('cannot have None count')
        if cmin > cmax or cmax == 0:
            raise Exception('Bad range for count {} - {}'.format(cmin, cmax))
        self.child = child
        self.cmin = int(cmin)
        self.cmax = int(cmax)

    def __str__(self):
        rv = '({})'.format(self.child)
        if (self.cmin == self.cmax):
            rv += '{{{}}}'.format(self.cmin)
        else:
            rv += '{{{},{}}}'.format(self.cmin, self.cmax)
        return rv

    def getTransitions(self, in_s):
        trans = []
        ns = in_s
        ct = []
        
        for i in range(self.cmin):
            nns, ct = self.child.getTransitions(ns)
            trans += ct
            ns = nns

        to_end = []

        for i in range(self.cmax - self.cmin):
            to_end.append(ns)
            nns, ct = self.child.getTransitions(ns)
            trans += ct

            ns = nns

        for st in to_end:
            trans.append(Transition(st, '_eps', ns))

        return (ns, trans)

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


# POSIX character sets
named_csets = {':alnum:': 'a-zA-Z0-9',
               ':alpha:': 'a-zA-Z',
               ':ascii:': '\x00-\x7F',
               ':blank:': ' \t',
               ':cntrl:': '\x00-\x1F\x7F',
               ':digit:': '0-9',
               ':graph:': '\x21-\x7E',
               ':lower:': 'a-z',
               ':print:': '\x21-\x7E',
               ':punct:': '''!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~''',
               ':space:': ' \t\r\n\v\f',
               ':upper:': 'A-Z',
               ':word:': 'a-zA-Z0-9_',
               ':xdigit:': '0-9a-fA-F'}

class PTCharSet(ParseTree):
    def __init__(self, cset_str):
        if cset_str is None:
            raise Exception('cannot have None in CharSet')
        self.cset = set()
        if named_csets.get(cset_str):
            cset_str = named_csets[cset_str]
        i = 0
        # print('cset_str = {}'.format(cset_str))
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
        if len(self.cset)==1:
            return ''.join(self.cset)
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
                | opt
                | plus
                | count
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

def p_opt(p):
    ''' opt : elemre OPT
    '''
    debug_p('opt', p)
    p[0] = PTCount(p[1], 0, 1)
    debug_p('  opt', p)

def p_count(p):
    ''' count : elemre icount
    '''
    debug_p('count', p)
    cmin, cmax = p[2][0], p[2][1]
    p[0] = PTCount(p[1], cmin, cmax)
    debug_p('  count', p)

def p_icount(p):
    ''' icount : LBRACE incount RBRACE
    '''
    debug_p('{', p)
    p[0] = p[2]
    debug_p('  }', p)

def p_incount(p):
    ''' incount : NUMBER
               | NUMBER COMMA NUMBER
    '''
    debug_p('icount', p)

    if len(p)>2:
        p[0] = (p[1], p[3])
    else:
        p[0] = (p[1], p[1])

    debug_p('  icount', p)

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
             | COMMA
             | NUMBER
    '''
    debug_p('.', p)
    p[0] = PTCharSet(p[1])
    debug_p('  .', p)
   
def p_cset(p):
    ''' cset : LBRACK class_or_setitems RBRACK
    '''
    debug_p('[', p)
    p[0] = PTCharSet(p[2])
    debug_p('  ]', p)

def p_class_or_setitems(p):
    ''' class_or_setitems : COLON name COLON
                          | setitems
    '''
    if len(p)>2:
        p[0] = ':' + p[2] + ':'
    else:
        p[0] = p[1]

def p_setitems(p):
    ''' setitems : setitem
                 | setitem setitems
    '''
    debug_p('si', p)
    if len(p)>2:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]
    debug_p('  si', p)

def p_setitem(p):
    ''' setitem : OTHER
                | NUMBER
                | COMMA
                | LPAREN
                | RPAREN
    '''
    debug_p('si2', p)
    p[0] = p[1]
    debug_p('  si2', p)

def p_name(p):
    ''' name : OTHER
            | OTHER name
    '''
    if len(p)>2:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


# Error rule for syntax errors
def p_error(p):
    # Better error handling required...
    # print("Syntax error in input: {}".format(p))
    pass

# Build the lexer
lexer = lex.lex()

# Build the parser
parser = yacc.yacc()

class Dfa(object):
    def __init__(self, rx = None):
        if rx:
            # I have my doubts whether or not this is a good practice...
            tmp = Nfa(rx).to_dfa()
            self.transitions = tmp.transitions
            self.accepting = tmp.accepting
            self.start = tmp.start
        else:
            self.transitions = dict()
            self.start = 0
            self.accepting = set()

    def addTransition(self, tran):
        # Add empty dictionary if it's not there
        self.transitions.update({tran.os: self.transitions.get(tran.os, {})})

        # Add the transition
        self.transitions[tran.os][tran.ch] = tran.ns

    def addAcceptState(self, st):
        self.accepting.add(st)

    # Test whether an Dfa accepts for the given string
    def matches(self, ins):
        curs = self.start
        for c in ins:
            if c in self.transitions[curs]:
                curs = self.transitions[curs][c]
            else:
                return False

        return len(self.accepting.intersection({curs}))>0

    def to_dot(self):
        result = 'digraph { rankdir = LR;'
        for st in sorted(self.transitions):
            for chs in sorted(self.transitions[st]):
                result += ' "{}" -> "{}" [label="{}"];'.format(st, self.transitions[st][chs], chs)

        for st in sorted(self.accepting):
            result += ' ' + str(st) + ' [shape=doublecircle];'

        result += ' node [shape=plaintext label=""]; nothing->"0"; }'
        return result

class Nfa(object):
    def __init__(self, rxs = None):
        self.transitions = dict()
        self.start = 0
        self.accepting = set()
        if rxs:
            pt = parser.parse(rxs)
            curState = 0
            ns, newTrans = pt.getTransitions(0)
            self.addTransitions(newTrans)
            self.setAccepting(ns)

    def addTransition(self, tran):
        self.transitions.update({tran.os: self.transitions.get(tran.os, {})})
        self.transitions[tran.os].update({tran.ch: self.transitions[tran.os].get(tran.ch, set())})
        self.transitions[tran.os][tran.ch].update({tran.ns})

    def addTransitions(self, trans):
        for t in trans:
            self.addTransition(t)

    def setAccepting(self, st):
        self.accepting.update(self.e_closure(st))
        
    def to_dot(self):
        result = 'digraph { rankdir = LR;'
        for st in sorted(self.transitions):
            for chs in sorted(self.transitions[st]):
                for ns in sorted(self.transitions[st][chs]):
                    lbl = chs
                    if lbl == '_eps':
                        lbl = '&epsilon;'
                    result += ' "{}" -> "{}" [label="{}"];'.format(st, ns, lbl)

        for st in sorted(self.accepting):
            result += ' ' + str(st) + ' [shape=doublecircle];'

        result += ' node [shape=plaintext label=""]; nothing->"0"; }'
        return result

    # Return a set of states accessible from st using only epsilon transitions
    def e_closure(self, st):
        if self.transitions.get(st) is None:
            # This could happen in two cases:
            #  * st really doesn't exist
            #  * st is a terminating accept state
            # Return {st} to simplify handling the second case...
            return {st}

        ss = {st}
        nt = set()
        os = 0
        ns = len(ss)
        while os != ns:
            os = ns
            for s in ss:
                nt.update(self.transitions.get(s, {}).get('_eps', set()))
            ss.update(nt)
            ns = len(ss)
        return ss

    # move is described in Figure 3.31 of section 3.7.1 of the Dragon book
    def move(self, sts, ch):
        new_states = set()
        for st in sts:
            tmp = self.transitions.get(st, {}).get(ch, set())
            for subs in tmp:
                new_states.update(self.e_closure(subs))
        return new_states

    # Test whether an Nfa accepts for the given string
    def matches(self, ins):
        curs = self.e_closure(self.start)
        for c in ins:
            curs = self.move(curs, c)
        return len(curs.intersection(self.accepting))>0

    def get_alphabet(self):
        alphabet = {'_eps'}
        for k in self.transitions.values():
            alphabet = alphabet.union(set(k.keys()))
        alphabet.remove('_eps')
        return alphabet

    def state_id(self, states, ss):
        ns = len(states)
        try:
            sid = states.index(ss)
        except ValueError as nf:
            sid = len(states)
            states.append(ss)
        return sid

    def to_dfa(self):
        df = Dfa()

        alphabet = self.get_alphabet()

        states = []

        unmarked_states = set()
        marked_states = set()

        ns = 0
        nss = self.e_closure(self.start)
        cs = self.state_id(states, nss)
        unmarked_states.add(cs)

        if len(self.accepting.intersection(nss))>0:
            df.addAcceptState(ns)

        while len(unmarked_states) > 0:
            cs = unmarked_states.pop()
            for cur_char in alphabet:
                nss = self.move(states[cs], cur_char)
                ns = self.state_id(states, nss)

                df.addTransition(Transition(cs, cur_char, ns))

                if ns not in marked_states:
                    unmarked_states.add(ns)

                if len(self.accepting.intersection(nss))>0:
                    df.addAcceptState(ns)
            marked_states.add(cs)
        return df


def re_match(rx, ins, use_dfa=False):
    if use_dfa:
        return Dfa(rx).matches(ins)
    return Nfa(rx).matches(ins)

def main():
    # print(Nfa('abc(ab|cd*)*def').to_dfa().to_dot())
    # print(Nfa('(a|b)*abb').to_dfa().to_dot())
    # print(Dfa('a{0,3}').to_dot())
    # print(Dfa('(a|b)*abb').to_dot())
    # print(Nfa('(a|b)*abb').to_dfa().to_dot())
    # print(Nfa('[0123456789]{3}-[0123456789]{3}-[0123456789]{4}').to_dot())
    print(Dfa('([:digit:]{3}-){1,2}[:digit:]{4}').to_dot())
    return

if __name__=="__main__":
    main()

