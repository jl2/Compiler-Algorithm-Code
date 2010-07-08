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

    def testTokens(self):
        self.assertEqual(tokenFor('a'), OTHER)
        self.assertEqual(tokenFor('-'), DASH)

    def testParseChar(self):
        pt = parse('a')
        self.assertEqual(str(pt), 'a')

    def testParseCharSet(self):
        pt = parse('[a-z]')
        self.assertEqual(str(pt), '[{}]'.format(''.join([chr(x) for x in range(ord('a'), ord('z')+1)])))

    def testParseAlt(self):
        pt = parse('a|b')
        self.assertEqual(str(pt), '(a)|(b)')

    def testParseConcat(self):
        pt = parse('ab')
        self.assertEqual(str(pt), 'ab')

    def testParseClosure(self):
        pt = parse('a*')
        self.assertEqual(str(pt), '(a)*')

    def testParseParens(self):
        pt = parse('(a)')
        self.assertEqual(str(pt), 'a')

    def testParseAltCharSet(self):
        pt = parse('[a-d]|c*')
        self.assertEqual(str(pt), '([abcd])|((c)*)')

    def testParseNestedAlt(self):
        pt = parse('(a|b)|(c|d)')
        self.assertEqual(str(pt), '((a)|(b))|((c)|(d))')

    def testParseAltConcat(self):
        pt = parse('ab|cd')
        self.assertEqual(str(pt), '(ab)|(cd)')

    def testParseAltConcat2(self):
        pt = parse('(ab)|(cd)')
        self.assertEqual(str(pt), '(ab)|(cd)')

    def testParseComplicated1(self):
        pt = parse('[a-d][x-z]|(abc|def)')
        self.assertEqual(str(pt), '([abcd][xyz])|((abc)|(def))')

    def testParseComplicated2(self):
        pt = parse('([abc]|[def]*)')
        self.assertEqual(str(pt), '([abc])|(([def])*)')

    def testParseComplicated3(self):
        pt = parse('([abc]|[def]*)|abc')
        self.assertEqual(str(pt), '(([abc])|(([def])*))|(abc)')

    def testParseComplicated4(self):
        pt = parse('([abc]|[def]*)|[a-d]')
        self.assertEqual(str(pt), '(([abc])|(([def])*))|([abcd])')

    def testParseComplicated4(self):
        pt = parse('([abc]|[def]*)|[a-d]*')
        self.assertEqual(str(pt), '(([abc])|(([def])*))|(([abcd])*)')

    def testParseComplicated5(self):
        pt = parse('(([abc]|[def]*)|[a-d]*)+')
        self.assertEqual(str(pt), '(([abc])|(([def])*))|(([abcd])*)((([abc])|(([def])*))|(([abcd])*))*')

    def testParseComplicated6(self):
        pt = parse('a|b|c')
        self.assertEqual(str(pt), '(a)|((b)|(c))')

    def testParseComplicated7(self):
        pt = parse('a|b*|c')
        self.assertEqual(str(pt), '(a)|(((b)*)|(c))')

if __name__=='__main__':
    unittest.main()
