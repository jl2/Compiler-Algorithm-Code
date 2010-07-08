-- REParser.hs

-- Copyright (c) 2010, Jeremiah LaRocco jeremiah.larocco@gmail.com

-- Permission to use, copy, modify, and/or distribute this software for any
-- purpose with or without fee is hereby granted, provided that the above
-- copyright notice and this permission notice appear in all copies.

-- THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
-- WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
-- MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
-- ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
-- WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
-- ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
-- OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

-- This module uses Parsec to create a parse tree from a string containing a
-- simple regular expression, such as ([abc]|[def])+((abc)*)

module REParser
where

import Text.ParserCombinators.Parsec
import Text.ParserCombinators.Parsec.Expr

data ParseTree = Char Char 
               | Closure ParseTree
               | Alternation ParseTree ParseTree
               | Concatenation ParseTree ParseTree
               | Empty
                 deriving (Show, Eq)

combineRegex :: ParseTree -> ParseTree -> ParseTree
combineRegex pt Empty = pt
combineRegex left right = Concatenation left right

parseRE :: String -> ParseTree
parseRE re = case (parse regex "" re) of
               Left _ -> Empty
               Right y -> y

regex :: Parser ParseTree
regex = do { x <- regex2; y <- regex; return (combineRegex x y) }
        <|> return Empty
        <?> "Regex"

oneOrMore :: ParseTree -> ParseTree
oneOrMore x = Concatenation x (Closure x)

regex2 :: Parser ParseTree
regex2 = buildExpressionParser retable refactor <?> "regular expression"

retable = [ [ (Postfix (do { string "*"; return Closure }) ),
              (Postfix (do { string "+"; return oneOrMore }) )],
            [ (Infix (do { string "|"; return Alternation }) AssocLeft) ]]

refactor = do { char '('; x <- regex; char ')'; return x; }
           <|> restring
           <?> "simple regular expression"

restring :: Parser ParseTree
restring = do { ds <- many1 (noneOf "[]|*+()"); return (makeConcat ds) }
           <|> charclass
           <?> "restring"

makeCharClass :: String -> ParseTree
makeCharClass (x:[]) = Char x
makeCharClass (x:'-':y:xs) =
    if (y>x)
    then (makeCharClass ([x..y]++xs))
    else (makeCharClass xs)

makeCharClass (x:xs) = Alternation (Char x) (makeCharClass xs)

charclass :: Parser ParseTree
charclass = do { char '['; cs <- many1 (noneOf "]"); char ']'; return (makeCharClass cs)}
            <?> "character class"

makeConcat :: String -> ParseTree
makeConcat ([]) = Empty
makeConcat (x:[]) = Char x
makeConcat (x:xs) = Concatenation (Char x) (makeConcat xs) 
