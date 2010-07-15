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

    def testEpsilon(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                           Transition(0, 'b', 2),
                           Transition(0, '_eps', 2)
                           ])
        nf.setAccepting(2)
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "2" [label="&epsilon;"]; "0" -> "1" [label="a"]; "0" -> "2" [label="b"]; 2 [shape=doublecircle];'))

    def testFromChar(self):
        nf = fromRegex('a')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; 1 [shape=doublecircle];'))

    def testFromCharParens(self):
        nf = fromRegex('(a)')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; 1 [shape=doublecircle];'))

    def testConcatChars(self):
        nf = fromRegex('ab')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "1" -> "2" [label="b"]; 2 [shape=doublecircle];'))

    def testConcatCharsParens(self):
        nf = fromRegex('(a)(b)')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "1" -> "2" [label="b"]; 2 [shape=doublecircle];'))


    def testAlt(self):
        nf = fromRegex('a|b')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "3" [label="&epsilon;"]; ' + 
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "5" [label="&epsilon;"]; ' + 
                                          '"3" -> "4" [label="b"]; ' +
                                          '"4" -> "5" [label="&epsilon;"]; ' +
                                          '5 [shape=doublecircle];'))

    def testConcatAlt(self):
        nf = fromRegex('ab|c')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "4" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; "2" -> "3" [label="b"]; ' +
                                          '"3" -> "6" [label="&epsilon;"]; ' + 
                                          '"4" -> "5" [label="c"]; ' +
                                          '"5" -> "6" [label="&epsilon;"]; ' +
                                          '6 [shape=doublecircle];'))

    def testClosure(self):
        nf = fromRegex('a*')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "3" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "1" [label="&epsilon;"]; ' + 
                                          '"2" -> "3" [label="&epsilon;"]; ' +
                                          '3 [shape=doublecircle];'))

    def testConcatClosure(self):
        nf = fromRegex('(ab)*')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "4" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "3" [label="b"]; ' +
                                          '"3" -> "1" [label="&epsilon;"]; ' + 
                                          '"3" -> "4" [label="&epsilon;"]; ' +
                                          '4 [shape=doublecircle];'))

    def testAltClosure(self):
        nf = fromRegex('a*|b')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "5" [label="&epsilon;"]; ' + 

                                          '"1" -> "2" [label="&epsilon;"]; ' +
                                          '"1" -> "4" [label="&epsilon;"]; ' +
                                          '"2" -> "3" [label="a"]; ' +
                                          '"3" -> "2" [label="&epsilon;"]; ' +
                                          '"3" -> "4" [label="&epsilon;"]; ' + 

                                          '"4" -> "7" [label="&epsilon;"]; ' + 
                                          '"5" -> "6" [label="b"]; ' +
                                          '"6" -> "7" [label="&epsilon;"]; ' + 
                                          '7 [shape=doublecircle];'))

    def testEClosure(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                           Transition(0, '_eps', 1),
                           Transition(1, '_eps', 2)])
        self.assertEqual(nf.e_closure(0), {0, 1, 2})
