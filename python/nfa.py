#!/usr/bin/python3

# nfa.py

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


from collections import namedtuple

import re_parser

Transition = namedtuple('Transition', 'os, ch, ns')

class Nfa(object):
    def __init__(self):
        self.transitions = dict()
        self.start = 0
        self.accepting = set()
        pass

    def addTransition(self, tran):
        self.transitions.update({tran.os: self.transitions.get(tran.os, {})})
        self.transitions[tran.os].update({tran.ch: self.transitions[tran.os].get(tran.ch, set())})
        self.transitions[tran.os][tran.ch].update({tran.ns})

    def addTransitions(self, trans):
        for t in trans:
            self.addTransition(t)

    def setAccepting(self, st):
        self.accepting.update({st})
        
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

    # nfa_move is described in Figure 3.31 of section 3.7.1 of the Dragon book
    def nfa_move(self, sts, ch):
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
            curs = self.nfa_move(curs, c)
        return len(curs.intersection(self.accepting))>0

# nfa_matches :: Nfa -> String -> Bool
# nfa_matches fa str =
#     ((Set.size (Set.intersection (n_accepting fa) (inner_match fa str (e_closure fa (n_start fa)))))>0)
#     where
#       inner_match fa ([]) set = set
#       inner_match fa (x:xs) set = inner_match fa xs (e_closure_set fa (nfa_move fa set (NfaChar x)))

def fromRegex(rx):
    pt = re_parser.parse(rx)
    nf = Nfa()
    curState = 0
    ns, newTrans = pt.getTransitions(0)
    nf.addTransitions(newTrans)
    nf.setAccepting(ns)
    return nf

def re_match(rx, ins):
    nf = fromRegex(rx)
    return nf.matches(ins)

def main():
    print(fromRegex('abc(ab|cd*)*def').to_dot())

if __name__=='__main__':
    main()
