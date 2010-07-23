#/usr/bin/python3

# test_re_parser.py

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

from regex import *

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
        nf = Nfa('a')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; 1 [shape=doublecircle];'))

    def testCSet(self):
        nf = Nfa('[ab]')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "0" -> "1" [label="b"]; 1 [shape=doublecircle];'))

    def testEmptyCSet(self):
        self.assertRaises(Exception, Nfa, '[]')
        # self.assertEqual(nf.to_dot(),
        #                  digraph_template('"0" -> "1" [label="a"]; "0" -> "1" [label="b"]; 1 [shape=doublecircle];'))

    def testBadCounts1(self):
        self.assertRaises(Exception, Nfa, '{0}')

    def testBadCounts2(self):
        self.assertRaises(Exception, Nfa, '{4,2}')

    def testCSetConcat(self):
        nf = Nfa('[ab][def]')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; ' +
                                          '"0" -> "1" [label="b"]; ' +
                                          '"1" -> "2" [label="d"]; ' +
                                          '"1" -> "2" [label="e"]; ' +
                                          '"1" -> "2" [label="f"]; ' +
                                          '2 [shape=doublecircle];'))
    def testAlt(self):
        nf = Nfa('[ab]|[de]')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "3" [label="&epsilon;"]; ' + 
                                          '"1" -> "2" [label="a"]; ' +
                                          '"1" -> "2" [label="b"]; ' +
                                          '"2" -> "5" [label="&epsilon;"]; ' + 
                                          '"3" -> "4" [label="d"]; ' +
                                          '"3" -> "4" [label="e"]; ' +
                                          '"4" -> "5" [label="&epsilon;"]; ' +
                                          '5 [shape=doublecircle];'))

    def testFromCharParens(self):
        nf = Nfa('(a)')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; 1 [shape=doublecircle];'))

    def testConcatChars(self):
        nf = Nfa('ab')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "1" -> "2" [label="b"]; 2 [shape=doublecircle];'))

    def testConcatCharsParens(self):
        nf = Nfa('(a)(b)')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; "1" -> "2" [label="b"]; 2 [shape=doublecircle];'))


    def testAlt(self):
        nf = Nfa('a|b')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "3" [label="&epsilon;"]; ' + 
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "5" [label="&epsilon;"]; ' + 
                                          '"3" -> "4" [label="b"]; ' +
                                          '"4" -> "5" [label="&epsilon;"]; ' +
                                          '5 [shape=doublecircle];'))

    def testConcatAlt(self):
        nf = Nfa('ab|c')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "4" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; "2" -> "3" [label="b"]; ' +
                                          '"3" -> "6" [label="&epsilon;"]; ' + 
                                          '"4" -> "5" [label="c"]; ' +
                                          '"5" -> "6" [label="&epsilon;"]; ' +
                                          '6 [shape=doublecircle];'))

    def testCount(self):
        nf = Nfa('a{3}')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "3" [label="a"]; ' +
                                          '3 [shape=doublecircle];'))
    def testCountMinMax(self):
        nf = Nfa('a{1,2}')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="a"]; ' +
                                          '"1" -> "2" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '2 [shape=doublecircle];'))
    def testCountZeroMin(self):
        nf = Nfa('a{0,2}')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "2" [label="&epsilon;"]; ' +
                                          '"0" -> "1" [label="a"]; ' +
                                          '"1" -> "2" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '2 [shape=doublecircle];'))

    def testClosure(self):
        nf = Nfa('a*')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "3" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "1" [label="&epsilon;"]; ' + 
                                          '"2" -> "3" [label="&epsilon;"]; ' +
                                          '3 [shape=doublecircle];'))

    def testConcatClosure(self):
        nf = Nfa('(ab)*')
        self.assertEqual(nf.to_dot(),
                         digraph_template('"0" -> "1" [label="&epsilon;"]; ' +
                                          '"0" -> "4" [label="&epsilon;"]; ' +
                                          '"1" -> "2" [label="a"]; ' +
                                          '"2" -> "3" [label="b"]; ' +
                                          '"3" -> "1" [label="&epsilon;"]; ' + 
                                          '"3" -> "4" [label="&epsilon;"]; ' +
                                          '4 [shape=doublecircle];'))

    def testAltClosure(self):
        nf = Nfa('a*|b')
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

    def testEClosure1(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                           Transition(0, '_eps', 1),
                           Transition(1, '_eps', 2)])
        self.assertEqual(nf.e_closure(0), {0, 1, 2})

    def testEClosure2(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                           Transition(0, 'b', 2),
                           Transition(1, 'c', 2)])
        self.assertEqual(nf.e_closure(0), {0})
        self.assertEqual(nf.e_closure(2), {2})

    def testMove(self):
        nf = Nfa()
        nf.addTransitions([Transition(0, 'a', 1),
                           Transition(0, '_eps', 1),
                           Transition(1, '_eps', 2)])

        self.assertEqual(nf.move({0}, 'a'), {1,2})

    def testMatchNfa01(self):
        self.assertTrue(re_match('abc|def', 'abc'))
        self.assertFalse(re_match('abc|def', 'abd'))

    def testMatchNfa02(self):
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abcdef'))
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abccddef'))
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abccdcddef'))
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abccdabcddef'))
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abcababcdabcddef'))

        self.assertFalse(re_match('abc(ab|cd*)*def', 'abcababcdabceddef'))
        self.assertFalse(re_match('abc(ab|cd*)*def', 'abc'))
    
    def testMatchNfa03(self):
        self.assertTrue(re_match('(abc+)+', 'abc'))
        self.assertTrue(re_match('(abc+)+', 'abccc'))
        self.assertTrue(re_match('(abc+)+', 'abcccabcc'))
        self.assertTrue(re_match('(abc+)+', 'abcccabccabc'))

        self.assertFalse(re_match('(abc+)+', 'abcccabccab'))
                        
    def testMatchNfa04(self):
        self.assertTrue(re_match('[a-z]+', 'abcdefg'))

    def testMatchNfa05(self):
        self.assertTrue(re_match('[a-z]+|[0-9]+', 'abcdefg'))
        self.assertTrue(re_match('[:alpha:]+|[:digit:]+', '432'))
        self.assertTrue(re_match('[a-z]+|[0-9]+', '1'))
        self.assertTrue(re_match('[:alnum:]+|[0-9]+', 'a'))
        
        self.assertFalse(re_match('[a-z]+|[0-9]+', '(432)'))

    def testMatchNfa06(self):
        self.assertTrue(re_match('[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]', '720-303-1234'))
        self.assertFalse(re_match('[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]', '720-3031-1234'))

    def testMatchNfa07(self):
        self.assertTrue(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '720-303-1234'))
        self.assertTrue(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '720-303-123-1234'))
        self.assertTrue(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '720-1234'))
        self.assertFalse(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '1234'))

    def testMatchNfa08(self):
        self.assertTrue(re_match('(abc*)+', 'ab'))

    def testMatchNfa09(self):
        self.assertTrue(re_match('(abc){3}', 'abcabcabc'))
        self.assertFalse(re_match('(abc){3}', 'abcabc'))
        self.assertFalse(re_match('(abc){3}', 'abcabcabcabc'))

    def testMatchNfa10(self):
        self.assertFalse(re_match('a{2,3}', 'a'))
        self.assertTrue(re_match('a{2,3}', 'aa'))
        self.assertTrue(re_match('a{2,3}', 'aaa'))
        self.assertFalse(re_match('a{2,3}', 'aaaa'))
        
    def testMatchNfa11(self):
        self.assertTrue(re_match('a{0,3}', ''))
        self.assertTrue(re_match('a{0,3}', 'a'))
        self.assertTrue(re_match('a{0,3}', 'aa'))
        self.assertTrue(re_match('a{0,3}', 'aaa'))
        self.assertFalse(re_match('a{0,3}', 'aaaa'))

    def testMatchNfa12(self):
        self.assertTrue(re_match('([0-9]{3}-){2}[0-9]{4}', '720-303-1234'))

    def testMatchNfa13(self):
        self.assertTrue(re_match('([0-9]{3,4}-?){3}[0-9]', '720-303-1234'))
        self.assertTrue(re_match('([0-9]{3,4}-?){3}', '720-303-1234'))
        self.assertTrue(re_match('([0-9]{3,4}-?){3}', '7203031234'))
        self.assertTrue(re_match('([:digit:]{3,4}-?){3}', '7203031234'))
        self.assertFalse(re_match('([0-9]{3,4}-?){3}', '720303a1234'))

    def testUnicodeMatch(self):
        self.assertTrue(re_match('▰', '▰'))
        self.assertTrue(re_match('▰+▣▰', '▰▰▣▰'))
        self.assertTrue(re_match('([◯-◿])+', '◯◺◯◿◯'))

    def testAlphabet(self):
        nf = Nfa('[:digit:]*')
        self.assertEqual(nf.get_alphabet(), set(str(x) for x in range(10)))

    def testNextState(self):
        nf = Nfa('bob')
        states = []

        nid = nf.state_id(states, {3,4})
        self.assertEqual(nid, 0)

        nid = nf.state_id(states, {4})
        self.assertEqual(nid, 1)

        nid = nf.state_id(states, {1,2,3})
        self.assertEqual(nid, 2)

        self.assertEqual(states, [{3,4}, {4}, {1,2,3}])

    def testDfaMatch01(self):
        df = Dfa('a|b')
        self.assertTrue(df.matches('a'))

    def testMatchDfa01(self):
        self.assertTrue(re_match('abc|def', 'abc', True) )
        self.assertFalse(re_match('abc|def', 'abd', True) )

    def testMatchDfa02(self):
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abcdef', True) )
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abccddef', True) )
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abccdcddef', True) )
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abccdabcddef', True) )
        self.assertTrue(re_match('abc(ab|cd*)*def', 'abcababcdabcddef', True) )

        self.assertFalse(re_match('abc(ab|cd*)*def', 'abcababcdabceddef', True) )
        self.assertFalse(re_match('abc(ab|cd*)*def', 'abc', True) )
    
    def testMatchDfa03(self):
        self.assertTrue(re_match('(abc+)+', 'abc', True) )
        self.assertTrue(re_match('(abc+)+', 'abccc', True) )
        self.assertTrue(re_match('(abc+)+', 'abcccabcc', True) )
        self.assertTrue(re_match('(abc+)+', 'abcccabccabc', True) )

        self.assertFalse(re_match('(abc+)+', 'abcccabccab', True) )
                        
    def testMatchDfa04(self):
        self.assertTrue(re_match('[a-z]+', 'abcdefg', True) )

    def testMatchDfa05(self):
        self.assertTrue(re_match('[a-z]+|[0-9]+', 'abcdefg', True) )
        self.assertTrue(re_match('[:alpha:]+|[:digit:]+', '432', True) )
        self.assertTrue(re_match('[a-z]+|[0-9]+', '1', True) )
        self.assertTrue(re_match('[:alnum:]+|[0-9]+', 'a', True) )
        
        self.assertFalse(re_match('[a-z]+|[0-9]+', '(432)', True) )

    def testMatchDfa06(self):
        self.assertTrue(re_match('[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]', '720-303-1234', True) )
        self.assertFalse(re_match('[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]', '720-3031-1234', True) )

    def testMatchDfa07(self):
        self.assertTrue(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '720-303-1234', True) )
        self.assertTrue(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '720-303-123-1234', True) )
        self.assertTrue(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '720-1234', True) )
        self.assertFalse(re_match('([0-9][0-9][0-9]-)+[0-9][0-9][0-9][0-9]', '1234', True) )

    def testMatchDfa08(self):
        self.assertTrue(re_match('(abc*)+', 'ab', True) )

    def testMatchDfa09(self):
        self.assertTrue(re_match('(abc){3}', 'abcabcabc', True) )
        self.assertFalse(re_match('(abc){3}', 'abcabc', True) )
        self.assertFalse(re_match('(abc){3}', 'abcabcabcabc', True) )

    def testMatchDfa10(self):
        self.assertFalse(re_match('a{2,3}', 'a', True) )
        self.assertTrue(re_match('a{2,3}', 'aa', True) )
        self.assertTrue(re_match('a{2,3}', 'aaa', True) )
        self.assertFalse(re_match('a{2,3}', 'aaaa', True) )
        
    def testMatchDfa11(self):
        self.assertTrue(re_match('a{0,3}', '', True) )
        self.assertTrue(re_match('a{0,3}', 'a', True) )
        self.assertTrue(re_match('a{0,3}', 'aa', True) )
        self.assertTrue(re_match('a{0,3}', 'aaa', True) )
        self.assertFalse(re_match('a{0,3}', 'aaaa', True) )

    def testMatchDfa12(self):
        self.assertTrue(re_match('([0-9]{3}-){2}[0-9]{4}', '720-303-1234', True) )

    def testMatchDfa13(self):
        self.assertTrue(re_match('([0-9]{3,4}-?){3}[0-9]', '720-303-1234', True) )
        self.assertTrue(re_match('([0-9]{3,4}-?){3}', '720-303-1234', True) )
        self.assertTrue(re_match('([0-9]{3,4}-?){3}', '7203031234', True) )
        self.assertTrue(re_match('([:digit:]{3,4}-?){3}', '7203031234', True) )
        self.assertFalse(re_match('([0-9]{3,4}-?){3}', '720303a1234', True) )

    def testUnicodeMatchDfa(self):
        self.assertTrue(re_match('▰', '▰', True) )
        self.assertTrue(re_match('▰+▣▰', '▰▰▣▰', True) )
        self.assertTrue(re_match('([◯-◿])+', '◯◺◯◿◯', True) )

if __name__=='__main__':
    unittest.main()
