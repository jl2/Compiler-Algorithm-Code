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

from re_parser import *

class TestREParser(unittest.TestCase):

    def testClosureStr(self):
        ac = PTChar('a')
        bc = PTChar('b')
        close = PTClosure(ac)
        self.assertEqual(str(close), '(a)*')

    def testAlternationStr(self):
        ac = PTChar('a')
        bc = PTChar('b')
        alt = PTAlternation(ac, bc)
        self.assertEqual(str(alt), '(a)|(b)')

    def testConcatenationStr(self):
        ac = PTChar('a')
        bc = PTChar('b')
        cat = PTConcatenation(ac, bc)
        self.assertEqual(str(cat), 'ab')

    def testCharClassStr(self):
        abc = PTCharSet('a-c')
        self.assertEqual(str(abc), '[abc]')

    def testCharStr(self):
        ac = PTChar('a')
        self.assertEqual(str(ac), 'a')

    def testParseChar(self):
        self.assertEqual(str(parse('a')), 'a')

    def testParseCharSet(self):
        self.assertEqual(str(parse('[a-z]')), '[{}]'.format(''.join([chr(x) for x in range(ord('a'), ord('z')+1)])))

    def testParseAlt(self):
        self.assertEqual(str(parse('a|b')), '(a)|(b)')

    def testParseConcat(self):
        self.assertEqual(str(parse('ab')), 'ab')

    def testParseClosure(self):
        self.assertEqual(str(parse('a*')), '(a)*')

    def testParseCount(self):
        self.assertEqual(str(parse('(a){3}')), '(a){3}')

    def testParseMinMaxCount(self):
        self.assertEqual(str(parse('a{3,4}')), '(a){3,4}')

    def testParseComma(self):
        self.assertEqual(str(parse('3,4,5')), '3,4,5')

    def testParseParens(self):
        self.assertEqual(str(parse('(a)')), 'a')

    def testParseAltCharSet(self):
        self.assertEqual(str(parse('[a-d]|c*')),
                         '([abcd])|((c)*)')

    def testParseNestedAlt(self):
        self.assertEqual(str(parse('(a|b)|(c|d)')),
                         '((a)|(b))|((c)|(d))')

    def testParseAltConcat(self):
        self.assertEqual(str(parse('ab|cd')), '(ab)|(cd)')

    def testParseAltConcat2(self):
        self.assertEqual(str(parse('(ab)|(cd)')),
                         '(ab)|(cd)')

    def testParseComplicated1(self):
        self.assertEqual(str(parse('[a-d][x-z]|(abc|def)')),
                         '([abcd][xyz])|((abc)|(def))')

    def testParseComplicated10(self):
        self.assertEqual(str(parse('(a-d)(x-z)|(abc|def)')),
                         '(a-dx-z)|((abc)|(def))')

    def testParseComplicated2(self):
        self.assertEqual(str(parse('([abc]|[def]*)')),
                         '([abc])|(([def])*)')

    def testParseComplicated3(self):
        self.assertEqual(str(parse('([abc]|[def]*)|abc')),
                         '(([abc])|(([def])*))|(abc)')

    def testParseComplicated4(self):
        self.assertEqual(str(parse('([abc]|[def]*)|[a-d]')),
                         '(([abc])|(([def])*))|([abcd])')

    def testParseComplicated4(self):
        self.assertEqual(str(parse('([abc]|[def]*)|[a-d]*')),
                         '(([abc])|(([def])*))|(([abcd])*)')

    def testParseComplicated5(self):
        self.assertEqual(str(parse('(([abc]|[def]*)|[a-d]*)+')),
                         '(([abc])|(([def])*))|(([abcd])*)((([abc])|(([def])*))|(([abcd])*))*')

    def testParseComplicated6(self):
        self.assertEqual(str(parse('a|b|c')), '((a)|(b))|(c)')

    def testParseComplicated7(self):
        self.assertEqual(str(parse('a|b*|c')), '((a)|((b)*))|(c)')
    
if __name__=='__main__':
    unittest.main()
