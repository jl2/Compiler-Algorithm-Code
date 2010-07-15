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

    def e_closure(self, st):
        if self.transitions.get(st) is None:
            return set()
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

def fromRegex(rx):
    pt = re_parser.parse(rx)
    nf = Nfa()
    curState = 0
    ns, newTrans = pt.getTransitions(0)
    nf.addTransitions(newTrans)
    nf.setAccepting(ns)
    return nf

def main():
    print(fromRegex('abc(ab|cd*)*def').to_dot())

if __name__=='__main__':
    main()
