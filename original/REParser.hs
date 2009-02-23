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
makeCharClass (x:'-':y:xs) = if (y>x)
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
