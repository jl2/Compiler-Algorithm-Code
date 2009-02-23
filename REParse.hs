-- This module parses simple regular expressions as described in
-- the book "Compilers: Principles, Techniques, & Tools"
-- The parser supports:
--   a*  closure (0 or more)
--   a+  one or more
--  (a)  sub-expressions in parentheses
--   a|b alternation (a or b)

-- There is currently a bug where ** will throw an error
-- It should be treated as *

module Nfa
    (ParseTree(..), parseRE) 
    where

data ParseTree = Empty
               | Char Char 
               | Closure ParseTree
               | Alternation ParseTree ParseTree
               | Concatenation ParseTree ParseTree
                 deriving (Show, Eq)

parseRE :: String -> ParseTree
parseRE s = parse2 (0, Empty) s

parse2 :: (Int, ParseTree) -> String -> ParseTree
parse2 (n, pt) ('|':xs) =
    Alternation pt (parse2 (n, Empty) xs)
                                                        
--     (Alternation pt (parse2 Empty xs))
parse2 (n, pt) ('*':xs) =
    case pt of
      Empty -> error "Closure over nothing"
      Char l -> (parse2 (n, (Closure pt)) xs)
      Concatenation l r -> (parse2 (n, (Concatenation pt (Closure r))) xs)
      Alternation l r -> (parse2 (n, Closure pt) xs)
      Closure r -> (parse2 (n, pt) xs)

parse2 (n, pt) ('(':cs) = parse2 (n+1, pt) cs

parse2 (n, pt) (')':cs) =
    if (n==0) then
        error "Mismatched paren"
    else
        (parse2 (n-1, pt) cs)

parse2 (n, pt) (x:xs) =
    case pt of
      Empty -> parse2 (n, (Char x)) xs
      Alternation l r -> parse2 (n, Alternation l (Concatenation r (Char x))) xs
      _ -> parse2 (n, Concatenation pt (Char x)) xs

parse2 (n, pt) _ = pt
