#/usr/bin/python3

# test_nfa.py

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

import unittest

from nfa import *

def digraph_template(txt):
    return 'digraph { rankdir = LR; ' + txt + ' node [shape=plaintext label=""]; nothing->"0"; }'

class TestNfa(unittest.TestCase):

    def testAddTrans(self):
        nf = Nfa()
        nf.addTransition(Transition(0, 'a', 1))
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"];'))

    def testAddTwoTrans(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                          Transition(0, 'b', 2)])
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "0" -> "2" [label="b"];'))

    def testAddThreeTrans(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                          Transition(0, 'b', 1),
                          Transition(0, 'b', 2)])
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "0" -> "1" [label="b"]; "0" -> "2" [label="b"];'))

    
    def testAddTwoTrans(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                          Transition(0, 'b', 2)])
        nf.setAccepting(2)
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "0" -> "2" [label="b"]; 2 [shape=doublecircle];'))
